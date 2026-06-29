"""
=============================================
融合检索节点
=============================================

并行执行三路检索并融合分数：
1. 向量检索（语义相似）
2. 关键词检索（精确匹配）
3. QA 匹配（问答对）

使用 Reciprocal Rank Fusion (RRF) 融合分数
"""

from typing import Dict, Any, List, Tuple
from ..state import CustomerServiceState, QuerySource


def fusion_retrieve(state: CustomerServiceState) -> CustomerServiceState:
    """
    融合检索节点

    并行执行三路检索并融合分数：
    1. 向量检索 - ChromaDB embedding 相似度
    2. 关键词检索 - chunk 内容关键词精确匹配
    3. QA 匹配 - 问答对检索

    使用 RRF (Reciprocal Rank Fusion) 融合：
    score(chunk) = Σ α_i / (k + rank_i(chunk))

    Returns:
        更新 state：retrieved_chunks, source, reference_doc_id
    """
    bot_id = state["bot_id"]
    user_input = state["user_input"]
    rag_top_k = state.get("rag_top_k", 10)  # 融合阶段取更多候选
    rag_rerank_top_k = state.get("rag_rerank_top_k", 5)

    if rag_rerank_top_k > rag_top_k:
        rag_rerank_top_k = rag_top_k

    try:
        from ...db.chroma import TenantChromaManager
        from .cross_encoder_rerank import rerank, is_reranker_available

        chroma_manager = TenantChromaManager(bot_id)

        # 1. 三路并行检索
        vector_results = _search_vector(chroma_manager, user_input, rag_top_k)
        keyword_results = _search_keyword(chroma_manager, user_input, rag_top_k)
        qa_results = _search_qa(chroma_manager, user_input, rag_top_k)

        print(f"[Fusion] Vector: {len(vector_results)}, Keyword: {len(keyword_results)}, QA: {len(qa_results)}")

        # 2. RRF 融合
        fused = _reciprocal_rank_fusion(
            [vector_results, keyword_results, qa_results],
            weights=[0.4, 0.4, 0.2],  # 向量 40%, 关键词 40%, QA 20%
            k=60
        )

        print(f"[Fusion] After RRF: {len(fused)} candidates")

        # 打印融合结果
        for i, item in enumerate(fused[:5]):
            print(f"[Fusion] Rank {i}: {item.get('chunk_id', 'N/A')}, score={item.get('fused_score', 0):.4f}, preview={item.get('content', '')[:40]}...")

        # 3. Rerank 精排
        if not fused:
            return {
                "retrieved_chunks": [],
                "source": QuerySource.FALLBACK
            }

        try:
            if is_reranker_available():
                print(f"[Fusion] Reranking {len(fused)} -> {rag_rerank_top_k}")
                reranked = rerank(user_input, fused, top_k=rag_rerank_top_k)

                doc_ids = set(doc['document_id'] for doc in reranked if doc.get('document_id'))

                return {
                    "retrieved_chunks": reranked,
                    "reference_doc_id": list(doc_ids)[0] if doc_ids else None,
                    "source": QuerySource.RAG
                }
        except Exception as e:
            print(f"[Fusion] Rerank failed: {e}")

        # Fallback: 返回融合后的前 N 个
        fallback_chunks = fused[:rag_rerank_top_k]
        doc_ids = set(doc['document_id'] for doc in fallback_chunks if doc.get('document_id'))

        return {
            "retrieved_chunks": fallback_chunks,
            "reference_doc_id": list(doc_ids)[0] if doc_ids else None,
            "source": QuerySource.RAG
        }

    except Exception as e:
        print(f"Fusion retrieve error: {e}")
        import traceback
        traceback.print_exc()

    return {
        "retrieved_chunks": [],
        "source": QuerySource.FALLBACK
    }


def _search_vector(chroma_manager, query: str, top_k: int) -> List[Dict[str, Any]]:
    """向量检索"""
    try:
        results = chroma_manager.search_kb(query=query, top_k=top_k)

        candidates = []
        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                candidates.append({
                    "chunk_id": results["ids"][0][i],
                    "content": doc,
                    "document_id": metadata.get("document_id"),
                    "section_title": metadata.get("section_title", ""),
                    "vector_rank": i + 1,
                    "vector_score": 1 - results["distances"][0][i] if results.get("distances") else 0.0
                })

        return candidates
    except Exception as e:
        print(f"[Fusion] Vector search error: {e}")
        return []


def _search_keyword(chroma_manager, query: str, top_k: int) -> List[Dict[str, Any]]:
    """关键词检索 - 提取查询关键词并匹配 chunk 内容"""
    try:
        # 提取查询中的关键实体
        keywords = _extract_keywords(query)
        print(f"[Fusion] Extracted keywords: {keywords}")

        # 获取所有 chunks 并计算关键词匹配得分
        kb_collection = chroma_manager._get_kb_collection()
        all_chunks = kb_collection.get(include=["documents", "metadatas"])

        scored_chunks = []
        for i, content in enumerate(all_chunks.get("documents", [])):
            if not content:
                continue

            metadata = all_chunks["metadatas"][i]
            chunk_id = all_chunks["ids"][i]

            # 计算关键词匹配得分
            keyword_score = _calculate_keyword_score(query, content, keywords)

            if keyword_score > 0:
                scored_chunks.append({
                    "chunk_id": chunk_id,
                    "content": content,
                    "document_id": metadata.get("document_id"),
                    "section_title": metadata.get("section_title", ""),
                    "keyword_rank": 0,  # 稍后排序后填入
                    "keyword_score": keyword_score
                })

        # 按关键词得分排序
        scored_chunks.sort(key=lambda x: x["keyword_score"], reverse=True)

        # 填入排名
        for i, chunk in enumerate(scored_chunks):
            chunk["keyword_rank"] = i + 1

        return scored_chunks[:top_k]

    except Exception as e:
        print(f"[Fusion] Keyword search error: {e}")
        return []


def _search_qa(chroma_manager, query: str, top_k: int) -> List[Dict[str, Any]]:
    """QA 检索 - 返回匹配的 QA 对答案作为候选"""
    try:
        qa_result = chroma_manager.search_qa(query=query, top_k=1, threshold=0.5)

        if qa_result:
            # QA 命中，将答案内容作为候选 chunk
            return [{
                "chunk_id": f"qa_{qa_result['id']}",
                "content": f"问题：{qa_result['question']}\n答案：{qa_result['answer']}",
                "document_id": None,
                "section_title": "QA",
                "qa_rank": 1,
                "qa_score": qa_result.get("similarity", 0),
                "qa_answer": qa_result.get("answer", "")
            }]

        return []
    except Exception as e:
        print(f"[Fusion] QA search error: {e}")
        return []


def _extract_keywords(query: str) -> List[str]:
    """从查询中提取关键实体"""
    import re

    keywords = []

    # 提取《...》标题
    title_matches = re.findall(r'《([^》]+)》', query)
    keywords.extend(title_matches)

    # 提取"作者"、"谁"等关键词
    if '作者' in query or '谁写的' in query:
        keywords.append('作者')
        keywords.append('是谁')

    # 提取常见实体词
    entity_pattern = r'([^\s]{2,5})(作者|是谁|写的|创作)'
    entity_matches = re.findall(entity_pattern, query)
    for match in entity_matches:
        keywords.append(match[0])

    return keywords


def _calculate_keyword_score(query: str, content: str, keywords: List[str]) -> float:
    """计算关键词匹配得分"""
    if not keywords:
        return 0.0

    content_lower = content.lower()
    query_lower = query.lower()

    score = 0.0

    for keyword in keywords:
        # 计算在内容和查询中的出现次数
        content_count = content_lower.count(keyword.lower())
        query_count = query_lower.count(keyword.lower())

        if content_count > 0:
            # 匹配得分 = 匹配次数 * 关键词重要性
            # 标题匹配权重更高
            if '《' + keyword + '》' in content or f'《{keyword}》' in content:
                score += content_count * 3.0  # 标题权重
            elif keyword in content:
                score += content_count * 1.0

    return score


def _reciprocal_rank_fusion(
    result_lists: List[List[Dict[str, Any]]],
    weights: List[float] = None,
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Reciprocal Rank Fusion (RRF) 融合多路检索结果

    score(chunk) = Σ α_i / (k + rank_i(chunk))

    Args:
        result_lists: 多路检索结果列表，每路是按排名排序的 chunk 列表
        weights: 各路权重 [vector_weight, keyword_weight, qa_weight]
        k: 折扣参数，越大越平滑

    Returns:
        融合后的 chunk 列表，按融合分数排序
    """
    if weights is None:
        weights = [1.0] * len(result_lists)

    # 收集所有 chunk_id -> chunk 信息的映射
    chunk_map: Dict[str, Dict[str, Any]] = {}
    chunk_scores: Dict[str, float] = {}

    for result_list in result_lists:
        for chunk in result_list:
            chunk_id = chunk.get("chunk_id")
            if not chunk_id:
                continue

            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = chunk.copy()
                chunk_map[chunk_id]["fused_score"] = 0.0
                chunk_scores[chunk_id] = 0.0

    # 计算 RRF 分数
    for i, result_list in enumerate(result_lists):
        weight = weights[i] if i < len(weights) else 1.0

        for rank, chunk in enumerate(result_list):
            chunk_id = chunk.get("chunk_id")
            if not chunk_id or chunk_id not in chunk_scores:
                continue

            # RRF 公式: weight / (k + rank)
            rrf_score = weight / (k + rank + 1)
            chunk_scores[chunk_id] += rrf_score

    # 更新所有 chunk 的融合分数
    for chunk_id, score in chunk_scores.items():
        if chunk_id in chunk_map:
            chunk_map[chunk_id]["fused_score"] = score

    # 按融合分数排序
    fused_results = sorted(
        chunk_map.values(),
        key=lambda x: x.get("fused_score", 0),
        reverse=True
    )

    return fused_results

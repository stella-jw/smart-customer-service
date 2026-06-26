"""
=============================================
RAG检索节点
=============================================
"""

from typing import Dict, Any
from ..state import CustomerServiceState, QuerySource


def rag_retrieve(state: CustomerServiceState) -> CustomerServiceState:
    """
    RAG检索节点

    1. 对用户问题进行向量化
    2. 在 ChromaDB kb_chunks 集合中检索 top_k 个相关片段
    3. 如果 Reranker 可用，执行精排返回 rag_rerank_top_k 个结果
    4. 否则直接返回向量搜索结果
    """
    bot_id = state["bot_id"]
    user_input = state["user_input"]
    rag_top_k = state.get("rag_top_k", 5)
    rag_rerank_top_k = state.get("rag_rerank_top_k", 5)

    # 约束：rag_rerank_top_k 不能超过 rag_top_k
    if rag_rerank_top_k > rag_top_k:
        rag_rerank_top_k = rag_top_k

    try:
        from ...db.chroma import TenantChromaManager
        from .cross_encoder_rerank import rerank, is_reranker_available

        chroma_manager = TenantChromaManager(bot_id)

        # 使用 rag_top_k 进行向量搜索（获取更多候选）
        results = chroma_manager.search_kb(
            query=user_input,
            top_k=rag_top_k
        )

        # 构建候选文档列表
        candidates = []
        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                candidates.append({
                    "content": doc,
                    "document_id": metadata.get("document_id"),
                    "title": metadata.get("title", ""),
                    "section": metadata.get("section", ""),
                    "score": results["distances"][0][i] if results.get("distances") else 1.0
                })

        if not candidates:
            return {
                "retrieved_chunks": [],
                "reference_doc_id": None,
                "source": QuerySource.FALLBACK
            }

        # 尝试使用 Reranker 精排
        try:
            if is_reranker_available():
                print(f"[RAG] 使用 Reranker 精排: {len(candidates)} -> {rag_rerank_top_k}")
                reranked = rerank(user_input, candidates, top_k=rag_rerank_top_k)

                # 提取 doc_ids
                doc_ids = set(doc['document_id'] for doc in reranked if doc.get('document_id'))

                return {
                    "retrieved_chunks": reranked,
                    "reference_doc_id": list(doc_ids)[0] if doc_ids else None,
                    "source": QuerySource.RAG
                }
            else:
                raise Exception("Reranker 不可用")
        except Exception as rerank_error:
            # Reranker 不可用或有错误，执行 fallback
            print(f"[RAG] Reranker 不可用，执行 fallback: {rerank_error}")

            # 直接返回向量搜索的前 rag_rerank_top_k 个结果
            fallback_chunks = candidates[:rag_rerank_top_k]
            doc_ids = set(doc['document_id'] for doc in fallback_chunks if doc.get('document_id'))

            return {
                "retrieved_chunks": fallback_chunks,
                "reference_doc_id": list(doc_ids)[0] if doc_ids else None,
                "source": QuerySource.RAG
            }

    except Exception as e:
        print(f"RAG retrieve error: {e}")

    return {
        "retrieved_chunks": [],
        "reference_doc_id": None,
        "source": QuerySource.FALLBACK
    }

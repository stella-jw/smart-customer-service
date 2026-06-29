"""
=============================================
SiliconFlow Rerank API 模块
=============================================

使用 SiliconFlow Rerank API 对检索结果进行精排
"""

import os
from typing import List, Dict, Any

# 全局 API 客户端缓存
_api_error = None


class RerankerError(Exception):
    """Reranker 相关错误"""
    pass


def is_reranker_available() -> bool:
    """检查 SiliconFlow Rerank API 是否可用"""
    global _api_error

    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        _api_error = "SILICONFLOW_API_KEY 环境变量未设置"
        return False

    if _api_error and "未设置" in _api_error:
        return False

    return True


def rerank(query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    对候选文档进行 SiliconFlow Rerank 精排

    Args:
        query: 用户查询
        candidates: 候选文档列表，每个文档包含 'content' 字段
        top_k: 返回的最高相关性文档数量

    Returns:
        精排后的文档列表，按相关性分数从高到低排序

    Raises:
        RerankerError: API 不可用或请求失败
    """
    if not candidates:
        return []

    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        raise RerankerError("SILICONFLOW_API_KEY 环境变量未设置，请配置 SiliconFlow API Key")

    try:
        import requests

        documents = [doc['content'] for doc in candidates]

        response = requests.post(
            "https://api.siliconflow.cn/v1/rerank",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "BAAI/bge-reranker-v2-m3",
                "query": query,
                "documents": documents,
                "top_n": top_k
            },
            timeout=30
        )

        if response.status_code != 200:
            error_msg = f"API 请求失败: {response.status_code} - {response.text}"
            print(f"[Reranker] 错误: {error_msg}")
            raise RerankerError(error_msg)

        result = response.json()

        # 解析结果，保持原始顺序
        results = []
        for item in result.get("results", []):
            original_idx = item["index"]
            original_doc = candidates[original_idx].copy()
            original_doc['rerank_score'] = item["relevance_score"]
            results.append(original_doc)

        # 按 rerank_score 降序排列
        results.sort(key=lambda x: x['rerank_score'], reverse=True)

        print(f"[Reranker] SiliconFlow 精排完成: {len(candidates)} -> {len(results)}")
        for i, r in enumerate(results):
            print(f"[Reranker DEBUG] Rank {i}: score={r['rerank_score']:.4f}, content_preview={r.get('content', '')[:60]}...")
        return results

    except RerankerError:
        raise
    except Exception as e:
        print(f"[Reranker] SiliconFlow API 调用失败: {e}")
        raise RerankerError(f"精排失败: {str(e)}")


def reset_reranker_cache():
    """重置缓存（用于测试或重新加载）"""
    global _api_error
    _api_error = None
    print("[Reranker] API 错误状态已重置")

"""
=============================================
QA匹配节点
=============================================
"""

from typing import Dict, Any
from ..state import CustomerServiceState, QuerySource


def qa_match(state: CustomerServiceState) -> CustomerServiceState:
    """
    QA对匹配节点

    1. 在 ChromaDB qa_embeddings 集合中检索
    2. 计算相似度分数
    3. 返回最高匹配的 QA 对
    """
    bot_id = state["bot_id"]
    user_input = state["user_input"]
    threshold = state["bot_config"].get("qa_match_threshold", 0.85)

    try:
        from ...db.chroma import TenantChromaManager

        chroma_manager = TenantChromaManager(bot_id)
        match_result = chroma_manager.search_qa(
            query=user_input,
            top_k=1,
            threshold=threshold
        )

        if match_result:
            print(f"[DEBUG qa_match] FOUND match: {match_result['answer'][:50]}...")
            return {
                "matched_qa_id": match_result["id"],
                "matched_qa_question": match_result["question"],
                "matched_qa_answer": match_result["answer"],
                "qa_match_score": match_result["similarity"],
                "source": QuerySource.QA,
                "reference_qa_id": match_result["id"]
            }
        else:
            print("[DEBUG qa_match] No match found")

    except Exception as e:
        print(f"QA match error: {e}")

    return {
        "matched_qa_id": None,
        "matched_qa_question": None,
        "matched_qa_answer": None,
        "qa_match_score": 0.0,
        "source": QuerySource.FALLBACK,
        "reference_qa_id": None
    }

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
    3. 返回检索结果和引用文档信息
    """
    bot_id = state["bot_id"]
    user_input = state["user_input"]
    top_k = state.get("rag_top_k", 5)

    try:
        from ...db.chroma import TenantChromaManager

        chroma_manager = TenantChromaManager(bot_id)
        results = chroma_manager.search_kb(
            query=user_input,
            top_k=top_k
        )

        chunks = []
        doc_ids = set()

        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                chunks.append({
                    "content": doc,
                    "document_id": metadata.get("document_id"),
                    "title": metadata.get("title", ""),
                    "section": metadata.get("section", ""),
                    "score": results["distances"][0][i] if results.get("distances") else 1.0
                })
                doc_ids.add(metadata.get("document_id"))

        if chunks:
            return {
                "retrieved_chunks": chunks,
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

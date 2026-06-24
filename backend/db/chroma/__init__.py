"""
=============================================
ChromaDB 多租户管理器模块
=============================================
"""

from .manager import (
    get_kb_collection_name,
    get_qa_collection_name,
    get_chroma_client,
    TenantChromaManager,
    GlobalChromaManager,
    create_chunk_id,
    create_qa_id,
    MiniMaxEmbeddingFunction
)

__all__ = [
    "get_kb_collection_name",
    "get_qa_collection_name",
    "get_chroma_client",
    "TenantChromaManager",
    "GlobalChromaManager",
    "create_chunk_id",
    "create_qa_id",
    "MiniMaxEmbeddingFunction"
]

"""
=============================================
ChromaDB 多Collection管理器
=============================================
支持多租户隔离，每个Bot独立的Collection
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import chromadb
from chromadb.config import Settings

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import config


# =============================================
# Collection 命名规范
# =============================================

COLLECTION_PREFIX = {
    "kb": "kb_chunks_{bot_id}",      # 知识库文档分块
    "qa": "qa_embeddings_{bot_id}"   # QA问题嵌入
}


def get_kb_collection_name(bot_id: str) -> str:
    """获取知识库Collection名称"""
    return COLLECTION_PREFIX["kb"].format(bot_id=bot_id)


def get_qa_collection_name(bot_id: str) -> str:
    """获取QA嵌入Collection名称"""
    return COLLECTION_PREFIX["qa"].format(bot_id=bot_id)


# =============================================
# MiniMax Embedding Function
# =============================================

class MiniMaxEmbeddingFunction:
    """MiniMax嵌入函数"""

    def __init__(self):
        self.model = config.MINIMAX_EMBEDDING_MODEL
        self.dimension = config.EMBEDDING_DIMENSION

    def __call__(self, input: List[str]) -> List[List[float]]:
        """生成嵌入向量 (兼容 ChromaDB 0.4.16+ 接口)"""
        import requests

        headers = {
            "Authorization": f"Bearer {config.MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }

        embeddings = []
        for text in input:
            payload = {
                "model": self.model,
                "texts": [text]
            }

            try:
                response = requests.post(
                    f"{config.MINIMAX_EMBEDDING_URL}/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                embeddings.append(result["data"][0]["embedding"])
            except Exception as e:
                print(f"Embedding error: {e}")
                # 返回零向量作为fallback
                embeddings.append([0.0] * self.dimension)

        return embeddings

    def name(self) -> str:
        """返回嵌入函数名称 (ChromaDB 0.4.16+ 接口要求)"""
        return "minimax-embedding"


# =============================================
# ChromaDB Client
# =============================================

def get_chroma_client():
    """获取ChromaDB客户端"""
    # 确保目录存在
    os.makedirs(config.CHROMA_DB_PATH, exist_ok=True)

    return chromadb.PersistentClient(
        path=config.CHROMA_DB_PATH
    )


# =============================================
# 多租户Collection管理器
# =============================================

class TenantChromaManager:
    """
    多租户ChromaDB管理器

    每个Bot有独立的Collection：
    - kb_chunks_{bot_id}: 知识库文档分块
    - qa_embeddings_{bot_id}: QA问题嵌入
    """

    def __init__(self, bot_id: str):
        self.bot_id = bot_id
        self.client = get_chroma_client()
        self.embedding_function = MiniMaxEmbeddingFunction()

        # 初始化Collection
        self._init_collections()

    def _init_collections(self):
        """初始化当前Bot的Collection"""
        # KB Collection
        kb_name = get_kb_collection_name(self.bot_id)
        try:
            self.client.get_collection(kb_name)
        except Exception:
            self.client.create_collection(
                name=kb_name,
                embedding_function=self.embedding_function,
                metadata={"bot_id": self.bot_id, "type": "knowledge_base"}
            )

        # QA Collection
        qa_name = get_qa_collection_name(self.bot_id)
        try:
            self.client.get_collection(qa_name)
        except Exception:
            self.client.create_collection(
                name=qa_name,
                embedding_function=self.embedding_function,
                metadata={"bot_id": self.bot_id, "type": "qa_embeddings"}
            )

    def _get_kb_collection(self):
        """获取KB Collection"""
        return self.client.get_collection(get_kb_collection_name(self.bot_id))

    def _get_qa_collection(self):
        """获取QA Collection"""
        return self.client.get_collection(get_qa_collection_name(self.bot_id))

    # =============================================
    # 文档分块操作 (KB)
    # =============================================

    def add_kb_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        添加文档分块

        Args:
            chunks: [{"id": str, "content": str, "metadata": dict}, ...]
        """
        collection = self._get_kb_collection()

        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        return True

    def search_kb(self, query: str, top_k: int = 5, where: Dict = None) -> Dict:
        """
        搜索知识库

        Returns:
            {"ids": [...], "documents": [...], "metadatas": [...], "distances": [...]}
        """
        collection = self._get_kb_collection()

        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where
        )

        return results

    def delete_kb_chunks(self, document_id: str) -> bool:
        """删除某个文档的所有分块"""
        collection = self._get_kb_collection()

        # 获取该文档的所有分块ID
        try:
            results = collection.get(where={"document_id": document_id})
            if results["ids"]:
                collection.delete(ids=results["ids"])
        except Exception as e:
            print(f"Delete KB chunks error: {e}")

        return True

    def get_kb_chunk_count(self) -> int:
        """获取KB分块总数"""
        collection = self._get_kb_collection()
        return collection.count()

    # =============================================
    # QA嵌入操作
    # =============================================

    def add_qa_embeddings(self, qa_pairs: List[Dict[str, Any]]) -> bool:
        """
        添加QA对嵌入

        Args:
            qa_pairs: [{"id": str, "question": str, "answer": str, "metadata": dict}, ...]
        """
        collection = self._get_qa_collection()

        ids = [qa["id"] for qa in qa_pairs]
        documents = [qa["question"] for qa in qa_pairs]
        metadatas = [qa["metadata"] for qa in qa_pairs]

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        return True

    def search_qa(self, query: str, top_k: int = 5, threshold: float = 0.85) -> Optional[Dict]:
        """
        搜索QA对

        Args:
            query: 用户问题
            top_k: 返回数量
            threshold: 相似度阈值

        Returns:
            最高匹配的QA对，如果没有达到阈值返回None
        """
        collection = self._get_qa_collection()

        print(f"[DEBUG ChromaDB search_qa] collection count: {collection.count()}")

        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )

        print(f"[DEBUG ChromaDB search_qa] raw results: {results}")

        if not results["documents"] or not results["documents"][0]:
            return None

        # 检查最高分是否达到阈值
        # ChromaDB返回的是distance，转换为similarity
        if not results.get("distances") or not results["distances"][0]:
            print("[DEBUG ChromaDB search_qa] No distances returned")
            return None

        distance = results["distances"][0][0]
        similarity = 1 - distance

        if similarity >= threshold:
            return {
                "id": results["metadatas"][0][0].get("qa_id"),
                "question": results["metadatas"][0][0].get("question"),
                "answer": results["metadatas"][0][0].get("answer"),
                "similarity": similarity,
                "keywords": results["metadatas"][0][0].get("keywords"),
                "category": results["metadatas"][0][0].get("category")
            }

        return None

    def delete_qa_embedding(self, qa_id: str) -> bool:
        """删除QA嵌入"""
        collection = self._get_qa_collection()

        try:
            collection.delete(ids=[f"qa_{qa_id}"])
        except Exception as e:
            print(f"Delete QA embedding error: {e}")

        return True

    def get_qa_embedding_count(self) -> int:
        """获取QA嵌入总数"""
        collection = self._get_qa_collection()
        return collection.count()

    # =============================================
    # 批量操作
    # =============================================

    def rebuild_kb_collection(self) -> bool:
        """重建KB Collection（清空并重建）"""
        kb_name = get_kb_collection_name(self.bot_id)
        try:
            self.client.delete_collection(kb_name)
        except Exception:
            pass

        self.client.create_collection(
            name=kb_name,
            embedding_function=self.embedding_function,
            metadata={"bot_id": self.bot_id, "type": "knowledge_base"}
        )
        return True

    def rebuild_qa_collection(self) -> bool:
        """重建QA Collection（清空并重建）"""
        qa_name = get_qa_collection_name(self.bot_id)
        try:
            self.client.delete_collection(qa_name)
        except Exception:
            pass

        self.client.create_collection(
            name=qa_name,
            embedding_function=self.embedding_function,
            metadata={"bot_id": self.bot_id, "type": "qa_embeddings"}
        )
        return True


# =============================================
# 全局Collection管理（跨Bot）
# =============================================

class GlobalChromaManager:
    """全局ChromaDB管理器，用于清理和数据统计"""

    def __init__(self):
        self.client = get_chroma_client()

    def delete_bot_collections(self, bot_id: str) -> bool:
        """删除某个Bot的所有Collection"""
        kb_name = get_kb_collection_name(bot_id)
        qa_name = get_qa_collection_name(bot_id)

        for name in [kb_name, qa_name]:
            try:
                self.client.delete_collection(name)
            except Exception:
                pass

        return True

    def get_all_collections(self) -> List[str]:
        """获取所有Collection名称"""
        return [col.name for col in self.client.list_collections()]

    def get_collection_stats(self) -> Dict[str, int]:
        """获取所有Collection的统计"""
        stats = {}
        for col in self.client.list_collections():
            try:
                stats[col.name] = col.count()
            except Exception:
                stats[col.name] = 0
        return stats


# =============================================
# 工具函数
# =============================================

def create_chunk_id(document_id: str, chunk_index: int) -> str:
    """生成chunk ID"""
    return f"chunk_{document_id}_{chunk_index}"


def create_qa_id(qa_id: str) -> str:
    """生成QA嵌入ID"""
    return f"qa_{qa_id}"

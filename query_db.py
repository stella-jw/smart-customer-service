"""
查询 ChromaDB 中的数据
直接运行: python query_db.py

用于查询 smart-customer-service 的知识库内容
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.db.chroma.manager import TenantChromaManager, get_chroma_client
from backend.db.sqlite.crud import get_db_session, get_bot_qa_pairs


def list_all_collections():
    """列出所有 Collection"""
    client = get_chroma_client()
    collections = client.list_collections()
    print("=" * 60)
    print("所有 Collection")
    print("=" * 60)
    for col in collections:
        print(f"  - {col.name}")
    print()


def query_knowledge_base(bot_id: str):
    """查询指定机器人的知识库"""
    print("=" * 60)
    print(f"知识库内容 (bot_id: {bot_id})")
    print("=" * 60)

    manager = TenantChromaManager(bot_id)

    # 获取 KB Collection 并查询所有分块
    collection = manager._get_kb_collection()
    results = collection.get()

    print(f"\n共 {len(results['documents'])} 个分块\n")

    for i, doc in enumerate(results['documents']):
        meta = results['metadatas'][i]
        print(f"【分块 {i+1}】")
        print(f"  文档ID: {meta.get('document_id', 'N/A')}")
        print(f"  块索引: {meta.get('chunk_index', 'N/A')}")
        print(f"  内容: {doc[:200]}..." if len(doc) > 200 else f"  内容: {doc}")
        print()


def semantic_search(bot_id: str, query: str, top_k: int = 5):
    """语义检索知识库"""
    print("=" * 60)
    print(f"语义检索:「{query}」")
    print("=" * 60)

    manager = TenantChromaManager(bot_id)
    results = manager.search_kb(query, top_k=top_k)

    if not results or not results.get('documents') or not results['documents'][0]:
        print("  (无结果)")
        return

    print(f"\n找到 {len(results['documents'][0])} 条相关结果:\n")
    for i, doc in enumerate(results['documents'][0]):
        distance = results['distances'][0][i] if results.get('distances') else 0
        similarity = 1 - distance
        meta = results['metadatas'][0][i]
        print(f"【结果 {i+1}】 相似度: {similarity:.4f}")
        print(f"  文档ID: {meta.get('document_id', 'N/A')}")
        print(f"  内容: {doc[:200]}..." if len(doc) > 200 else f"  内容: {doc}")
        print()


def query_qa_pairs(bot_id: str):
    """查询指定机器人的 QA 对"""
    print("=" * 60)
    print(f"QA 问答对 (bot_id: {bot_id})")
    print("=" * 60)

    # 1. 查询 SQLite 中的 QA 对
    print("\n【SQLite 数据库】")
    with get_db_session() as db:
        qa_pairs = get_bot_qa_pairs(db, bot_id, only_active=False)
        print(f"\n共 {len(qa_pairs)} 个 QA 对\n")
        for qa in qa_pairs:
            print(f"【QA {qa.id}】")
            print(f"  问题: {qa.question}")
            print(f"  答案: {qa.answer[:200]}..." if len(qa.answer) > 200 else f"  答案: {qa.answer}")
            print(f"  关键词: {qa.keywords}")
            print(f"  分类: {qa.category}")
            print(f"  激活: {qa.is_active}")
            print()

    # 2. 查询 ChromaDB 中的 QA 嵌入
    print("\n【ChromaDB 向量库】")
    manager = TenantChromaManager(bot_id)
    collection = manager._get_qa_collection()
    results = collection.get()

    print(f"\n共 {len(results['documents'])} 个 QA 嵌入\n")

    if results['documents']:
        for i, doc in enumerate(results['documents']):
            meta = results['metadatas'][i]
            print(f"【QA 嵌入 {i+1}】")
            print(f"  问题: {meta.get('question', 'N/A')}")
            print(f"  答案: {doc[:200]}..." if len(doc) > 200 else f"  答案: {doc}")
            print()
    else:
        print("  (ChromaDB 中没有 QA 嵌入数据)")
        print("  提示: QA 对已存入 SQLite，但尚未索引到向量库")


def main():
    # 配置
    BOT_ID = "c72c47d8-6787-43e2-b9d5-f317d2c06ec3"  # 替换为实际的 bot_id

    # 1. 列出所有 Collection
    list_all_collections()

    # 2. 查询知识库内容
    query_knowledge_base(BOT_ID)

    # 3. 语义检索测试
    semantic_search(BOT_ID, "所见", top_k=6)

    # 4. 查询 QA 对
    query_qa_pairs(BOT_ID)


if __name__ == "__main__":
    main()

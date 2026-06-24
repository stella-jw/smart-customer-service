"""
查看文档处理进度
直接运行: python check_progress.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.db.chroma.manager import TenantChromaManager
from backend.db.sqlite.crud import get_db_session, get_document


def check_document_progress(bot_id: str, document_id: str = None):
    """查看文档处理进度"""

    # 获取该 bot 的分块总数
    manager = TenantChromaManager(bot_id)
    kb_collection = manager._get_kb_collection()

    print("=" * 60)
    print("文档处理进度查询")
    print("=" * 60)

    # 1. 统计已索引的分块数
    if document_id:
        # 查询特定文档的分块
        results = kb_collection.get(where={"document_id": document_id})
        chunk_count = len(results['ids'])
        print(f"\n文档 ID: {document_id}")
        print(f"已索引分块数: {chunk_count}")
    else:
        # 统计该 bot 所有分块
        total_chunks = kb_collection.count()
        print(f"\nBot ID: {bot_id}")
        print(f"知识库总分块数: {total_chunks}")

    # 2. 查看数据库中的文档状态
    print("\n【文档状态】")
    with get_db_session() as db:
        from backend.db.sqlite.crud import get_bot_documents
        docs = get_bot_documents(db, bot_id, limit=10)

        for doc in docs:
            print(f"\n  文档: {doc.title}")
            print(f"  ID: {doc.id}")
            print(f"  状态: {doc.status.value}")
            print(f"  分块数: {doc.chunk_count}")
            print(f"  文件大小: {doc.file_size / 1024 / 1024:.2f} MB")
            if doc.error_message:
                print(f"  错误: {doc.error_message}")


if __name__ == "__main__":
    BOT_ID = "c72c47d8-6787-43e2-b9d5-f317d2c06ec3"
    DOCUMENT_ID = None  # 可指定文档 ID

    check_document_progress(BOT_ID, DOCUMENT_ID)

"""
=============================================
知识库管理 API
=============================================
"""

import os
import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from pydantic import BaseModel

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from ...db.sqlite import (
    create_document, get_document, get_bot_documents,
    update_document, delete_document
)
from ...db.sqlite.crud import get_db_session
from ...db.chroma import TenantChromaManager, create_chunk_id
from ...core.auth import verify_admin_token


router = APIRouter(prefix="/api/admin", tags=["知识库管理"])


# =============================================
# 常量配置
# =============================================

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md', '.html'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
DOCUMENTS_PATH = "./data/documents"


# =============================================
# 请求/响应模型
# =============================================

class DocumentResponse(BaseModel):
    id: str
    bot_id: str
    title: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    created_at: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


# =============================================
# 工具函数
# =============================================

def validate_file(file: UploadFile) -> str:
    """验证文件"""
    # 检查扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {ext}，支持的类型: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 检查文件大小
    if file.size and file.size > MAX_FILE_SIZE:
        actual_size_mb = file.size / 1024 / 1024
        limit_size_mb = MAX_FILE_SIZE / 1024 / 1024
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制！当前文件: {actual_size_mb:.2f}MB，最大支持: {limit_size_mb:.0f}MB，请上传更小的文件"
        )

    return ext


def save_upload_file(file: UploadFile, bot_id: str) -> str:
    """保存上传文件"""
    # 创建目录
    bot_doc_path = os.path.join(DOCUMENTS_PATH, bot_id)
    os.makedirs(bot_doc_path, exist_ok=True)

    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(bot_doc_path, unique_filename)

    # 保存文件
    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)

    return file_path


# =============================================
# 文档处理函数
# =============================================

async def process_document_task(document_id: str, bot_id: str, file_path: str, file_type: str, chunker_type: str = "fixed"):
    """异步文档处理任务"""
    print(f"[DocumentTask] Starting: document_id={document_id}, bot_id={bot_id}, file_path={file_path}, chunker={chunker_type}")
    try:
        from ...db.sqlite.crud import get_db_session
        from ...service.document_parser import DocumentParser
        from ...service.chunker import get_chunker
        from ...db.chroma import TenantChromaManager, create_chunk_id

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise Exception(f"文件不存在: {file_path}")

        # 更新状态为parsing
        print(f"[DocumentTask] Updating status to parsing: {document_id}")
        with get_db_session() as db:
            update_document(db, document_id, status="parsing")

        # 解析文档
        print(f"[DocumentTask] Parsing document: {document_id}")
        parser = DocumentParser.get_parser(file_type)
        text = parser.parse(file_path)
        print(f"[DocumentTask] Parsed text length: {len(text)}")

        # 分块
        print(f"[DocumentTask] Chunking document: {document_id}")
        chunker = get_chunker(chunker_type)
        chunks = chunker.chunk(text, {
            "document_id": document_id,
            "bot_id": bot_id,
            "chunker_type": chunker_type
        })
        print(f"[DocumentTask] Created {len(chunks)} chunks using {chunker_type}")

        # 存储到ChromaDB
        print(f"[DocumentTask] Storing to ChromaDB: {document_id}")
        chroma_manager = TenantChromaManager(bot_id)
        chroma_chunks = [
            {
                "id": create_chunk_id(document_id, i),
                "content": chunk["content"],
                "metadata": {
                    **chunk["metadata"],
                    "chunk_index": i
                }
            }
            for i, chunk in enumerate(chunks)
        ]
        chroma_manager.add_kb_chunks(chroma_chunks)

        # 更新状态为indexed
        print(f"[DocumentTask] Updating status to indexed: {document_id}")
        with get_db_session() as db:
            update_document(db, document_id, status="indexed", chunk_count=len(chunks))

        print(f"[DocumentTask] Completed: {document_id}")

    except Exception as e:
        print(f"[DocumentTask] Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            with get_db_session() as db:
                update_document(db, document_id, status="failed", error_message=str(e))
        except Exception as db_err:
            print(f"[DocumentTask] Failed to update error status: {db_err}")


# =============================================
# API 端点
# =============================================

@router.post("/documents")
async def upload_document(
    bot_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    _: dict = Depends(verify_admin_token)
):
    """
    上传文档到知识库

    支持格式: PDF, DOCX, TXT, MD, HTML
    """
    try:
        # 验证文件
        ext = validate_file(file)

        # 保存文件
        file_path = save_upload_file(file, bot_id)

        # 创建数据库记录
        with get_db_session() as db:
            doc = create_document(
                db=db,
                bot_id=bot_id,
                title=file.filename,
                file_type=ext[1:],  # 去掉点号
                file_path=file_path,
                file_size=file.size or 0
            )
            # 在 session 关闭前提取需要的数据
            doc_id = doc.id
            doc_title = doc.title

        # 异步处理文档
        background_tasks.add_task(
            process_document_task,
            document_id=doc_id,
            bot_id=bot_id,
            file_path=file_path,
            file_type=ext[1:]
        )

        return {
            "document_id": doc_id,
            "title": doc_title,
            "status": "pending",
            "message": "文档上传成功，正在后台处理"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/documents POST 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(bot_id: str, skip: int = 0, limit: int = 100, _: dict = Depends(verify_admin_token)):
    """获取文档列表"""
    try:
        with get_db_session() as db:
            docs = get_bot_documents(db, bot_id, skip=skip, limit=limit)
            # 在 session 关闭前提取所有数据到普通对象
            doc_responses = []
            for doc in docs:
                doc_responses.append(DocumentResponse(
                    id=doc.id,
                    bot_id=doc.bot_id,
                    title=doc.title,
                    file_type=doc.file_type,
                    file_size=doc.file_size or 0,
                    status=doc.status.value,
                    chunk_count=doc.chunk_count,
                    created_at=doc.created_at.isoformat()
                ))
            total = len(doc_responses)
        # session 已关闭，返回已提取的数据
        return DocumentListResponse(documents=doc_responses, total=total)
    except Exception as e:
        print(f"[API] /api/admin/documents GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}")
async def get_document_info(document_id: str, _: dict = Depends(verify_admin_token)):
    """获取文档详情"""
    try:
        with get_db_session() as db:
            doc = get_document(db, document_id)
            if not doc:
                raise HTTPException(status_code=404, detail="文档不存在")
            return {
                "id": doc.id,
                "title": doc.title,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "status": doc.status.value,
                "chunk_count": doc.chunk_count,
                "error_message": doc.error_message,
                "created_at": doc.created_at.isoformat(),
                "updated_at": doc.updated_at.isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/documents/{document_id} GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document_file(document_id: str, _: dict = Depends(verify_admin_token)):
    """删除文档"""
    try:
        with get_db_session() as db:
            doc = get_document(db, document_id)
            if not doc:
                raise HTTPException(status_code=404, detail="文档不存在")

            bot_id = doc.bot_id

            # 删除物理文件
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)

            # 删除ChromaDB中的分块
            try:
                from ...db.chroma import TenantChromaManager
                chroma_manager = TenantChromaManager(bot_id)
                chroma_manager.delete_kb_chunks(document_id)
            except Exception as chroma_err:
                # ChromaDB 可能有内部状态冲突，忽略删除向量库的误差
                print(f"[API] ChromaDB 删除警告: {chroma_err}")

            # 删除数据库记录
            delete_document(db, document_id)

        return {"success": True, "message": "文档已删除"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/documents/{document_id} DELETE 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/{document_id}/reindex")
async def reindex_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    chunker_type: str = "fixed",
    _: dict = Depends(verify_admin_token)
):
    """重新索引文档

    Args:
        chunker_type: 分块策略，可选:
            - fixed: 固定大小分块（默认）
            - title_aware: 标题感知分块（适合古诗、文档集）
    """
    try:
        # 验证chunker_type
        valid_chunker_types = ["fixed", "title_aware"]
        if chunker_type not in valid_chunker_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的分块策略: {chunker_type}，可选: {valid_chunker_types}"
            )

        with get_db_session() as db:
            doc = get_document(db, document_id)
            if not doc:
                raise HTTPException(status_code=404, detail="文档不存在")

            # 在 session 关闭前提取所需字段
            doc_bot_id = doc.bot_id
            doc_file_path = doc.file_path
            doc_file_type = doc.file_type

            # 先删除旧的ChromaDB数据
            from ...db.chroma import TenantChromaManager
            chroma_manager = TenantChromaManager(doc_bot_id)
            chroma_manager.delete_kb_chunks(document_id)

        # 重新处理
        background_tasks.add_task(
            process_document_task,
            document_id=document_id,
            bot_id=doc_bot_id,
            file_path=doc_file_path,
            file_type=doc_file_type,
            chunker_type=chunker_type
        )

        return {"success": True, "message": f"文档重新索引中（使用 {chunker_type} 分块策略）"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/documents/{document_id}/reindex 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

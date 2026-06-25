"""
=============================================
Admin 管理 API
=============================================
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from ...db.sqlite import (
    create_bot, get_bot, get_all_bots, update_bot, delete_bot,
    create_qa_pair, get_qa_pair, get_bot_qa_pairs, update_qa_pair, delete_qa_pair,
    get_bot_config, update_bot_config,
    create_industry_template, get_industry_template, get_all_templates,
    get_bot_analytics
)
from ...db.sqlite.crud import get_db_session, set_default_bot, get_default_bot, count_bots, get_all_bots_with_default
from ...db.sqlite.crud import get_bot_access, create_or_update_bot_access, get_all_users
from ...core.auth import verify_admin_token


router = APIRouter(prefix="/api/admin", tags=["Admin管理"])


# =============================================
# 请求/响应模型
# =============================================

class CreateBotRequest(BaseModel):
    name: str
    industry_type: str = "general"
    description: Optional[str] = None


class BotResponse(BaseModel):
    id: str
    name: str
    industry_type: str
    description: Optional[str]
    status: str
    is_default: bool = False


class UpdateBotRequest(BaseModel):
    name: Optional[str] = None
    industry_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CreateQARequest(BaseModel):
    bot_id: str
    question: str
    answer: str
    keywords: Optional[str] = None
    category: Optional[str] = None


class QAResponse(BaseModel):
    id: str
    question: str
    answer: str
    keywords: Optional[str]
    category: Optional[str]
    usage_count: int
    satisfaction_rate: Optional[float]


class UpdateQARequest(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    keywords: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class BotConfigRequest(BaseModel):
    welcome_message: Optional[str] = None
    opening_message: Optional[str] = None
    fallback_message: Optional[str] = None
    timeout_message: Optional[str] = None
    personality: Optional[str] = None
    response_tone: Optional[str] = None
    system_prompt: Optional[str] = None
    enable_rag: Optional[bool] = None
    enable_qa_match: Optional[bool] = None
    enable_chitchat: Optional[bool] = None
    rag_top_k: Optional[int] = None
    qa_match_threshold: Optional[float] = None
    enable_rating: Optional[bool] = None
    require_feedback: Optional[bool] = None


class AnalyticsResponse(BaseModel):
    total_conversations: int
    today_conversations: int
    avg_satisfaction: float
    rag_hit_rate: float
    qa_match_rate: float
    document_count: int
    qa_pair_count: int


class BotAccessRequest(BaseModel):
    access_type: str  # "all" | "specific_users" | "specific_teams"
    allowed_users: List[str] = []
    allowed_teams: List[str] = []


class BotAccessResponse(BaseModel):
    bot_id: str
    access_type: str
    allowed_users: List[str] = []
    allowed_teams: List[str] = []


class UserResponse(BaseModel):
    id: str
    username: str
    role: str


class TemplateResponse(BaseModel):
    industry_type: str
    industry_name: str
    description: Optional[str]
    default_categories: List[str]
    sample_qa_pairs: List[dict]


# =============================================
# Bot 管理 API
# =============================================

@router.post("/bots", response_model=BotResponse)
async def create_new_bot(request: CreateBotRequest, _: dict = Depends(verify_admin_token)):
    """创建机器人"""
    try:
        with get_db_session() as db:
            bot = create_bot(
                db=db,
                name=request.name,
                industry_type=request.industry_type,
                description=request.description
            )
            return BotResponse(
                id=bot.id,
                name=bot.name,
                industry_type=bot.industry_type,
                description=bot.description,
                status=bot.status.value
            )
    except Exception as e:
        print(f"[API] /api/admin/bots POST 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bots", response_model=List[BotResponse])
async def list_bots(skip: int = 0, limit: int = 100, _: dict = Depends(verify_admin_token)):
    """获取机器人列表"""
    try:
        with get_db_session() as db:
            bots = get_all_bots_with_default(db, skip=skip, limit=limit)
            return [
                BotResponse(
                    id=bot.id,
                    name=bot.name,
                    industry_type=bot.industry_type,
                    description=bot.description,
                    status=bot.status.value,
                    is_default=bot.is_default
                )
                for bot in bots
            ]
    except Exception as e:
        print(f"[API] /api/admin/bots GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bots/default")
async def get_default(_: dict = Depends(verify_admin_token)):
    """获取当前默认机器人"""
    try:
        with get_db_session() as db:
            bot = get_default_bot(db)
            if not bot:
                return {"has_default": False, "bot": None}
            return {
                "has_default": True,
                "bot": BotResponse(
                    id=bot.id,
                    name=bot.name,
                    industry_type=bot.industry_type,
                    description=bot.description,
                    status=bot.status.value,
                    is_default=bot.is_default
                )
            }
    except Exception as e:
        print(f"[API] /api/admin/bots/default GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bots/default/{bot_id}")
async def set_default(bot_id: str, _: dict = Depends(verify_admin_token)):
    """设置默认机器人"""
    try:
        with get_db_session() as db:
            bot = set_default_bot(db, bot_id)
            if not bot:
                raise HTTPException(status_code=404, detail="Bot不存在")
            return {
                "success": True,
                "message": f"已将 {bot.name} 设为默认机器人",
                "bot": BotResponse(
                    id=bot.id,
                    name=bot.name,
                    industry_type=bot.industry_type,
                    description=bot.description,
                    status=bot.status.value,
                    is_default=bot.is_default
                )
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/bots/default/{bot_id} PUT 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bots/{bot_id}", response_model=BotResponse)
async def get_bot_info(bot_id: str, _: dict = Depends(verify_admin_token)):
    """获取机器人详情"""
    try:
        with get_db_session() as db:
            bot = get_bot(db, bot_id)
            if not bot:
                raise HTTPException(status_code=404, detail="Bot不存在")
            return BotResponse(
                id=bot.id,
                name=bot.name,
                industry_type=bot.industry_type,
                description=bot.description,
                status=bot.status.value
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/bots/{bot_id} GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bots/{bot_id}", response_model=BotResponse)
async def update_bot_info(bot_id: str, request: UpdateBotRequest, _: dict = Depends(verify_admin_token)):
    """更新机器人"""
    try:
        update_data = request.dict(exclude_unset=True)
        with get_db_session() as db:
            bot = update_bot(db, bot_id, **update_data)
            if not bot:
                raise HTTPException(status_code=404, detail="Bot不存在")
            return BotResponse(
                id=bot.id,
                name=bot.name,
                industry_type=bot.industry_type,
                description=bot.description,
                status=bot.status.value
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/bots/{bot_id} PUT 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/bots/{bot_id}")
async def delete_bot_info(bot_id: str, _: dict = Depends(verify_admin_token)):
    """删除机器人"""
    try:
        with get_db_session() as db:
            success = delete_bot(db, bot_id)
            if not success:
                raise HTTPException(status_code=404, detail="Bot不存在")

        # 删除ChromaDB collections
        from ...db.chroma import GlobalChromaManager
        chroma_manager = GlobalChromaManager()
        chroma_manager.delete_bot_collections(bot_id)

        return {"success": True, "message": "Bot已删除"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/bots/{bot_id} DELETE 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================
# Bot 配置 API
# =============================================

@router.get("/bots/{bot_id}/config")
async def get_config(bot_id: str, _: dict = Depends(verify_admin_token)):
    """获取机器人配置"""
    try:
        with get_db_session() as db:
            config = get_bot_config(db, bot_id)
            if not config:
                raise HTTPException(status_code=404, detail="配置不存在")
            return {
                "welcome_message": config.welcome_message,
                "opening_message": config.opening_message,
                "fallback_message": config.fallback_message,
                "timeout_message": config.timeout_message,
                "personality": config.personality,
                "response_tone": config.response_tone,
                "enable_rag": config.enable_rag,
                "enable_qa_match": config.enable_qa_match,
                "enable_chitchat": config.enable_chitchat,
                "rag_top_k": config.rag_top_k,
                "qa_match_threshold": config.qa_match_threshold,
                "enable_rating": config.enable_rating,
                "require_feedback": config.require_feedback
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/bots/{bot_id}/config GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bots/{bot_id}/config")
async def update_config(bot_id: str, request: BotConfigRequest, _: dict = Depends(verify_admin_token)):
    """更新机器人配置"""
    try:
        update_data = request.dict(exclude_unset=True)
        with get_db_session() as db:
            config = update_bot_config(db, bot_id, **update_data)
            if not config:
                raise HTTPException(status_code=404, detail="配置不存在")
            return {"success": True, "message": "配置已更新"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/bots/{bot_id}/config PUT 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================
# Bot 访问权限 API
# =============================================

@router.get("/bots/{bot_id}/access", response_model=BotAccessResponse)
async def get_access_config(bot_id: str, _: dict = Depends(verify_admin_token)):
    """获取机器人访问配置"""
    try:
        with get_db_session() as db:
            bot = get_bot(db, bot_id)
            if not bot:
                raise HTTPException(status_code=404, detail="Bot不存在")

            access = get_bot_access(db, bot_id)
            if not access:
                # 返回默认配置（所有人可访问）
                return BotAccessResponse(
                    bot_id=bot_id,
                    access_type="all",
                    allowed_users=[],
                    allowed_teams=[]
                )
            return BotAccessResponse(
                bot_id=bot_id,
                access_type=access.access_type.value,
                allowed_users=access.allowed_users or [],
                allowed_teams=access.allowed_teams or []
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/bots/{bot_id}/access GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bots/{bot_id}/access", response_model=BotAccessResponse)
async def update_access_config(bot_id: str, request: BotAccessRequest, _: dict = Depends(verify_admin_token)):
    """更新机器人访问配置"""
    try:
        with get_db_session() as db:
            bot = get_bot(db, bot_id)
            if not bot:
                raise HTTPException(status_code=404, detail="Bot不存在")

            access = create_or_update_bot_access(
                db, bot_id,
                access_type=request.access_type,
                allowed_users=request.allowed_users,
                allowed_teams=request.allowed_teams
            )
            return BotAccessResponse(
                bot_id=bot_id,
                access_type=access.access_type.value,
                allowed_users=access.allowed_users or [],
                allowed_teams=access.allowed_teams or []
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/bots/{bot_id}/access PUT 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================
# QA 管理 API
# =============================================

@router.post("/qa", response_model=QAResponse)
async def create_qa(request: CreateQARequest, _: dict = Depends(verify_admin_token)):
    """创建QA对"""
    try:
        with get_db_session() as db:
            qa = create_qa_pair(
                db=db,
                bot_id=request.bot_id,
                question=request.question,
                answer=request.answer,
                keywords=request.keywords,
                category=request.category
            )

            # 添加到ChromaDB
            from ...db.chroma import TenantChromaManager, create_qa_id
            chroma_manager = TenantChromaManager(request.bot_id)
            chroma_manager.add_qa_embeddings([{
                "id": create_qa_id(qa.id),
                "question": qa.question,
                "answer": qa.answer,
                "metadata": {
                    "qa_id": qa.id,
                    "question": qa.question,
                    "answer": qa.answer,
                    "keywords": qa.keywords,
                    "category": qa.category
                }
            }])

            return QAResponse(
                id=qa.id,
                question=qa.question,
                answer=qa.answer,
                keywords=qa.keywords,
                category=qa.category,
                usage_count=qa.usage_count,
                satisfaction_rate=qa.satisfaction_rate
            )
    except Exception as e:
        print(f"[API] /api/admin/qa POST 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/qa", response_model=List[QAResponse])
async def list_qa(bot_id: str, skip: int = 0, limit: int = 100, _: dict = Depends(verify_admin_token)):
    """获取QA列表"""
    try:
        with get_db_session() as db:
            qa_pairs = get_bot_qa_pairs(db, bot_id, skip=skip, limit=limit)
            return [
                QAResponse(
                    id=qa.id,
                    question=qa.question,
                    answer=qa.answer,
                    keywords=qa.keywords,
                    category=qa.category,
                    usage_count=qa.usage_count,
                    satisfaction_rate=qa.satisfaction_rate
                )
                for qa in qa_pairs
            ]
    except Exception as e:
        print(f"[API] /api/admin/qa GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/qa/{qa_id}", response_model=QAResponse)
async def update_qa(qa_id: str, request: UpdateQARequest, _: dict = Depends(verify_admin_token)):
    """更新QA对"""
    try:
        update_data = request.dict(exclude_unset=True)
        with get_db_session() as db:
            qa = update_qa_pair(db, qa_id, **update_data)
            if not qa:
                raise HTTPException(status_code=404, detail="QA不存在")
            return QAResponse(
                id=qa.id,
                question=qa.question,
                answer=qa.answer,
                keywords=qa.keywords,
                category=qa.category,
                usage_count=qa.usage_count,
                satisfaction_rate=qa.satisfaction_rate
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/qa/{qa_id} PUT 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/qa/{qa_id}")
async def delete_qa(qa_id: str, _: dict = Depends(verify_admin_token)):
    """删除QA对"""
    try:
        with get_db_session() as db:
            # 获取bot_id以便删除ChromaDB数据
            qa = get_qa_pair(db, qa_id)
            if not qa:
                raise HTTPException(status_code=404, detail="QA不存在")

            bot_id = qa.bot_id

            success = delete_qa_pair(db, qa_id)
            if success:
                # 从ChromaDB删除
                from ...db.chroma import TenantChromaManager
                chroma_manager = TenantChromaManager(bot_id)
                chroma_manager.delete_qa_embedding(qa_id)

        return {"success": True, "message": "QA已删除"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/qa/{qa_id} DELETE 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================
# 行业模板 API
# =============================================

@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(_: dict = Depends(verify_admin_token)):
    """获取行业模板列表"""
    try:
        with get_db_session() as db:
            templates = get_all_templates(db)
            return [
                TemplateResponse(
                    industry_type=t.industry_type,
                    industry_name=t.industry_name,
                    description=t.description,
                    default_categories=t.default_categories or [],
                    sample_qa_pairs=t.sample_qa_pairs or []
                )
                for t in templates
            ]
    except Exception as e:
        print(f"[API] /api/admin/templates GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/{industry_type}/apply")
async def apply_template(bot_id: str, industry_type: str, _: dict = Depends(verify_admin_token)):
    """应用行业模板到机器人"""
    try:
        with get_db_session() as db:
            template = get_industry_template(db, industry_type)
            if not template:
                raise HTTPException(status_code=404, detail="模板不存在")

            # 更新bot配置
            update_bot(db, bot_id, industry_type=industry_type)

            return {
                "success": True,
                "message": f"已应用{template.industry_name}模板",
                "template": {
                    "industry_type": template.industry_type,
                    "industry_name": template.industry_name,
                    "default_categories": template.default_categories,
                    "recommended_chunk_size": template.recommended_chunk_size
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/admin/templates/{industry_type}/apply 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================
# 数据分析 API
# =============================================

@router.get("/analytics/{bot_id}", response_model=AnalyticsResponse)
async def get_analytics(bot_id: str, days: int = 7, _: dict = Depends(verify_admin_token)):
    """获取机器人统计数据"""
    try:
        with get_db_session() as db:
            stats = get_bot_analytics(db, bot_id, days=days)
            return AnalyticsResponse(**stats)
    except Exception as e:
        print(f"[API] /api/admin/analytics/{bot_id} GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chunks/{bot_id}")
async def get_bot_chunks(bot_id: str, _: dict = Depends(verify_admin_token)):
    """获取机器人的所有向量片段（KB chunks 和 QA embeddings）"""
    try:
        from ...db.chroma import TenantChromaManager, get_kb_collection_name, get_qa_collection_name

        chroma_manager = TenantChromaManager(bot_id)

        # 获取KB chunks
        kb_collection = chroma_manager._get_kb_collection()
        kb_data = kb_collection.get(include=["documents", "metadatas"])

        # 获取QA embeddings
        qa_collection = chroma_manager._get_qa_collection()
        qa_data = qa_collection.get(include=["documents", "metadatas"])

        return {
            "kb_chunks": {
                "count": kb_collection.count(),
                "items": [
                    {
                        "id": kb_data["ids"][i] if i < len(kb_data["ids"]) else "",
                        "content": kb_data["documents"][i] if i < len(kb_data["documents"]) else "",
                        "metadata": kb_data["metadatas"][i] if i < len(kb_data["metadatas"]) else {}
                    }
                    for i in range(len(kb_data.get("ids", [])))
                ]
            },
            "qa_embeddings": {
                "count": qa_collection.count(),
                "items": [
                    {
                        "id": qa_data["ids"][i] if i < len(qa_data["ids"]) else "",
                        "question": qa_data["documents"][i] if i < len(qa_data["documents"]) else "",
                        "metadata": qa_data["metadatas"][i] if i < len(qa_data["metadatas"]) else {}
                    }
                    for i in range(len(qa_data.get("ids", [])))
                ]
            }
        }
    except Exception as e:
        print(f"[API] /api/admin/chunks/{bot_id} GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================
# User 管理 API
# =============================================

@router.get("/users", response_model=List[UserResponse])
async def list_users(_: dict = Depends(verify_admin_token)):
    """获取所有用户列表（仅管理员）"""
    try:
        with get_db_session() as db:
            users = get_all_users(db)
            return [
                UserResponse(
                    id=user.id,
                    username=user.username,
                    role=user.role.value
                )
                for user in users
            ]
    except Exception as e:
        print(f"[API] /api/admin/users GET 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

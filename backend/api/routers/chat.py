"""
=============================================
用户端聊天 API
=============================================
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from ...graph import chat
from ...db.sqlite import (
    get_session_conversations, create_conversation, get_bot_config,
    get_bot, ConversationSource
)
from ...db.sqlite.crud import get_db_session, get_all_bots_with_default
from ...core.auth import decode_token, verify_password


router = APIRouter(prefix="/api", tags=["用户端"])


# =============================================
# 请求/响应模型
# =============================================

class ChatRequest(BaseModel):
    """聊天请求"""
    bot_id: Optional[str] = None  # 可选，不提供则使用默认机器人
    session_id: str
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str
    source: str
    intent: str
    confidence: float
    reference_doc_id: Optional[str] = None
    reference_qa_id: Optional[str] = None
    conversation_id: str


class Message(BaseModel):
    """消息"""
    id: str
    content: str
    is_from_user: bool
    source: str
    timestamp: datetime


class HistoryResponse(BaseModel):
    """历史记录响应"""
    session_id: str
    messages: List[Message]


class RateRequest(BaseModel):
    """评价请求"""
    conversation_id: str
    rating: int
    feedback: Optional[str] = None
    feedback_reason: Optional[str] = None


class RateResponse(BaseModel):
    """评价响应"""
    success: bool
    message: str


class PublicBotResponse(BaseModel):
    """公开机器人信息"""
    id: str
    name: str
    industry_type: str
    description: Optional[str]
    is_default: bool


# =============================================
# API 端点
# =============================================

@router.post("/chat", response_model=ChatResponse)
async def send_message(request: ChatRequest, authorization: Optional[str] = Header(None)):
    """
    发送消息并获取回复

    这是智能客服的核心接口：
    1. 接收用户问题
    2. 执行RAG+QA双轨工作流
    3. 返回AI回复
    """
    try:
        from ...db.sqlite import get_bot_config, create_conversation
        from ...db.sqlite.crud import get_db_session, get_bot, get_default_bot, increment_qa_usage
        from ...db.sqlite.crud import check_user_bot_access, get_user_teams
        from ...db.sqlite.models import ConversationSource

        config_dict = {}
        user_conv_id = ""
        bot_id = request.bot_id

        # 解析用户信息（可选）
        user_id = request.user_id
        user_role = "anonymous"
        user_team_ids = []

        if authorization:
            token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
            payload = decode_token(token)
            if payload:
                user_id = payload.get("sub")
                user_role = payload.get("role", "anonymous")
                user_team_ids = payload.get("team_ids", [])

        # 在session中获取bot配置和保存用户消息
        with get_db_session() as db:
            # 如果没有提供bot_id，获取默认机器人
            if not bot_id:
                default_bot = get_default_bot(db)
                if not default_bot:
                    raise HTTPException(status_code=400, detail="没有设置默认机器人，请联系管理员")
                bot_id = default_bot.id

            bot = get_bot(db, bot_id)
            if not bot:
                raise HTTPException(status_code=404, detail=f"Bot不存在: {bot_id}")

            # 检查机器人访问权限
            has_access = check_user_bot_access(db, user_id or "", user_team_ids, bot_id)
            if not has_access:
                raise HTTPException(
                    status_code=403,
                    detail="您没有权限使用此机器人"
                )

            bot_config = get_bot_config(db, bot_id)
            if bot_config:
                config_dict = {
                    "welcome_message": bot_config.welcome_message,
                    "opening_message": bot_config.opening_message,
                    "fallback_message": bot_config.fallback_message,
                    "timeout_message": bot_config.timeout_message,
                    "personality": bot_config.personality,
                    "response_tone": bot_config.response_tone,
                    "system_prompt": bot_config.system_prompt,
                    "enable_rag": bot_config.enable_rag,
                    "enable_qa_match": bot_config.enable_qa_match,
                    "enable_chitchat": bot_config.enable_chitchat,
                    "rag_top_k": bot_config.rag_top_k,
                    "rag_rerank_top_k": bot_config.rag_rerank_top_k,
                    "qa_match_threshold": bot_config.qa_match_threshold,
                    "industry_type": bot.industry_type
                }

            # 保存用户消息
            user_conv_id = create_conversation(
                db=db,
                bot_id=bot_id,
                session_id=request.session_id,
                message=request.message,
                user_id=request.user_id,
                is_from_user=True,
                source=ConversationSource.LLM
            ).id

        # 执行聊天（不需要db session）
        result = chat(
            user_input=request.message,
            session_id=request.session_id,
            bot_id=bot_id,
            user_id=request.user_id,
            bot_config=config_dict
        )

        # 保存AI回复
        with get_db_session() as db:
            create_conversation(
                db=db,
                bot_id=bot_id,
                session_id=request.session_id,
                message=result["response"],
                user_id=request.user_id,
                is_from_user=False,
                source=ConversationSource(result["source"]),
                confidence_score=result.get("confidence"),
                reference_doc_id=result.get("reference_doc_id"),
                reference_qa_id=result.get("reference_qa_id")
            )

            # 更新QA使用次数
            if result.get("reference_qa_id"):
                increment_qa_usage(db, result["reference_qa_id"])

        return ChatResponse(
            response=result["response"],
            source=result["source"],
            intent=result.get("intent", "question"),
            confidence=result.get("confidence", 0.0),
            reference_doc_id=result.get("reference_doc_id"),
            reference_qa_id=result.get("reference_qa_id"),
            conversation_id=user_conv_id
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/chat 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(bot_id: str, session_id: str):
    """
    获取会话历史记录
    """
    try:
        from ...db.sqlite.crud import get_db_session

        with get_db_session() as db:
            conversations = get_session_conversations(db, bot_id, session_id)
            # 在session关闭前提取所有需要的数据
            messages = [
                Message(
                    id=conv.id,
                    content=conv.message,
                    is_from_user=conv.is_from_user,
                    source=conv.source.value if conv.source else "llm",
                    timestamp=conv.created_at
                )
                for conv in conversations
            ]

        return HistoryResponse(
            session_id=session_id,
            messages=messages
        )

    except Exception as e:
        print(f"[API] /api/history 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rate", response_model=RateResponse)
async def rate_conversation(request: RateRequest):
    """
    评价对话
    """
    try:
        from ...db.sqlite import create_rating, get_conversation
        from ...db.sqlite.crud import get_db_session

        # 验证conversation存在
        with get_db_session() as db:
            conversation = get_conversation(db, request.conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="对话不存在")

            # 创建评价
            create_rating(
                db=db,
                conversation_id=request.conversation_id,
                bot_id=conversation.bot_id,
                rating=request.rating,
                feedback=request.feedback,
                feedback_reason=request.feedback_reason
            )

            # 更新QA满意度
            if conversation.reference_qa_id and request.rating > 0:
                from ...db.sqlite import update_qa_satisfaction
                update_qa_satisfaction(db, conversation.reference_qa_id, request.rating)

        return RateResponse(
            success=True,
            message="评价已提交，感谢您的反馈"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] /api/rate 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bots", response_model=List[PublicBotResponse])
async def list_public_bots(authorization: Optional[str] = Header(None)):
    """
    获取机器人列表（根据用户权限返回不同的机器人）
    - 匿名用户：只能看到默认机器人
    - 登录用户：能看到有权限访问的机器人
    """
    try:
        from ...db.sqlite.crud import get_accessible_bots

        # 解析用户信息
        user_id = None
        user_role = "anonymous"
        user_team_ids = []

        if authorization:
            token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
            payload = decode_token(token)
            if payload:
                user_id = payload.get("sub")
                user_role = payload.get("role", "anonymous")
                user_team_ids = payload.get("team_ids", [])

        with get_db_session() as db:
            if user_role == "anonymous" or not user_id:
                bots = get_accessible_bots(db, is_anonymous=True)
            else:
                bots = get_accessible_bots(db, user_id, user_team_ids)

            return [
                PublicBotResponse(
                    id=bot.id,
                    name=bot.name,
                    industry_type=bot.industry_type,
                    description=bot.description,
                    is_default=bot.is_default
                )
                for bot in bots
            ]
    except Exception as e:
        print(f"[API] /api/bots 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

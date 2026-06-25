"""
=============================================
用户路由
=============================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

from ...core.auth import get_current_user_payload
from ...db.sqlite import get_db_session, get_user_by_id, get_all_bots, get_user_teams
from ...db.sqlite import get_accessible_bots

router = APIRouter(prefix="/api/users", tags=["用户"])


class UserInfo(BaseModel):
    id: str
    username: str
    role: str
    team_ids: List[str] = []


class BotInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    industry_type: Optional[str] = None
    is_default: bool = False


@router.get("/me", response_model=UserInfo)
async def get_current_user(payload: dict = Depends(get_current_user_payload)):
    """获取当前用户信息"""
    user_id = payload.get("sub")
    with get_db_session() as db:
        user = get_user_by_id(db, user_id)
        if not user:
            return UserInfo(
                id=user_id,
                username=payload.get("username", ""),
                role=payload.get("role", "anonymous"),
                team_ids=payload.get("team_ids", [])
            )
        teams = get_user_teams(db, user.id)
        return UserInfo(
            id=user.id,
            username=user.username,
            role=user.role.value,
            team_ids=[t.id for t in teams]
        )


@router.get("/available-bots", response_model=List[BotInfo])
async def get_available_bots(payload: dict = Depends(get_current_user_payload)):
    """获取当前用户可用的机器人列表"""
    user_id = payload.get("sub")
    role = payload.get("role", "anonymous")
    team_ids = payload.get("team_ids", [])

    with get_db_session() as db:
        # 匿名用户只能访问默认机器人
        if role == "anonymous" or not user_id:
            bots = get_accessible_bots(db, is_anonymous=True)
        else:
            bots = get_accessible_bots(db, user_id, team_ids)

        return [
            BotInfo(
                id=bot.id,
                name=bot.name,
                description=bot.description,
                industry_type=bot.industry_type,
                is_default=bot.is_default
            )
            for bot in bots
        ]

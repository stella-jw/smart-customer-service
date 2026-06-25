"""
=============================================
团队管理 API
=============================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ...core.auth import verify_admin_token, get_current_admin_id
from ...db.sqlite import get_db_session
from ...db.sqlite.crud import (
    create_team, get_team, get_all_teams, update_team, delete_team,
    add_team_member, remove_team_member, get_team_members, get_user_teams,
    get_all_users
)

router = APIRouter(prefix="/api/teams", tags=["团队管理"])


# =============================================
# 请求/响应模型
# =============================================

class TeamCreate(BaseModel):
    name: str


class TeamUpdate(BaseModel):
    name: str


class TeamResponse(BaseModel):
    id: str
    name: str
    member_count: int = 0


class TeamMemberAdd(BaseModel):
    user_id: str


class TeamMemberResponse(BaseModel):
    id: str
    username: str


# =============================================
# API 端点
# =============================================

@router.get("", response_model=List[TeamResponse])
async def list_teams(payload: dict = Depends(verify_admin_token)):
    """获取所有团队列表（仅管理员）"""
    with get_db_session() as db:
        teams = get_all_teams(db)
        return [
            TeamResponse(
                id=team.id,
                name=team.name,
                member_count=len(team.members) if team.members else 0
            )
            for team in teams
        ]


@router.post("", response_model=TeamResponse)
async def create_new_team(request: TeamCreate, payload: dict = Depends(verify_admin_token)):
    """创建团队（仅管理员）"""
    with get_db_session() as db:
        team = create_team(db, request.name)
        return TeamResponse(
            id=team.id,
            name=team.name,
            member_count=0
        )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team_info(team_id: str, payload: dict = Depends(verify_admin_token)):
    """获取团队详情（仅管理员）"""
    with get_db_session() as db:
        team = get_team(db, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="团队不存在")
        return TeamResponse(
            id=team.id,
            name=team.name,
            member_count=len(team.members) if team.members else 0
        )


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team_info(team_id: str, request: TeamUpdate, payload: dict = Depends(verify_admin_token)):
    """更新团队（仅管理员）"""
    with get_db_session() as db:
        team = update_team(db, team_id, request.name)
        if not team:
            raise HTTPException(status_code=404, detail="团队不存在")
        return TeamResponse(
            id=team.id,
            name=team.name,
            member_count=len(team.members) if team.members else 0
        )


@router.delete("/{team_id}")
async def delete_team_endpoint(team_id: str, payload: dict = Depends(verify_admin_token)):
    """删除团队（仅管理员）"""
    with get_db_session() as db:
        if not delete_team(db, team_id):
            raise HTTPException(status_code=404, detail="团队不存在")
        return {"success": True, "message": "团队已删除"}


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(team_id: str, payload: dict = Depends(verify_admin_token)):
    """获取团队成员列表（仅管理员）"""
    with get_db_session() as db:
        team = get_team(db, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="团队不存在")
        members = get_team_members(db, team_id)
        return [
            TeamMemberResponse(id=member.id, username=member.username)
            for member in members
        ]


@router.post("/{team_id}/members")
async def add_team_member_endpoint(team_id: str, request: TeamMemberAdd, payload: dict = Depends(verify_admin_token)):
    """添加团队成员（仅管理员）"""
    with get_db_session() as db:
        team = get_team(db, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="团队不存在")
        add_team_member(db, team_id, request.user_id)
        return {"success": True, "message": "成员已添加"}


@router.delete("/{team_id}/members/{user_id}")
async def remove_team_member_endpoint(team_id: str, user_id: str, payload: dict = Depends(verify_admin_token)):
    """移除团队成员（仅管理员）"""
    with get_db_session() as db:
        if not remove_team_member(db, team_id, user_id):
            raise HTTPException(status_code=404, detail="成员不在团队中")
        return {"success": True, "message": "成员已移除"}

"""
=============================================
认证路由
=============================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...core.auth import (
    hash_password, verify_password, create_access_token,
    verify_admin_token, verify_any_token, get_current_user_payload
)
from ...db.sqlite import get_db_session, create_admin, get_admin_by_username
from ...db.sqlite import create_user, get_user_by_username, get_user_teams

router = APIRouter(prefix="/api/auth", tags=["认证"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "internal"  # internal or admin


class AuthResponse(BaseModel):
    success: bool
    message: str
    token: str = None
    user_id: str = None
    role: str = None


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """用户登录（支持管理员和内部用户）"""
    with get_db_session() as db:
        # 先检查是否是管理员
        admin = get_admin_by_username(db, request.username)
        if admin:
            if not verify_password(request.password, admin.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误"
                )
            token = create_access_token(admin.id, admin.username, "admin")
            return AuthResponse(
                success=True,
                message="管理员登录成功",
                token=token,
                user_id=admin.id,
                role="admin"
            )

        # 再检查是否是内部用户
        user = get_user_by_username(db, request.username)
        if user:
            if not verify_password(request.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误"
                )
            # 获取用户的团队列表
            teams = get_user_teams(db, user.id)
            team_ids = [t.id for t in teams]
            role = "admin" if user.role.value == "admin" else "internal"
            token = create_access_token(user.id, user.username, role, team_ids)
            return AuthResponse(
                success=True,
                message="登录成功",
                token=token,
                user_id=user.id,
                role=role
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """注册用户（仅允许注册内部用户，管理员通过后台创建）"""
    with get_db_session() as db:
        # 检查管理员是否存在
        existing_admin = get_admin_by_username(db, request.username)
        # 检查用户是否存在
        existing_user = get_user_by_username(db, request.username)
        if existing_admin or existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )

        password_hash = hash_password(request.password)
        user = create_user(db, request.username, password_hash, request.role)

        token = create_access_token(user.id, user.username, user.role.value)

        return AuthResponse(
            success=True,
            message="注册成功",
            token=token,
            user_id=user.id,
            role=user.role.value
        )


@router.get("/verify")
async def verify_token(payload: dict = Depends(get_current_user_payload)):
    """验证令牌"""
    return {
        "valid": True,
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role"),
        "team_ids": payload.get("team_ids", [])
    }


@router.post("/logout")
async def logout():
    """登出（JWT无状态，只需客户端删除token）"""
    return {"success": True, "message": "登出成功"}

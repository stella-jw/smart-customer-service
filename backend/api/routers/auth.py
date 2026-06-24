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
    hash_password, verify_password, create_access_token, verify_admin_token
)
from ...db.sqlite import get_db_session, create_admin, get_admin_by_username

router = APIRouter(prefix="/api/auth", tags=["认证"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    token: str = None
    admin_id: str = None


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """管理员登录"""
    with get_db_session() as db:
        admin = get_admin_by_username(db, request.username)

        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        if not verify_password(request.password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        token = create_access_token(admin.id, admin.username)

        return AuthResponse(
            success=True,
            message="登录成功",
            token=token,
            admin_id=admin.id
        )


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """注册管理员"""
    with get_db_session() as db:
        existing = get_admin_by_username(db, request.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )

        password_hash = hash_password(request.password)
        admin = create_admin(db, request.username, password_hash)

        token = create_access_token(admin.id, admin.username)

        return AuthResponse(
            success=True,
            message="注册成功",
            token=token,
            admin_id=admin.id
        )


@router.get("/verify")
async def verify_token(payload: dict = Depends(verify_admin_token)):
    """验证令牌"""
    return {
        "valid": True,
        "admin_id": payload.get("sub"),
        "username": payload.get("username")
    }

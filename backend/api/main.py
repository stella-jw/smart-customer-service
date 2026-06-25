"""
=============================================
FastAPI 应用入口
=============================================

智能客服系统 REST API 接口
"""

import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from backend.db.sqlite import init_database
from backend.api.routers import chat_router, admin_router, knowledge_router, auth_router, users_router, teams_router
from pydantic import BaseModel


# =============================================
# 响应模型
# =============================================

class HealthResponse(BaseModel):
    status: str
    version: str


# =============================================
# Lifespan
# =============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("[API] 智能客服系统启动")

    # 初始化数据库
    init_database()

    print("[API] 数据库初始化完成")
    yield
    print("[API] 智能客服系统关闭")


# =============================================
# FastAPI 应用
# =============================================

app = FastAPI(
    title="智能客服系统 API",
    description="通用型企业智能客服 REST API 接口",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_router)      # /api/chat, /api/history, /api/rate
app.include_router(admin_router)     # /api/admin/*
app.include_router(knowledge_router)  # /api/admin/documents/*
app.include_router(auth_router)      # /api/auth/*
app.include_router(users_router)     # /api/users/*
app.include_router(teams_router)     # /api/teams/*


# =============================================
# 健康检查
# =============================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(status="ok", version="1.0.0")


# =============================================
# 启动命令
# =============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )

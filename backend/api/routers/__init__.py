"""
=============================================
API 路由模块
=============================================
"""

from .chat import router as chat_router
from .admin import router as admin_router
from .knowledge import router as knowledge_router
from .auth import router as auth_router

__all__ = ["chat_router", "admin_router", "knowledge_router", "auth_router"]

"""
=============================================
SQLite 数据库模型定义
=============================================
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    DateTime, ForeignKey, JSON, Enum, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class BotStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"


class DocumentStatus(str, PyEnum):
    PENDING = "pending"
    PARSING = "parsing"
    INDEXED = "indexed"
    FAILED = "failed"


class ConversationSource(str, PyEnum):
    RAG = "rag"
    QA = "qa"
    LLM = "llm"
    FALLBACK = "fallback"


class Bot(Base):
    """机器人表"""
    __tablename__ = "bots"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    industry_type = Column(String(50))  # medical/ecommerce/saas/it/general
    status = Column(Enum(BotStatus), default=BotStatus.ACTIVE)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    documents = relationship("Document", back_populates="bot", cascade="all, delete-orphan")
    qa_pairs = relationship("QAPair", back_populates="bot", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="bot", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="bot", cascade="all, delete-orphan")
    configuration = relationship("BotConfiguration", back_populates="bot", uselist=False, cascade="all, delete-orphan")


class Document(Base):
    """文档表"""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True)
    bot_id = Column(String(36), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf/docx/txt/md/html
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    error_message = Column(Text)
    chunk_count = Column(Integer, default=0)
    doc_metadata = Column(JSON)  # {section, url, author}
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    bot = relationship("Bot", back_populates="documents")


class QAPair(Base):
    """QA对表"""
    __tablename__ = "qa_pairs"

    id = Column(String(36), primary_key=True)
    bot_id = Column(String(36), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    question_norm = Column(Text)  # 归一化问题
    answer = Column(Text, nullable=False)
    keywords = Column(String(500))
    category = Column(String(100))
    usage_count = Column(Integer, default=0)
    satisfaction_rate = Column(Float)
    rating_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    bot = relationship("Bot", back_populates="qa_pairs")


class Conversation(Base):
    """对话记录表"""
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True)
    bot_id = Column(String(36), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(100), nullable=False)
    user_id = Column(String(100))
    message = Column(Text, nullable=False)
    is_from_user = Column(Boolean, default=True)
    source = Column(Enum(ConversationSource), default=ConversationSource.LLM)
    confidence_score = Column(Float)
    reference_doc_id = Column(String(36), ForeignKey("documents.id"))
    reference_qa_id = Column(String(36), ForeignKey("qa_pairs.id"))
    conv_metadata = Column(JSON)  # {intent, entities}
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    bot = relationship("Bot", back_populates="conversations")
    ratings = relationship("Rating", back_populates="conversation", cascade="all, delete-orphan")


class Rating(Base):
    """评价记录表"""
    __tablename__ = "ratings"

    id = Column(String(36), primary_key=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    bot_id = Column(String(36), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    feedback = Column(Text)
    feedback_reason = Column(String(50))  # inaccurate/irrelevant/incomplete/other
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    conversation = relationship("Conversation", back_populates="ratings")
    bot = relationship("Bot", back_populates="ratings")


class BotConfiguration(Base):
    """机器人配置表"""
    __tablename__ = "bot_configurations"

    id = Column(String(36), primary_key=True)
    bot_id = Column(String(36), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False, unique=True)

    # 话术配置
    welcome_message = Column(Text)
    opening_message = Column(Text)
    timeout_message = Column(Text)
    fallback_message = Column(Text)

    # 机器人人格
    personality = Column(String(50), default="friendly")  # professional/friendly/humorous/empathetic
    response_tone = Column(String(50), default="friendly")  # formal/casual/brief/detailed

    # 功能开关
    enable_rag = Column(Boolean, default=True)
    enable_qa_match = Column(Boolean, default=True)
    enable_clarification = Column(Boolean, default=True)
    enable_chitchat = Column(Boolean, default=True)
    enable_suggestions = Column(Boolean, default=True)

    # 检索参数
    rag_top_k = Column(Integer, default=5)
    qa_match_threshold = Column(Float, default=0.85)

    # 评价设置
    enable_rating = Column(Boolean, default=True)
    require_feedback = Column(Boolean, default=False)
    rating_prompt = Column(Text, default="您对我的回答满意吗？")
    feedback_options = Column(JSON, default=["不准确", "不相关", "不完整", "其他"])

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    bot = relationship("Bot", back_populates="configuration")


class IndustryTemplate(Base):
    """行业模板表"""
    __tablename__ = "industry_templates"

    id = Column(String(36), primary_key=True)
    industry_type = Column(String(50), nullable=False, unique=True)
    industry_name = Column(String(100), nullable=False)
    description = Column(Text)
    default_categories = Column(JSON)  # ["产品咨询", "售后支持", "技术问题"]
    sample_qa_pairs = Column(JSON)
    recommended_chunk_size = Column(Integer, default=500)
    created_at = Column(DateTime, default=datetime.now)


class Admin(Base):
    """管理员表"""
    __tablename__ = "admins"

    id = Column(String(36), primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


# =============================================
# 数据库初始化
# =============================================

DATABASE_PATH = "./data/customer_service.db"


def get_engine(database_path: str = DATABASE_PATH):
    """创建数据库引擎"""
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    return create_engine(f"sqlite:///{database_path}")


def init_database(engine=None):
    """初始化数据库表"""
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(engine)


import os  # 需要os模块用于目录创建

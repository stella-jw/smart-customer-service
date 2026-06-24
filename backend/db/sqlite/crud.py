"""
=============================================
SQLite CRUD 操作
=============================================
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import and_, or_

from .models import (
    Base, Bot, Document, QAPair, Conversation, Rating,
    BotConfiguration, IndustryTemplate, Admin, BotStatus, DocumentStatus, ConversationSource
)


def generate_id() -> str:
    """生成UUID"""
    return str(uuid.uuid4())


# =============================================
# Bot CRUD
# =============================================

def create_bot(db: Session, name: str, industry_type: str = "general",
               description: str = None) -> Bot:
    """创建机器人"""
    bot = Bot(
        id=generate_id(),
        name=name,
        industry_type=industry_type,
        description=description
    )
    db.add(bot)

    # 同时创建默认配置
    config = BotConfiguration(
        id=generate_id(),
        bot_id=bot.id
    )
    db.add(config)

    db.commit()
    db.refresh(bot)
    return bot


def get_bot(db: Session, bot_id: str) -> Optional[Bot]:
    """获取机器人"""
    return db.query(Bot).filter(Bot.id == bot_id).first()


def get_all_bots(db: Session, skip: int = 0, limit: int = 100) -> List[Bot]:
    """获取所有机器人"""
    return db.query(Bot).offset(skip).limit(limit).all()


def update_bot(db: Session, bot_id: str, **kwargs) -> Optional[Bot]:
    """更新机器人"""
    bot = get_bot(db, bot_id)
    if bot:
        for key, value in kwargs.items():
            if hasattr(bot, key):
                setattr(bot, key, value)
        bot.updated_at = datetime.now()
        db.commit()
        db.refresh(bot)
    return bot


def delete_bot(db: Session, bot_id: str) -> bool:
    """删除机器人（不允许删除默认机器人）"""
    bot = get_bot(db, bot_id)
    if bot:
        if bot.is_default:
            raise ValueError("无法删除默认机器人，请先设置另一个机器人为默认")
        db.delete(bot)
        db.commit()
        return True
    return False


def set_default_bot(db: Session, bot_id: str) -> Optional[Bot]:
    """设置默认机器人"""
    # 检查 bot 是否存在
    bot = get_bot(db, bot_id)
    if not bot:
        return None

    # 取消所有机器人的默认状态
    db.query(Bot).filter(Bot.is_default == True).update({"is_default": False})

    # 设置新的默认
    bot.is_default = True
    bot.updated_at = datetime.now()
    db.commit()
    db.refresh(bot)
    return bot


def get_default_bot(db: Session) -> Optional[Bot]:
    """获取默认机器人"""
    return db.query(Bot).filter(Bot.is_default == True).first()


def get_all_bots_with_default(db: Session, skip: int = 0, limit: int = 100) -> List[Bot]:
    """获取所有机器人（包括默认状态）"""
    return db.query(Bot).offset(skip).limit(limit).all()


def count_bots(db: Session) -> int:
    """统计机器人数量"""
    return db.query(Bot).count()


# =============================================
# Document CRUD
# =============================================

def create_document(db: Session, bot_id: str, title: str, file_type: str,
                    file_path: str, file_size: int = None, doc_metadata: dict = None) -> Document:
    """创建文档记录"""
    doc = Document(
        id=generate_id(),
        bot_id=bot_id,
        title=title,
        file_type=file_type,
        file_path=file_path,
        file_size=file_size,
        doc_metadata=doc_metadata,
        status=DocumentStatus.PENDING
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document(db: Session, document_id: str) -> Optional[Document]:
    """获取文档"""
    return db.query(Document).filter(Document.id == document_id).first()


def get_bot_documents(db: Session, bot_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
    """获取机器人的所有文档"""
    return db.query(Document).filter(Document.bot_id == bot_id).offset(skip).limit(limit).all()


def update_document(db: Session, document_id: str, **kwargs) -> Optional[Document]:
    """更新文档"""
    doc = get_document(db, document_id)
    if doc:
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        doc.updated_at = datetime.now()
        db.commit()
        db.refresh(doc)
    return doc


def delete_document(db: Session, document_id: str) -> bool:
    """删除文档"""
    doc = get_document(db, document_id)
    if doc:
        db.delete(doc)
        db.commit()
        return True
    return False


# =============================================
# QAPair CRUD
# =============================================

def create_qa_pair(db: Session, bot_id: str, question: str, answer: str,
                   keywords: str = None, category: str = None) -> QAPair:
    """创建QA对"""
    qa = QAPair(
        id=generate_id(),
        bot_id=bot_id,
        question=question,
        answer=answer,
        keywords=keywords,
        category=category
    )
    db.add(qa)
    db.commit()
    db.refresh(qa)
    return qa


def get_qa_pair(db: Session, qa_id: str) -> Optional[QAPair]:
    """获取QA对"""
    return db.query(QAPair).filter(QAPair.id == qa_id).first()


def get_bot_qa_pairs(db: Session, bot_id: str, skip: int = 0, limit: int = 100,
                     only_active: bool = True) -> List[QAPair]:
    """获取机器人的所有QA对"""
    query = db.query(QAPair).filter(QAPair.bot_id == bot_id)
    if only_active:
        query = query.filter(QAPair.is_active == True)
    return query.offset(skip).limit(limit).all()


def update_qa_pair(db: Session, qa_id: str, **kwargs) -> Optional[QAPair]:
    """更新QA对"""
    qa = get_qa_pair(db, qa_id)
    if qa:
        for key, value in kwargs.items():
            if hasattr(qa, key):
                setattr(qa, key, value)
        qa.updated_at = datetime.now()
        db.commit()
        db.refresh(qa)
    return qa


def delete_qa_pair(db: Session, qa_id: str) -> bool:
    """删除QA对"""
    qa = get_qa_pair(db, qa_id)
    if qa:
        db.delete(qa)
        db.commit()
        return True
    return False


def increment_qa_usage(db: Session, qa_id: str) -> Optional[QAPair]:
    """增加QA对使用次数"""
    qa = get_qa_pair(db, qa_id)
    if qa:
        qa.usage_count += 1
        db.commit()
        db.refresh(qa)
    return qa


def update_qa_satisfaction(db: Session, qa_id: str, rating: int) -> Optional[QAPair]:
    """更新QA对满意度"""
    qa = get_qa_pair(db, qa_id)
    if qa:
        qa.rating_count += 1
        # 计算新的满意度
        if qa.satisfaction_rate is None:
            qa.satisfaction_rate = rating
        else:
            qa.satisfaction_rate = (qa.satisfaction_rate * (qa.rating_count - 1) + rating) / qa.rating_count
        db.commit()
        db.refresh(qa)
    return qa


# =============================================
# Conversation CRUD
# =============================================

def create_conversation(db: Session, bot_id: str, session_id: str, message: str,
                        user_id: str = None, is_from_user: bool = True,
                        source: ConversationSource = ConversationSource.LLM,
                        confidence_score: float = None, reference_doc_id: str = None,
                        reference_qa_id: str = None, conv_metadata: dict = None) -> Conversation:
    """创建对话记录"""
    conv = Conversation(
        id=generate_id(),
        bot_id=bot_id,
        session_id=session_id,
        user_id=user_id,
        message=message,
        is_from_user=is_from_user,
        source=source,
        confidence_score=confidence_score,
        reference_doc_id=reference_doc_id,
        reference_qa_id=reference_qa_id,
        conv_metadata=conv_metadata
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def get_conversation(db: Session, conversation_id: str) -> Optional[Conversation]:
    """获取对话"""
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_session_conversations(db: Session, bot_id: str, session_id: str) -> List[Conversation]:
    """获取会话的所有对话"""
    return db.query(Conversation).filter(
        and_(Conversation.bot_id == bot_id, Conversation.session_id == session_id)
    ).order_by(Conversation.created_at).all()


def get_user_sessions(db: Session, bot_id: str, user_id: str = None,
                      skip: int = 0, limit: int = 50) -> List:
    """获取用户的所有会话ID列表"""
    query = db.query(Conversation.session_id, Conversation.bot_id).filter(
        Conversation.bot_id == bot_id
    )
    if user_id:
        query = query.filter(Conversation.user_id == user_id)

    # 去重并按最新消息排序
    results = db.query(Conversation).filter(
        Conversation.bot_id == bot_id,
        Conversation.id.in_(
            db.query(Conversation.id).filter(
                Conversation.session_id == Conversation.session_id
            ).group_by(Conversation.session_id)
        )
    ).order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()

    return results


# =============================================
# Rating CRUD
# =============================================

def create_rating(db: Session, conversation_id: str, bot_id: str, rating: int,
                 feedback: str = None, feedback_reason: str = None) -> Rating:
    """创建评价"""
    rate = Rating(
        id=generate_id(),
        conversation_id=conversation_id,
        bot_id=bot_id,
        rating=rating,
        feedback=feedback,
        feedback_reason=feedback_reason
    )
    db.add(rate)
    db.commit()
    db.refresh(rate)
    return rate


def get_conversation_rating(db: Session, conversation_id: str) -> Optional[Rating]:
    """获取对话的评价"""
    return db.query(Rating).filter(Rating.conversation_id == conversation_id).first()


# =============================================
# BotConfiguration CRUD
# =============================================

def get_bot_config(db: Session, bot_id: str) -> Optional[BotConfiguration]:
    """获取机器人配置"""
    return db.query(BotConfiguration).filter(BotConfiguration.bot_id == bot_id).first()


def update_bot_config(db: Session, bot_id: str, **kwargs) -> Optional[BotConfiguration]:
    """更新机器人配置"""
    config = get_bot_config(db, bot_id)
    if config:
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.updated_at = datetime.now()
        db.commit()
        db.refresh(config)
    return config


# =============================================
# IndustryTemplate CRUD
# =============================================

def create_industry_template(db: Session, industry_type: str, industry_name: str,
                            description: str = None, default_categories: list = None,
                            sample_qa_pairs: list = None, recommended_chunk_size: int = 500) -> IndustryTemplate:
    """创建行业模板"""
    template = IndustryTemplate(
        id=generate_id(),
        industry_type=industry_type,
        industry_name=industry_name,
        description=description,
        default_categories=default_categories,
        sample_qa_pairs=sample_qa_pairs,
        recommended_chunk_size=recommended_chunk_size
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def get_industry_template(db: Session, industry_type: str) -> Optional[IndustryTemplate]:
    """获取行业模板"""
    return db.query(IndustryTemplate).filter(
        IndustryTemplate.industry_type == industry_type
    ).first()


def get_all_templates(db: Session) -> List[IndustryTemplate]:
    """获取所有行业模板"""
    return db.query(IndustryTemplate).all()


# =============================================
# Admin CRUD
# =============================================

def create_admin(db: Session, username: str, password_hash: str) -> Admin:
    """创建管理员"""
    from .models import Admin
    admin = Admin(
        id=generate_id(),
        username=username,
        password_hash=password_hash
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def get_admin_by_username(db: Session, username: str) -> Optional[Admin]:
    """根据用户名获取管理员"""
    return db.query(Admin).filter(Admin.username == username).first()


def get_admin_by_id(db: Session, admin_id: str) -> Optional[Admin]:
    """根据ID获取管理员"""
    return db.query(Admin).filter(Admin.id == admin_id).first()


# =============================================
# Analytics
# =============================================

def get_bot_analytics(db: Session, bot_id: str, days: int = 7) -> dict:
    """获取机器人统计数据"""
    from datetime import timedelta
    from sqlalchemy import func

    now = datetime.now()
    start_date = now - timedelta(days=days)

    # 总对话数
    total_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.bot_id == bot_id
    ).scalar()

    # 今日对话数
    today_conversations = db.query(func.count(Conversation.id)).filter(
        and_(
            Conversation.bot_id == bot_id,
            Conversation.created_at >= now - timedelta(days=1)
        )
    ).scalar()

    # 平均满意度
    avg_satisfaction = db.query(func.avg(Rating.rating)).filter(
        Rating.bot_id == bot_id
    ).scalar()

    # RAG命中率
    rag_count = db.query(func.count(Conversation.id)).filter(
        and_(
            Conversation.bot_id == bot_id,
            Conversation.source == ConversationSource.RAG
        )
    ).scalar()

    # QA匹配率
    qa_count = db.query(func.count(Conversation.id)).filter(
        and_(
            Conversation.bot_id == bot_id,
            Conversation.source == ConversationSource.QA
        )
    ).scalar()

    rag_hit_rate = (rag_count / total_conversations * 100) if total_conversations > 0 else 0
    qa_match_rate = (qa_count / total_conversations * 100) if total_conversations > 0 else 0

    # 文档数
    doc_count = db.query(func.count(Document.id)).filter(
        Document.bot_id == bot_id
    ).scalar()

    # QA对数
    qa_count_total = db.query(func.count(QAPair.id)).filter(
        and_(QAPair.bot_id == bot_id, QAPair.is_active == True)
    ).scalar()

    return {
        "total_conversations": total_conversations or 0,
        "today_conversations": today_conversations or 0,
        "avg_satisfaction": round(avg_satisfaction, 1) if avg_satisfaction else 0,
        "rag_hit_rate": round(rag_hit_rate, 1),
        "qa_match_rate": round(qa_match_rate, 1),
        "document_count": doc_count or 0,
        "qa_pair_count": qa_count_total or 0
    }


# =============================================
# 数据库会话管理
# =============================================

from contextlib import contextmanager

_session_maker = None


def get_session_maker():
    """获取SessionMaker"""
    global _session_maker
    if _session_maker is None:
        from .models import get_engine
        engine = get_engine()
        _session_maker = sessionmaker(bind=engine)
    return _session_maker


@contextmanager
def get_db_session():
    """获取数据库会话的上下文管理器"""
    maker = get_session_maker()
    session = maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

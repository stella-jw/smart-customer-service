"""
=============================================
SQLite CRUD 操作
=============================================
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import and_, or_

from .models import (
    Base, Bot, Document, QAPair, Conversation, Rating,
    BotConfiguration, IndustryTemplate, Admin, User, Team, TeamMember, BotAccess,
    BotStatus, DocumentStatus, ConversationSource, UserRole, AccessType
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


def get_conversation_history(
    db: Session,
    bot_id: str,
    session_id: str,
    max_turns: int = 5
) -> List[Dict[str, str]]:
    """
    获取指定数量的历史对话

    Args:
        db: 数据库 session
        bot_id: 机器人 ID
        session_id: 会话 ID
        max_turns: 最大轮数（每轮=用户+客服），默认 5

    Returns:
        对话历史列表，格式: [{"role": "user"/"assistant", "content": "..."}]
    """
    conversations = get_session_conversations(db, bot_id, session_id)

    # 取最近 max_turns 轮（每轮=用户+客服=2条消息）
    history = []
    for conv in reversed(conversations[-max_turns * 2:]):
        history.insert(0, {
            "role": "user" if conv.is_from_user else "assistant",
            "content": conv.message
        })
    return history


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
# User CRUD
# =============================================

def create_user(db: Session, username: str, password_hash: str, role: str = "internal") -> User:
    """创建用户"""
    from .models import User as UserModel, UserRole
    user = UserModel(
        id=generate_id(),
        username=username,
        password_hash=password_hash,
        role=UserRole(role) if isinstance(role, str) else role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session) -> List[User]:
    """获取所有用户"""
    return db.query(User).all()


# =============================================
# Team CRUD
# =============================================

def create_team(db: Session, name: str) -> Team:
    """创建团队"""
    team = Team(
        id=generate_id(),
        name=name
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_team(db: Session, team_id: str) -> Optional[Team]:
    """获取团队"""
    return db.query(Team).filter(Team.id == team_id).first()


def get_all_teams(db: Session) -> List[Team]:
    """获取所有团队"""
    return db.query(Team).all()


def update_team(db: Session, team_id: str, name: str) -> Optional[Team]:
    """更新团队"""
    team = get_team(db, team_id)
    if team:
        team.name = name
        db.commit()
        db.refresh(team)
    return team


def delete_team(db: Session, team_id: str) -> bool:
    """删除团队"""
    team = get_team(db, team_id)
    if team:
        db.delete(team)
        db.commit()
        return True
    return False


def add_team_member(db: Session, team_id: str, user_id: str) -> TeamMember:
    """添加团队成员"""
    member = TeamMember(
        team_id=team_id,
        user_id=user_id
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def remove_team_member(db: Session, team_id: str, user_id: str) -> bool:
    """移除团队成员"""
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()
    if member:
        db.delete(member)
        db.commit()
        return True
    return False


def get_user_teams(db: Session, user_id: str) -> List[Team]:
    """获取用户所属的团队"""
    memberships = db.query(TeamMember).filter(TeamMember.user_id == user_id).all()
    team_ids = [m.team_id for m in memberships]
    return db.query(Team).filter(Team.id.in_(team_ids)).all() if team_ids else []


def get_team_members(db: Session, team_id: str) -> List[User]:
    """获取团队的所有成员"""
    memberships = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    user_ids = [m.user_id for m in memberships]
    return db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []


# =============================================
# BotAccess CRUD
# =============================================

def get_bot_access(db: Session, bot_id: str) -> Optional[BotAccess]:
    """获取机器人访问配置"""
    return db.query(BotAccess).filter(BotAccess.bot_id == bot_id).first()


def create_or_update_bot_access(db: Session, bot_id: str, access_type: str,
                                allowed_users: list = None, allowed_teams: list = None) -> BotAccess:
    """创建或更新机器人访问配置"""
    from .models import AccessType
    access = get_bot_access(db, bot_id)
    if access:
        access.access_type = AccessType(access_type) if isinstance(access_type, str) else access_type
        access.allowed_users = allowed_users or []
        access.allowed_teams = allowed_teams or []
        access.updated_at = datetime.now()
    else:
        access = BotAccess(
            bot_id=bot_id,
            access_type=AccessType(access_type) if isinstance(access_type, str) else access_type,
            allowed_users=allowed_users or [],
            allowed_teams=allowed_teams or []
        )
        db.add(access)
    db.commit()
    db.refresh(access)
    return access


def check_user_bot_access(db: Session, user_id: str, team_ids: list, bot_id: str) -> bool:
    """检查用户是否有权访问指定机器人"""
    from .models import AccessType
    access = get_bot_access(db, bot_id)
    if not access or access.access_type == AccessType.ALL:
        return True
    if access.access_type == AccessType.SPECIFIC_USERS:
        return user_id in (access.allowed_users or [])
    if access.access_type == AccessType.SPECIFIC_TEAMS:
        return any(tid in (access.allowed_teams or []) for tid in team_ids)
    return False


def get_accessible_bots(db: Session, user_id: str = None, team_ids: list = None,
                        is_anonymous: bool = False) -> List[Bot]:
    """获取用户可访问的机器人列表"""
    from .models import AccessType
    all_bots = db.query(Bot).filter(Bot.status == BotStatus.ACTIVE).all()
    if is_anonymous:
        # 匿名用户只能访问默认机器人
        return [b for b in all_bots if b.is_default]
    if not user_id:
        return all_bots
    accessible = []
    for bot in all_bots:
        if check_user_bot_access(db, user_id, team_ids or [], bot.id):
            accessible.append(bot)
    return accessible


# =============================================
# Analytics
# =============================================

def get_bot_analytics(db: Session, bot_id: str, days: int = 7) -> dict:
    """获取机器人统计数据"""
    from datetime import timedelta
    from sqlalchemy import func

    now = datetime.now()
    start_date = now - timedelta(days=days)

    # 总对话数（按session_id去重）
    total_conversations = db.query(func.count(func.distinct(Conversation.session_id))).filter(
        Conversation.bot_id == bot_id
    ).scalar()

    # 今日对话数（按session_id去重）
    today_conversations = db.query(func.count(func.distinct(Conversation.session_id))).filter(
        and_(
            Conversation.bot_id == bot_id,
            Conversation.created_at >= now - timedelta(days=1)
        )
    ).scalar()

    # 平均满意度（只统计近期的评分，转换为百分比）
    # 5星=100%, 4星=80%, 3星=60%, 2星=40%, 1星=20%
    avg_rating = db.query(func.avg(Rating.rating)).filter(
        and_(
            Rating.bot_id == bot_id,
            Rating.created_at >= start_date
        )
    ).scalar()
    avg_satisfaction = (avg_rating * 20) if avg_rating else 0

    # RAG命中数（消息数）
    rag_count = db.query(func.count(Conversation.id)).filter(
        and_(
            Conversation.bot_id == bot_id,
            Conversation.source == ConversationSource.RAG
        )
    ).scalar()

    # QA匹配数（消息数）
    qa_count = db.query(func.count(Conversation.id)).filter(
        and_(
            Conversation.bot_id == bot_id,
            Conversation.source == ConversationSource.QA
        )
    ).scalar()

    # 总消息数（作为命中率的分母）
    total_messages = db.query(func.count(Conversation.id)).filter(
        Conversation.bot_id == bot_id
    ).scalar()

    rag_hit_rate = (rag_count / total_messages * 100) if total_messages > 0 else 0
    qa_match_rate = (qa_count / total_messages * 100) if total_messages > 0 else 0

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
# System Prompt
# =============================================

DEFAULT_SYSTEM_PROMPTS = {
    "general": {
        "friendly": "你是一个热情友好的智能客服助手，始终以积极的态度帮助用户解决问题。你的目标是让每位用户都感到受到尊重和重视。",
        "professional": "你是一个专业严谨的智能客服助手，回答问题时条理清晰、言简意赅。你的目标是高效准确地解决用户问题。",
        "humorous": "你是一个幽默风趣的智能客服助手，在保持专业的同时会用轻松的方式缓解用户的焦虑。",
        "empathetic": "你是一个富有同理心的智能客服助手，善于理解用户的情感需求，给予温暖和关怀的回应。"
    },
    "ecommerce": {
        "friendly": "你是一家电商平台的热情客服助手，熟悉各类商品特点。你应该友好地与顾客交流，帮助他们找到满意的商品，耐心解答购物过程中的疑问。",
        "professional": "你是一家电商平台的专业客服助手，精通商品知识、订单处理和售后流程。你的回答应该准确，专业，高效。",
        "humorous": "你是电商平台的幽默客服，能在推荐商品和处理问题时带来轻松愉快的氛围，让购物体验更有趣。",
        "empathetic": "你深度理解购物者的需求和担忧，无论是选择困难还是售后问题，都能给予充分的理解和贴心的建议。"
    },
    "medical": {
        "friendly": "你是一家医疗机构的专业客服助手，熟悉常见健康问题和医疗流程。请以亲切的态度回答用户的健康咨询，引导他们获得合适的医疗服务。",
        "professional": "你是一位医疗领域的专业客服，具备扎实的医学知识。你的回答应该严谨准确，帮助用户正确理解健康信息。",
        "humorous": "虽然医疗话题严肃，但你可以用温和的幽默缓解用户的紧张情绪，让沟通更加轻松。",
        "empathetic": "你理解用户在健康问题上的焦虑，会给予充分的倾听和温暖的回应，同时引导专业医疗建议。"
    },
    "it": {
        "friendly": "你是一家IT公司的技术支持客服，擅长用通俗易懂的语言解释技术问题。你的服务态度热情耐心，让技术问题不再令人头疼。",
        "professional": "你是一位资深技术支持工程师，技术功底扎实。你的回答应该准确，专业，能够快速定位和解决各类技术问题。",
        "humorous": "你是IT界的幽默技术顾问，bug和宕机都不是事儿，用轻松的方式化解技术麻烦。",
        "empathetic": "你理解技术人员和非技术用户在面对IT问题时的困惑和压力，给予耐心的指导和情绪支持。"
    },
    "saas": {
        "friendly": "你是SaaS产品的友好客服助手，熟悉产品功能和常见问题。你应该帮助用户快速上手，提供愉快的使用体验。",
        "professional": "你是SaaS产品的专业客服专家，精通产品功能和最佳实践，帮助企业用户充分发挥产品价值。",
        "humorous": "你是SaaS界的幽默顾问，让枯燥的功能介绍变得生动有趣。",
        "empathetic": "你理解企业用户在选型和使用过程中的顾虑，提供贴心、专业的建议。"
    }
}


def get_default_system_prompt(industry_type: str, personality: str) -> str:
    """获取指定行业和人格的默认系统提示词"""
    industry_prompts = DEFAULT_SYSTEM_PROMPTS.get(industry_type, DEFAULT_SYSTEM_PROMPTS["general"])
    return industry_prompts.get(personality, industry_prompts["friendly"])


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

"""
=============================================
SQLite 数据库模块
=============================================
"""

from .models import (
    Base, Bot, Document, QAPair, Conversation, Rating,
    BotConfiguration, IndustryTemplate, Admin, User, Team, TeamMember, BotAccess,
    BotStatus, DocumentStatus, ConversationSource, UserRole, AccessType,
    get_engine, init_database, DATABASE_PATH
)
from .crud import (
    generate_id,
    get_db_session,
    # Bot
    create_bot, get_bot, get_all_bots, update_bot, delete_bot,
    # Document
    create_document, get_document, get_bot_documents, update_document, delete_document,
    # QAPair
    create_qa_pair, get_qa_pair, get_bot_qa_pairs, update_qa_pair, delete_qa_pair,
    increment_qa_usage, update_qa_satisfaction,
    # Conversation
    create_conversation, get_conversation, get_session_conversations, get_user_sessions,
    # Rating
    create_rating, get_conversation_rating,
    # Config
    get_bot_config, update_bot_config,
    # Template
    create_industry_template, get_industry_template, get_all_templates,
    # Analytics
    get_bot_analytics,
    # Admin
    create_admin, get_admin_by_username, get_admin_by_id,
    # User
    create_user, get_user_by_username, get_user_by_id, get_all_users,
    # Team
    create_team, get_team, get_all_teams, update_team, delete_team,
    add_team_member, remove_team_member, get_user_teams, get_team_members,
    # BotAccess
    get_bot_access, create_or_update_bot_access, check_user_bot_access, get_accessible_bots
)

__all__ = [
    "Base", "Bot", "Document", "QAPair", "Conversation", "Rating",
    "BotConfiguration", "IndustryTemplate", "Admin", "User", "Team", "TeamMember", "BotAccess",
    "BotStatus", "DocumentStatus", "ConversationSource", "UserRole", "AccessType",
    "get_engine", "init_database", "DATABASE_PATH",
    "generate_id",
    "create_bot", "get_bot", "get_all_bots", "update_bot", "delete_bot",
    "create_document", "get_document", "get_bot_documents", "update_document", "delete_document",
    "create_qa_pair", "get_qa_pair", "get_bot_qa_pairs", "update_qa_pair", "delete_qa_pair",
    "increment_qa_usage", "update_qa_satisfaction",
    "create_conversation", "get_conversation", "get_session_conversations", "get_user_sessions",
    "create_rating", "get_conversation_rating",
    "get_bot_config", "update_bot_config",
    "create_industry_template", "get_industry_template", "get_all_templates",
    "get_bot_analytics",
    "create_admin", "get_admin_by_username", "get_admin_by_id",
    "create_user", "get_user_by_username", "get_user_by_id", "get_all_users",
    "create_team", "get_team", "get_all_teams", "update_team", "delete_team",
    "add_team_member", "remove_team_member", "get_user_teams", "get_team_members",
    "get_bot_access", "create_or_update_bot_access", "check_user_bot_access", "get_accessible_bots"
]

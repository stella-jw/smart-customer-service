"""
=============================================
客服系统状态定义
=============================================
"""

from typing import TypedDict, Optional, List, Dict, Any
from enum import Enum


class QuerySource(str, Enum):
    """回答来源"""
    RAG = "rag"          # 知识库检索
    QA = "qa"            # QA对匹配
    LLM = "llm"          # 纯LLM闲聊
    FALLBACK = "fallback" # 兜底回复


class Intent(str, Enum):
    """用户意图"""
    GREETING = "greeting"          # 问候
    QUESTION = "question"          # 咨询问题
    COMPLAINT = "complaint"        # 投诉
    CHITCHAT = "chitchat"          # 闲聊
    CLARIFICATION = "clarification" # 澄清


class CustomerServiceState(TypedDict):
    """客服系统状态定义"""

    # 原始输入
    user_input: str
    session_id: str
    user_id: Optional[str]
    bot_id: str

    # 分类结果
    intent: Intent
    confidence: float

    # QA匹配结果
    matched_qa_id: Optional[str]
    matched_qa_question: Optional[str]
    matched_qa_answer: Optional[str]
    qa_match_score: float

    # RAG检索结果
    retrieved_chunks: List[Dict[str, Any]]
    rag_top_k: int

    # 生成结果
    generated_response: str
    final_response: str

    # 上下文
    conversation_history: List[Dict[str, str]]  # [{"role": "user/assistant", "content": str}]
    context_turns: int

    # 配置
    bot_config: Dict[str, Any]

    # 来源标识
    source: QuerySource

    # 引用
    reference_doc_id: Optional[str]
    reference_qa_id: Optional[str]


def create_initial_state(
    user_input: str,
    session_id: str,
    bot_id: str,
    user_id: Optional[str] = None,
    bot_config: Optional[Dict[str, Any]] = None
) -> CustomerServiceState:
    """创建初始状态"""

    default_config = {
        "welcome_message": "您好！有什么可以帮您的？",
        "opening_message": "请问有什么可以帮您？",
        "fallback_message": "抱歉，我没有找到相关答案，请联系人工客服获取帮助。",
        "timeout_message": "抱歉，我没有及时回复，请稍后再试。",
        "personality": "friendly",
        "response_tone": "friendly",
        "enable_rag": True,
        "enable_qa_match": True,
        "enable_chitchat": True,
        "rag_top_k": 5,
        "qa_match_threshold": 0.85
    }

    if bot_config:
        default_config.update(bot_config)

    return CustomerServiceState(
        user_input=user_input,
        session_id=session_id,
        user_id=user_id,
        bot_id=bot_id,
        intent=Intent.QUESTION,
        confidence=0.0,
        matched_qa_id=None,
        matched_qa_question=None,
        matched_qa_answer=None,
        qa_match_score=0.0,
        retrieved_chunks=[],
        rag_top_k=default_config.get("rag_top_k", 5),
        generated_response="",
        final_response="",
        conversation_history=[],
        context_turns=0,
        bot_config=default_config,
        source=QuerySource.LLM,
        reference_doc_id=None,
        reference_qa_id=None
    )

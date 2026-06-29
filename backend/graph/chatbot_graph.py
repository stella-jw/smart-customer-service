"""
=============================================
智能客服 LangGraph 工作流
=============================================

工作流图 (融合检索版):
    START → classify_intent → route_intent
                                  ↓
              ┌───────────────────┼───────────────────┐
              ↓                   ↓                   ↓
          greeting            question            chitchat/complaint
              ↓                   ↓                   ↓
              │                   ↓                   │
              │         ┌───────┴───────┐           │
              │         ↓               ↓           │
              │   fusion_retrieve    generate        │
              │         ↓               ↓           │
              │         └──────►respond◄────────────┘
              │                   ↓
                               END

融合检索:
    question → fusion_retrieve (向量+关键词+QA并行) → generate → respond
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END

from .state import CustomerServiceState, QuerySource, Intent, create_initial_state
from .nodes import classify_intent, fusion_retrieve, generate_response, respond


def route_intent(state: CustomerServiceState) -> str:
    """
    根据意图路由到不同分支
    """
    intent = state.get("intent", Intent.QUESTION)

    if intent == Intent.GREETING:
        return "greeting"
    elif intent == Intent.QUESTION:
        return "question"
    else:
        # complaint, chitchat, clarification 都走通用流程
        return "other"


def route_question_source(state: CustomerServiceState) -> str:
    """
    在 question 分支后，判断走 QA 还是 RAG 路径

    策略:
    1. 先进行 QA 语义匹配 (已在question_node前执行)
    2. 如果 QA 匹配分数 > 阈值，直接返回 QA 答案
    3. 否则走 RAG 检索路径
    """
    qa_score = state.get("qa_match_score", 0.0)
    threshold = state.get("bot_config", {}).get("qa_match_threshold", 0.85)

    if qa_score >= threshold:
        return "qa_match"
    else:
        return "rag_retrieve"


def create_chatbot_graph() -> StateGraph:
    """创建客服工作流图"""

    # 创建图构建器
    workflow = StateGraph(CustomerServiceState)

    # 添加节点
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("fusion_retrieve", fusion_retrieve)
    workflow.add_node("generate", generate_response)
    workflow.add_node("respond", respond)

    # 设置入口点
    workflow.set_entry_point("classify_intent")

    # 意图路由函数
    def route_by_intent(state: CustomerServiceState) -> str:
        """根据意图路由"""
        intent = state.get("intent", Intent.QUESTION)
        if intent == Intent.GREETING:
            return "greeting"
        elif intent == Intent.QUESTION:
            return "question"
        else:
            return "other"

    # 条件边：意图分类后路由
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "greeting": "respond",
            "question": "fusion_retrieve",
            "other": "generate"
        }
    )

    # fusion_retrieve后生成并回复
    workflow.add_edge("fusion_retrieve", "generate")
    workflow.add_edge("generate", "respond")

    # 结束
    workflow.add_edge("respond", END)

    return workflow


# 创建编译后的图
_chatbot_graph = None


def get_chatbot_graph() -> StateGraph:
    """获取编译后的聊天机器人图"""
    global _chatbot_graph
    if _chatbot_graph is None:
        _chatbot_graph = create_chatbot_graph().compile()
    return _chatbot_graph


def chat(
    user_input: str,
    session_id: str,
    bot_id: str,
    user_id: str = None,
    bot_config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    执行聊天流程

    Args:
        user_input: 用户输入
        session_id: 会话ID
        bot_id: 机器人ID
        user_id: 用户ID（可选）
        bot_config: 机器人配置（可选）

    Returns:
        {
            "response": str,  # 最终回复
            "source": str,    # 来源: rag/qa/llm/fallback
            "intent": str,     # 意图
            "confidence": float,  # 置信度
            "reference_doc_id": str,  # 引用的文档ID
            "reference_qa_id": str   # 引用的QA对ID
        }
    """
    # 获取对话历史
    max_history_turns = 5
    if bot_config and "max_history_turns" in bot_config:
        max_history_turns = bot_config["max_history_turns"]

    from ..db.sqlite.crud import get_conversation_history, get_db_session
    conversation_history = []
    try:
        with get_db_session() as db:
            conversation_history = get_conversation_history(
                db=db,
                bot_id=bot_id,
                session_id=session_id,
                max_turns=max_history_turns
            )
    except Exception as e:
        print(f"[chat] 获取对话历史失败: {e}")

    # 创建初始状态
    initial_state = create_initial_state(
        user_input=user_input,
        session_id=session_id,
        bot_id=bot_id,
        user_id=user_id,
        bot_config=bot_config,
        conversation_history=conversation_history,
        context_turns=len(conversation_history) // 2  # 每轮=2条消息
    )

    # 执行图
    graph = get_chatbot_graph()
    result_state = graph.invoke(initial_state)

    print(f"[DEBUG chat] result_state keys: {result_state.keys()}")
    print(f"[DEBUG chat] final_response: '{result_state.get('final_response', '')}'")
    print(f"[DEBUG chat] source: {result_state.get('source')}")
    print(f"[DEBUG chat] matched_qa_answer: '{result_state.get('matched_qa_answer', '')}'")

    return {
        "response": result_state.get("final_response", ""),
        "source": result_state.get("source", QuerySource.LLM).value,
        "intent": result_state.get("intent", Intent.QUESTION).value,
        "confidence": result_state.get("confidence", 0.0),
        "reference_doc_id": result_state.get("reference_doc_id"),
        "reference_qa_id": result_state.get("reference_qa_id"),
        "matched_qa_question": result_state.get("matched_qa_question"),
        "retrieved_chunks": result_state.get("retrieved_chunks", [])
    }

"""
=============================================
回复节点
=============================================
"""

from typing import Dict, Any
from ..state import CustomerServiceState, Intent, QuerySource


def respond(state: CustomerServiceState) -> CustomerServiceState:
    """
    最终回复节点

    1. 整合所有处理结果
    2. 应用机器人配置(欢迎语/超时回复等)
    3. 返回最终响应
    """
    bot_config = state.get("bot_config", {})
    intent = state.get("intent", Intent.QUESTION)
    source = state.get("source", QuerySource.LLM)

    print(f"[DEBUG respond] source={source}, type={type(source)}, matched_qa_answer={state.get('matched_qa_answer')}")

    # 处理特殊意图的回复
    if intent == Intent.GREETING:
        response = bot_config.get(
            "welcome_message",
            "您好！有什么可以帮您的？"
        )
    elif intent == Intent.COMPLAINT:
        # 投诉要有同理心
        complaint_response = state.get("generated_response", "")
        response = f"非常抱歉给您带来不好的体验。{complaint_response}"
    elif intent == Intent.CHITCHAT:
        response = state.get(
            "generated_response",
            "很高兴与您交流！还有什么问题吗？"
        )
    elif intent == Intent.CLARIFICATION:
        response = state.get(
            "generated_response",
            "关于您的问题，我需要更多信息来帮助您。请详细描述一下您的情况。"
        )
    else:
        # 先检查QA匹配结果（QA优先于RAG）
        matched_answer = state.get("matched_qa_answer", "")
        print(f"[DEBUG respond] matched_answer from state: '{matched_answer}'")
        if matched_answer:
            response = matched_answer
        else:
            response = state.get("generated_response", "")

    # 如果没有生成任何回复，使用兜底消息
    if not response:
        response = bot_config.get(
            "fallback_message",
            "抱歉，我没有找到相关答案，请联系人工客服获取帮助。"
        )

    print(f"[DEBUG respond] final response: '{response}'")
    return {
        "final_response": response
    }

"""
=============================================
LLM生成节点
=============================================
"""

import json
from typing import Dict, Any
from ..state import CustomerServiceState, QuerySource
import config as cfg


def generate_response(state: CustomerServiceState) -> CustomerServiceState:
    """
    LLM生成节点

    根据不同来源生成回复:
    1. RAG: 基于检索到的文档片段生成回答
    2. QA: 直接使用QA答案(可加适当润色)
    3. LLM: 纯闲聊生成
    """
    source = state.get("source", QuerySource.LLM)
    bot_config = state.get("bot_config", {})
    user_input = state["user_input"]

    tone = bot_config.get("response_tone", "friendly")
    personality = bot_config.get("personality", "friendly")

    # 获取系统提示词
    system_prompt = bot_config.get("system_prompt", "")
    if not system_prompt:
        # 如果没有配置系统提示词，使用基于人格的默认提示词
        from ...db.sqlite.crud import get_default_system_prompt
        industry_type = bot_config.get("industry_type", "general")
        system_prompt = get_default_system_prompt(industry_type, personality)

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatOpenAI(
            api_key=cfg.MINIMAX_API_KEY,
            base_url=cfg.MINIMAX_BASE_URL,
            model=cfg.MINIMAX_MODEL_NAME,
            temperature=0.7
        )

        if source == QuerySource.RAG:
            # RAG模式: 基于上下文生成
            context = "\n".join([
                f"- {chunk['content']}"
                for chunk in state["retrieved_chunks"]
            ])

            user_prompt = f"""基于以下知识库内容，回答用户问题。如果内容不足以回答，请说明"根据现有资料..."。

知识库内容:
{context}

用户问题: {user_input}

回答要求:
- 简洁明了，突出关键信息
- 如果涉及具体数据或步骤，请准确引用
"""

        elif source == QuerySource.QA:
            # QA模式: 直接使用答案
            user_prompt = f"""请将以下回答润色成自然的客服回复语气。

原始回答: {state['matched_qa_answer']}

用户问题: {user_input}
"""

        else:
            # 兜底回复或闲聊
            if bot_config.get("enable_chitchat", True):
                user_prompt = f"""请生成一个友好的客服回复。

用户问题: {user_input}
"""
            else:
                user_prompt = f"""请生成一个简洁的回复，引导用户提出具体问题。

用户问题: {user_input}
"""

        # 调用 LLM，传入系统提示词
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)

        return {
            "generated_response": response.content
        }

    except Exception as e:
        print(f"Generate response error: {e}")
        return {
            "generated_response": bot_config.get(
                "fallback_message",
                "抱歉，我没有找到相关答案，请联系人工客服获取帮助。"
            )
        }

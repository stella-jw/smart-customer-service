"""
=============================================
意图分类节点
=============================================
"""

import json
from typing import Dict, Any
from ..state import CustomerServiceState, Intent


def classify_intent(state: CustomerServiceState) -> CustomerServiceState:
    """
    意图分类节点

    使用 LLM 分析用户输入，判断:
    1. 意图类型 (greeting/question/complaint/chitchat/clarification)
    2. 置信度评估
    """
    user_input = state["user_input"]
    bot_config = state.get("bot_config", {})

    # 构建分类prompt
    prompt = f"""你是一个客服意图分类器。请分析用户输入，判断其意图类型。

用户输入: {user_input}

意图类型定义:
- greeting: 问候、打招呼、开始对话（如"你好"、"在吗"、"嗨"）
- question: 咨询问题、需要知识库回答（如"产品怎么使用"、"价格多少"）
- complaint: 投诉、抱怨、表达不满（如"太慢了"、"质量太差"）
- chitchat: 闲聊、寒暄、无特定目的（如"今天天气不错"）
- clarification: 要求澄清、追问（如"你说的XX是什么意思"）

判断规则:
1. 如果用户输入是问候语(你好/在吗/嗨/早上好等) → greeting
2. 如果用户询问产品/服务/技术问题 → question
3. 如果用户表达不满/抱怨/投诉 → complaint
4. 如果用户只是在聊天/寒暄/无明确目的 → chitchat
5. 如果用户要求解释之前回答/追问 → clarification

请以JSON格式返回:
{{"intent": "类型", "confidence": 0.0-1.0, "reasoning": "判断理由"}}
"""

    try:
        from langchain_openai import ChatOpenAI
        import config as cfg

        llm = ChatOpenAI(
            api_key=cfg.MINIMAX_API_KEY,
            base_url=cfg.MINIMAX_BASE_URL,
            model=cfg.MINIMAX_MODEL_NAME,
            temperature=0.1
        )

        response = llm.invoke(prompt)
        result = json.loads(response.content)

        intent_str = result.get("intent", "question").lower()
        confidence = result.get("confidence", 0.5)

        # 映射意图字符串到枚举
        intent_mapping = {
            "greeting": Intent.GREETING,
            "question": Intent.QUESTION,
            "complaint": Intent.COMPLAINT,
            "chitchat": Intent.CHITCHAT,
            "clarification": Intent.CLARIFICATION
        }

        intent = intent_mapping.get(intent_str, Intent.QUESTION)

    except Exception as e:
        print(f"Intent classification error: {e}")
        intent = Intent.QUESTION
        confidence = 0.5

    return {
        "intent": intent,
        "confidence": confidence
    }

"""
=============================================
LLM生成节点
=============================================
"""

import json
from typing import Dict, Any, List
from ..state import CustomerServiceState, QuerySource
import config as cfg


def format_history_context(history: List[Dict[str, str]]) -> str:
    """
    格式化对话历史为字符串

    Args:
        history: 对话历史 [{"role": "user"/"assistant", "content": "..."}]

    Returns:
        格式化后的字符串
    """
    if not history:
        return ""

    lines = []
    for msg in history:
        role = "用户" if msg.get("role") == "user" else "客服"
        lines.append(f"{role}: {msg.get('content', '')}")

    return "\n".join(lines)


def truncate_history_by_tokens(
    history: List[Dict[str, str]],
    max_tokens: int = 1500
) -> List[Dict[str, str]]:
    """
    根据 token 数量截断历史记录

    Args:
        history: 对话历史
        max_tokens: 最大 token 数（默认 1500）

    Returns:
        截断后的历史
    """
    if not history:
        return []

    # 粗略估算：中文约 2 字符/token，英文约 4 字符/token
    def estimate_tokens(text: str) -> int:
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return chinese_chars // 2 + other_chars // 4

    total_tokens = sum(estimate_tokens(msg.get('content', '')) for msg in history)

    if total_tokens <= max_tokens:
        return history

    # 从最旧的开始截断
    truncated = []
    current_tokens = 0
    for msg in reversed(history):
        msg_tokens = estimate_tokens(msg.get('content', ''))
        if current_tokens + msg_tokens > max_tokens:
            break
        truncated.insert(0, msg)
        current_tokens += msg_tokens

    return truncated


def is_factual_question(text: str) -> bool:
    """
    判断是否为事实性问题

    Args:
        text: 用户问题

    Returns:
        True 如果是事实性问题
    """
    # 问词特征
    question_words = ["谁", "什么", "哪些", "哪个", "何时", "哪里", "多少", "怎么", "为什么", "是否"]

    # 实体特征（简化判断）
    entity_indicators = ["的", "作者", "作品", "诗人", "公司", "产品", "价格", "地址", "电话", "版本"]

    has_question_word = any(word in text for word in question_words)
    has_entity = any(word in text for word in entity_indicators)

    # 包含问词或实体特征即为事实性问题
    return has_question_word or has_entity


def generate_response(state: CustomerServiceState) -> CustomerServiceState:
    """
    LLM生成节点

    根据不同来源生成回复:
    1. RAG: 基于检索到的文档片段生成回答
    2. QA: 直接使用QA答案(可加适当润色)
    3. FALLBACK: 判断是否允许 LLM 知识补全
    """
    source = state.get("source", QuerySource.LLM)
    bot_config = state.get("bot_config", {})
    user_input = state["user_input"]

    # 获取对话历史并截断
    history = state.get("conversation_history", [])
    history = truncate_history_by_tokens(history, max_tokens=1500)
    history_context = format_history_context(history)

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

            if history_context:
                user_prompt = f"""【对话历史】
{history_context}

基于以下知识库内容，回答用户问题。如果内容不足以回答，请说明"根据现有资料..."。

知识库内容:
{context}

用户问题: {user_input}

回答要求:
- 简洁明了，突出关键信息
- 如果涉及具体数据或步骤，请准确引用
"""
            else:
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
            if history_context:
                user_prompt = f"""【对话历史】
{history_context}

请将以下回答润色成自然的客服回复语气。

原始回答: {state['matched_qa_answer']}

用户问题: {user_input}
"""
            else:
                user_prompt = f"""请将以下回答润色成自然的客服回复语气。

原始回答: {state['matched_qa_answer']}

用户问题: {user_input}
"""

        else:
            # FALLBACK: 判断是否为事实性问题，允许 LLM 用知识回答
            if is_factual_question(user_input):
                if history_context:
                    user_prompt = f"""【对话历史】
{history_context}

以下问题无法从知识库找到答案，请基于你的知识回答。
如果不确定，请说"这个我不太确定，建议联系人工客服"。
重要：回答时提示用户"以下仅供参考，实际情况请以官方为准"。

用户问题: {user_input}"""
                else:
                    user_prompt = f"""以下问题无法从知识库找到答案，请基于你的知识回答。
如果不确定，请说"这个我不太确定，建议联系人工客服"。
重要：回答时提示用户"以下仅供参考，实际情况请以官方为准"。

用户问题: {user_input}"""
            else:
                # 非事实性问题，保持 fallback
                if bot_config.get("enable_chitchat", True):
                    if history_context:
                        user_prompt = f"""【对话历史】
{history_context}

请生成一个友好的客服回复，引导用户提供更多具体信息以便更好地帮助他们。

用户问题: {user_input}"""
                    else:
                        user_prompt = f"""请生成一个友好的客服回复，引导用户提供更多具体信息以便更好地帮助他们。

用户问题: {user_input}"""
                else:
                    user_prompt = f"""请生成一个简洁的回复，引导用户联系人工客服获取帮助。

用户问题: {user_input}"""

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

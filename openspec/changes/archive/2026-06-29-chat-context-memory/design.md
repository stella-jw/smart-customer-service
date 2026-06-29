## Context

当前 RAG 检索系统将每个用户问题作为独立查询处理。在 `generate_response` 节点中，LLM 仅接收当前用户问题 `user_input`，不包含任何对话历史。这导致以下问题：

```
问: "《所见》的作者是谁？"
答: "袁枚"

问: "内容是什么？"  ← 系统只看到"内容是什么？"
答: "抱歉，我不知道你在问什么内容"

问: "作者还有哪些其它作品？"  ← 系统不知道"作者"指谁
答: "抱歉，我不知道你在问哪位作者"
```

现有系统已有对话存储能力（`conversations` 表），但 `generate_response` 节点未利用这些历史数据。

**另一个问题：** 当 RAG/QA 检索未命中时，系统直接返回 fallback 消息，放弃使用 LLM 自身的知识。例如问"《所见》的作者还写过哪些诗？"，知识库可能没有答案，但 LLM 训练数据中可能有袁枚的相关作品信息。

## Goals / Non-Goals

**Goals:**
- 实现多轮对话上下文管理，用户追问可以被正确理解
- 在 `generate_response` 节点加入历史对话上下文
- 控制上下文长度（token 限制），避免超出 LLM 窗口
- RAG/QA 未命中时，允许 LLM 用自身知识回答事实性问题
- 保持向后兼容：单轮对话、无历史记录时照常工作

**Non-Goals:**
- 不实现跨 session 的用户记忆（用户画像等）
- 不修改现有的 RAG/QA 检索逻辑（仅生成环节变化）
- 不实现 Function Calling / Tool Use
- 不做实时知识查询（依赖 LLM 自身知识，非实时 API）

## Decisions

### 1. 上下文获取时机

**选择:** 在 `chatbot_graph.py` 的 `chat()` 函数中获取历史消息

**理由:**
- `chat()` 是入口点，可以统一获取历史后传递给整个图
- 避免在多个节点重复查询数据库
- 后续节点（classify、qa_match 等）可能也需要历史上下文

### 2. 上下文格式

**选择:** 格式化为字符串，插入到 system_prompt 或 user_prompt 中

```
【对话历史】
用户: 《所见》的作者是谁？
客服: 《所见》是清代诗人袁枚创作的一首五言绝句...

用户: 内容是什么？
客服: 这首诗描写的是...
```

**理由:**
- 实现简单，不需要修改 LangChain message 结构
- 灵活控制长度，可截断或限制轮数
- LLM 可以直接理解这种格式

### 3. 上下文轮数控制

**选择:** 默认取最近 5 轮对话（用户+客服=1轮），可配置

**理由:**
- 5 轮足够覆盖大多数追问场景
- 避免超出 token 限制
- 可通过配置项 `max_history_turns` 控制

### 4. Token 限制

**选择:** 粗略估算 + 截断

**理由:**
- 精确计算 token 需要额外调用编码器，开销大
- 粗略估算：中文约 2 字符/token，英文约 4 字符/token
- 预留 500 token 给当前问题和生成内容

### 5. LLM 知识补全（Fallback 增强）

**选择:** 当 RAG/QA 未命中时，区分事实性和非事实性问题

**事实性问题判断逻辑：**
```
问: "《所见》的作者还写过哪些诗？"
特征: 问"谁"、"什么"、"哪些"、"何时"等 → 可能是事实性问题
      涉及具体人物、作品、地点等 → 事实性

LLM 自身知识可以回答 → 生成回答 + 提示"以下仅供参考"
```

**非事实性问题：**
```
问: "你觉得我应该买哪个？"
特征: 问"建议"、"推荐"、"看法"等 → 非事实性
      涉及主观判断 → 保持 fallback
```

**Prompt 模板：**
```python
if is_factual_question(user_input):
    user_prompt = f"""以下问题无法从知识库找到答案，请基于你的知识回答。
如果不确定，请说"这个我不太确定，建议联系人工客服"。
重要：回答时提示用户"以下仅供参考，实际情况请以官方为准"。

用户问题: {user_input}"""
else:
    user_prompt = "请生成简洁回复，引导用户联系人工客服获取帮助。"
```

## Implementation

### 修改 `chatbot_graph.py`

```python
def chat(
    user_input: str,
    session_id: str,
    bot_id: str,
    user_id: str = None,
    bot_config: Dict[str, Any] = None
) -> Dict[str, Any]:
    # 获取对话历史
    history_turns = bot_config.get("max_history_turns", 5) if bot_config else 5
    conversation_history = get_conversation_history(
        bot_id=bot_id,
        session_id=session_id,
        max_turns=history_turns
    )

    # 创建初始状态，包含历史
    initial_state = create_initial_state(
        user_input=user_input,
        session_id=session_id,
        bot_id=bot_id,
        user_id=user_id,
        bot_config=bot_config,
        conversation_history=conversation_history  # 新增
    )
    ...
```

### 修改 `state.py`

```python
class CustomerServiceState(TypedDict):
    ...
    conversation_history: Optional[List[Dict]]  # 新增: [{"role": "user", "content": "..."}, ...]
```

### 修改 `generate.py`

```python
def generate_response(state: CustomerServiceState) -> CustomerServiceState:
    ...
    source = state.get("source", QuerySource.LLM)

    # 构建带上下文的 prompt
    history_context = format_history_context(state.get("conversation_history", []))

    if source == QuerySource.RAG:
        user_prompt = f"""【对话历史】
{history_context}

基于以下知识库内容，回答用户问题。

知识库内容:
{context}

用户问题: {user_input}
"""
    elif source == QuerySource.QA:
        # QA 命中...
    else:
        # Fallback: 判断是否为事实性问题
        if is_factual_question(state["user_input"]):
            user_prompt = f"""以下问题无法从知识库找到答案，请基于你的知识回答。
如果不确定，请说"这个我不太确定，建议联系人工客服"。
重要：回答时提示用户"以下仅供参考，实际情况请以官方为准"。

用户问题: {user_input}"""
        else:
            user_prompt = "请生成简洁回复，引导用户联系人工客服获取帮助。"

def is_factual_question(text: str) -> bool:
    """简单判断是否为事实性问题"""
    # 问词特征
    question_words = ["谁", "什么", "哪些", "哪个", "何时", "哪里", "多少", "怎么"]
    # 实体特征（简化判断）
    entity_indicators = ["的", "作者", "作品", "诗人", "公司", "产品", "价格"]

    has_question_word = any(word in text for word in question_words)
    has_entity = any(word in text for word in entity_indicators)

    return has_question_word or has_entity
```

### 新增 `backend/db/sqlite/crud.py`

```python
def get_conversation_history(
    db: Session,
    bot_id: str,
    session_id: str,
    max_turns: int = 5
) -> List[Dict[str, str]]:
    """获取指定数量的历史对话"""
    conversations = get_session_conversations(db, bot_id, session_id)

    # 取最近 max_turns 轮（每轮=用户+客服）
    history = []
    for conv in reversed(conversations[-max_turns * 2:]):
        history.insert(0, {
            "role": "user" if conv.is_from_user else "assistant",
            "content": conv.message
        })
    return history
```

## Risks / Trade-offs

[Risk] Token 超出限制 → **Mitigation:** 粗略估算 + 截断，预留 buffer

[Risk] 历史消息过多影响 LLM 理解 → **Mitigation:** 限制 max_turns=5，优先保留最近对话

[Risk] 跨session混淆 → **Mitigation:** 按 session_id 隔离查询

[Risk] LLM 幻觉回答事实性问题 → **Mitigation:** 提示用户"仅供参考"，建议核实

[Risk] 事实性问题判断不准确 → **Mitigation:**保守判断，只对高置信度的事实性问题启用 LLM 知识

## Migration Plan

1. **数据库**: 无需迁移，对话历史已存在
2. **代码改动**:
   - `backend/graph/state.py` - 添加 conversation_history 字段
   - `backend/graph/chatbot_graph.py` - 获取历史并传入 state
   - `backend/graph/nodes/generate.py` - 使用历史上下文 + LLM 知识补全
   - `backend/db/sqlite/crud.py` - 添加 get_conversation_history 函数
3. **测试**:
   - 单轮对话（向后兼容）
   - 多轮追问场景验证
   - 事实性问题 LLM 知识回答验证
   - 非事实性问题 fallback 验证

## Open Questions

- 是否需要在配置中添加 `max_history_turns` 配置项？（建议默认 5）
- 事实性问题判断逻辑是否需要优化？（当前为简化版本）

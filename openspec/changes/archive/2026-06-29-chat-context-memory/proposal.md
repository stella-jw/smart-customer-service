## Why

当前 RAG 检索系统将每个用户问题作为独立查询处理，不保留对话历史上下文。当用户追问"内容是什么？"或"作者还有哪些其它作品？"时，系统无法理解"内容"和"作者"指代的是前面对话中提到的《所见》和袁枚。这导致多轮对话中后续问题完全脱离上下文，回答质量严重下降。

## What Changes

1. **新增对话上下文管理机制**
   - 在同一 session 中保存用户问题和 AI 回复
   - 生成回答时将历史对话作为上下文一并传给 LLM
   - 支持上下文窗口控制，避免超出 token 限制

2. **修改 LLM 生成节点 `generate.py`**
   - 接收包含历史消息的完整 prompt
   - 支持可配置的上下文轮数（默认最近 5 轮）

3. **修改聊天 API `chat.py`**
   - 在调用 LLM 前获取同一 session 的历史消息
   - 将历史消息格式化为上下文字符串

4. **新增 LLM 知识补全机制**
   - RAG/QA 未命中时，判断是否为事实性问题
   - 事实性问题：允许 LLM 用自身知识回答，并提示用户"仅供参考"
   - 非事实性问题：保持 fallback，引导用户联系人工客服

5. **保持向后兼容**
   - session_id 不存在或无历史记录时，照常工作
   - 不影响单轮问答场景

## Capabilities

### New Capabilities
- `chat-context-memory`: 对话上下文管理，支持多轮对话上下文传递
- `llm-knowledge-fallback`: LLM 知识补全，RAG/QA 未命中时允许 LLM 用自身知识回答事实性问题

### Modified Capabilities
- 无（现有对话生成流程仅修改实现方式，不改变接口行为）

## Impact

- **后端**: `backend/api/routers/chat.py` - 获取历史消息
- **后端**: `backend/graph/nodes/generate.py` - 构建带上下文的 prompt
- **后端**: `backend/graph/state.py` - 可能需要扩展 state 结构
- **API**: `/api/chat` 接口行为不变，仅内部逻辑变化

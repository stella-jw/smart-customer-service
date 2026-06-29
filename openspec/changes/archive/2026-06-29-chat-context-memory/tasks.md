## 1. Database - Add history query function

- [x] 1.1 在 `backend/db/sqlite/crud.py` 添加 `get_conversation_history()` 函数
- [x] 1.2 支持按 session_id 查询最近 N 轮对话
- [x] 1.3 导出到 `backend/db/sqlite/__init__.py`

## 2. Backend - State definition

- [x] 2.1 在 `backend/graph/state.py` 的 `CustomerServiceState` 添加 `conversation_history` 字段

## 3. Backend - Graph integration

- [x] 3.1 修改 `backend/graph/chatbot_graph.py` 的 `chat()` 函数获取历史消息
- [x] 3.2 将历史消息传递给 `create_initial_state()`
- [x] 3.3 控制历史轮数（默认 5 轮，可配置）

## 4. Backend - Generate node

- [x] 4.1 修改 `backend/graph/nodes/generate.py` 的 `generate_response()` 函数
- [x] 4.2 添加 `format_history_context()` 函数格式化历史
- [x] 4.3 在 prompt 中插入【对话历史】上下文
- [x] 4.4 添加 token 估算和截断逻辑

## 5. Backend - LLM Knowledge Fallback

- [x] 5.1 在 `generate.py` 添加 `is_factual_question()` 函数判断问题类型
- [x] 5.2 在 fallback 分支实现 LLM 知识回答逻辑
- [x] 5.3 添加免责声明提示"以下仅供参考"

## 6. Configuration

- [x] 6.1 在 `backend/db/sqlite/models.py` 的 `BotConfiguration` 添加 `max_history_turns` 字段（Integer, default=5）
- [x] 6.2 数据库迁移：添加 `max_history_turns` 字段

## 7. Frontend (optional)

- [x] 7.1 在 `BotConfigPage.vue` 添加「最大历史轮数」配置项（暂不实现，可后续迭代）

## 8. Testing

- [ ] 8.1 测试单轮对话（向后兼容）
- [ ] 8.2 测试多轮追问：「《所见》作者是谁」→「内容是什么」→「作者还有哪些作品」
- [ ] 8.3 测试历史截断（设置 max_history_turns=2，验证只保留最近 2 轮）
- [ ] 8.4 测试 LLM 知识补全（问"《所见》作者还写过哪些诗"，RAG 未命中时）
- [ ] 8.5 测试非事实性问题 fallback（问"我应该买哪个"，验证引导人工客服）

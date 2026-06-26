## 1. Database Migration

- [x] 1.1 在 `BotConfiguration` 模型添加 `rag_rerank_top_k` 字段（Integer, default=5）
- [x] 1.2 添加数据库迁移脚本，为现有记录设置默认值

## 2. Backend - Model & Config

- [x] 2.1 更新 `backend/db/sqlite/models.py` 的 `BotConfiguration` 类
- [x] 2.2 更新 `get_bot_config` API 返回 `rag_rerank_top_k`
- [x] 2.3 更新 `BotConfigRequest` Pydantic 模型包含 `rag_rerank_top_k`

## 3. Backend - Cross-encoder Implementation

- [x] 3.1 创建 `backend/graph/nodes/cross_encoder_rerank.py` 模块（SiliconFlow API 调用）
- [x] 3.2 实现 `rerank()` 函数（requests 调用）
- [x] 3.3 修改 `backend/graph/nodes/retrieve.py` 集成 rerank 逻辑
- [x] 3.4 添加 fallback 机制（API 不可用时）

**变更说明:** 因 Intel Mac PyTorch 2.2.2 限制，原 sentence-transformers 本地模型方案不可用。Cohere API 国内访问受限（403错误），改用国内直连的 SiliconFlow Rerank API。

## 4. Frontend - BotConfigPage

- [x] 4.1 在 RAG 检索参数区域添加 `rag_rerank_top_k` 输入框
- [x] 4.2 添加前端校验：`rag_rerank_top_k` 不能超过 `rag_top_k`
- [x] 4.3 添加 tooltip 说明（精排后返回数量）

## 5. Dependencies

- [x] 5.1 无需额外安装（requests 已包含在依赖中）
- [x] 5.2 配置 SILICONFLOW_API_KEY 环境变量（已添加到 .env 文件）

## 6. Testing

- [ ] 6.1 测试 rerank 开启时的检索结果
- [ ] 6.2 测试 fallback（API 不可用时）
- [ ] 6.3 测试配置校验逻辑

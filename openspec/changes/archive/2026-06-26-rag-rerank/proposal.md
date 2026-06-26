## Why

当前 RAG 检索仅基于向量相似度搜索，返回的 top_k 结果往往不够精准，影响 AI 回答质量。通过引入 Cross-encoder rerank 机制，可以对初始检索结果进行精排，显著提升检索相关性。

## What Changes

1. **新增 Cross-encoder Rerank 检索流程**
   - 先用向量搜索返回更多候选结果（rag_top_k）
   - 再用 SiliconFlow Rerank API 对候选结果进行精排
   - 最终返回精排后的 top 结果（rag_rerank_top_k）

2. **新增配置项 `rag_rerank_top_k`**
   - 用于配置精排后返回的结果数量
   - 必须 ≤ rag_top_k

3. **保留现有 `rag_top_k` 配置**
   - 内部检索候选数量
   - 建议默认值从 5 调整为 10-20

4. **保持向后兼容**
   - 如果 SiliconFlow Rerank API 不可用（key 未配置/网络问题/限流），fallback 到原有向量搜索流程

## Capabilities

### New Capabilities
- `rag-rerank`: 新增 Cross-encoder 精排检索能力（基于 SiliconFlow Rerank API），支持 rag_top_k 和 rag_rerank_top_k 双配置

### Modified Capabilities
- 无（现有 RAG spec 无需修改，只扩展实现方式）

## Impact

- **后端**: `backend/graph/nodes/retrieve.py` - 修改检索逻辑
- **依赖**: 无新增（使用 requests 库）
- **配置**: `BotConfiguration` 模型新增 `rag_rerank_top_k` 字段
- **前端**: `BotConfigPage.vue` 新增精排数量配置项
- **环境**: 需要配置 `SILICONFLOW_API_KEY` 环境变量

**变更说明:** 原方案使用 sentence-transformers 本地模型，但 Intel Mac PyTorch 2.2.2 不支持 sentence-transformers >= 2.4。Cohere API 国内访问受限（403错误），最终改用国内直连的 SiliconFlow Rerank API。

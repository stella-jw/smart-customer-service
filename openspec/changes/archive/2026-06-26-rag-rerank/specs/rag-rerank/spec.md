## ADDED Requirements

### Requirement: Cross-encoder Rerank Retrieval

RAG 检索节点 SHALL 支持 Cross-encoder 模型对向量搜索结果进行精排，返回更相关的结果。

#### Scenario: Successful rerank with available model
- **WHEN** RAG 检索被触发 AND Cross-encoder 模型可用
- **THEN** 系统执行两步检索：
  1. 向量搜索返回 `rag_top_k` 个候选结果
  2. Cross-encoder 计算候选与查询的相关性分数
  3. 返回分数最高的 `rag_rerank_top_k` 个结果

#### Scenario: Fallback when model unavailable
- **WHEN** RAG 检索被触发 AND Cross-encoder 模型不可用
- **THEN** 系统直接返回向量搜索的前 `rag_rerank_top_k` 个结果 AND 记录警告日志

---

### Requirement: Dual Top-K Configuration

系统 SHALL 支持两个独立的 Top-K 配置项：

#### Scenario: rag_rerank_top_k constraint
- **WHEN** 用户设置 `rag_rerank_top_k` 大于 `rag_top_k`
- **THEN** 系统 SHALL 自动将 `rag_rerank_top_k` 设置为等于 `rag_top_k`

#### Scenario: Default values
- **WHEN** 机器人配置首次创建时
- **THEN** `rag_top_k` 默认值为 15 AND `rag_rerank_top_k` 默认值为 5

---

### Requirement: rag_rerank_top_k in Bot Configuration

系统 SHALL 在 `BotConfiguration` 模型中存储 `rag_rerank_top_k` 配置。

#### Scenario: Configuration retrieval
- **WHEN** 获取机器人配置时
- **THEN** 返回 `rag_rerank_top_k` 字段（如果未设置则为默认值 5）

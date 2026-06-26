## Context

当前 RAG 检索使用 ChromaDB 向量相似度搜索，直接返回 top_k 个结果。但向量搜索仅考虑语义相似度，可能遗漏关键词匹配或上下文相关性更高的结果。

引入 Rerank 模型可以对初始候选结果进行更精确的相关性排序。

## Goals / Non-Goals

**Goals:**
- 实现 Rerank 精排流程，提升检索相关性
- 保留双配置项（rag_top_k 内部检索数量，rag_rerank_top_k 最终返回数量）
- 保持向后兼容，无 Rerank 模型时 fallback 到原有流程

**Non-Goals:**
- 不实现多路召回（Hybrid search）
- 不修改现有的向量搜索实现

## Decisions

### 1. 使用 SiliconFlow Rerank API

**选择:** `BAAI/bge-reranker-v2-m3`（通过 SiliconFlow API 调用）

**理由:**
- MTEB Rerank 榜单前三，效果顶级
- 中文支持优秀
- 纯 API 调用，不依赖本地 PyTorch 运行环境
- 国内直连，无需 VPN
- 免费额度充足（100万tokens/月）

**变更原因:**
项目部署环境为 Intel Mac，PyTorch 2.2.2 是最后一个支持 macOS x86_64 的版本。sentence-transformers >= 2.4 要求 PyTorch >= 2.4，导致本地模型方案均无法运行。Cohere Rerank API 在国内访问受限（403错误），改用国内直连的 SiliconFlow。

**替代方案对比:**
| 方案 | 国内访问 | 中文支持 | 效果 | 免费额度 | 推荐场景 |
|------|----------|---------|------|----------|---------|
| **SiliconFlow** | ✅ | ★★★★★ | ★★★★★ | 100万tokens/月 | ⭐ 推荐 |
| Cohere API | ❌ 403 | ★★★★★ | ★★★★★ | 1000次/月 | 国内不可用 |
| jina-reranker | ❌ | ★★★★ | ★★★ | 100万字符/月 | 国内不可用 |

### 2. 双配置项设计

| 配置项 | 用途 | 默认值 |
|--------|------|--------|
| `rag_top_k` | 内部检索候选数量 | 15 |
| `rag_rerank_top_k` | 精排后返回数量 | 5 |

**理由:**
- rag_top_k 需要足够大以提供 rerank 候选池（建议 10-20）
- rag_rerank_top_k 控制最终给 LLM 的上下文数量
- 约束：rag_rerank_top_k ≤ rag_top_k

### 3. API 连接复用

**设计:** 使用 requests 库直接调用 SiliconFlow API

**理由:**
- SiliconFlow 提供标准 REST API，无需 SDK
- requests 库已包含在依赖中，无额外安装成本
- 按需调用，无连接缓存需求

### 4. Fallback 机制

```python
if is_reranker_available():
    # 1. 向量搜索返回 top_k 个候选
    candidates = vector_search(query, top_k=rag_top_k)
    # 2. SiliconFlow Rerank API 精排
    reranked = rerank(query, candidates)
    # 3. 返回 top rag_rerank_top_k
    return reranked[:rag_rerank_top_k]
else:
    # Fallback: 直接返回向量搜索结果
    return vector_search(query, top_k=rag_rerank_top_k)
```

**API 不可用场景:**
- SILICONFLOW_API_KEY 未配置
- 网络连接失败
- API 限流或服务异常

## Risks / Trade-offs

[Risk] API 调用增加网络延迟 → **Mitigation:** SiliconFlow 国内延迟低（通常 100-300ms），fallback 快速

[Risk] API 依赖外部服务 → **Mitigation:** Fallback 到原始向量搜索，保证服务可用性

[Risk] 免费额度用尽 → **Mitigation:** SiliconFlow 价格便宜（¥1/百万tokens），个人项目基本用不完

[Risk] API Key 泄露 → **Mitigation:** 使用环境变量 SILICONFLOW_API_KEY，不硬编码

## Migration Plan

1. **数据库迁移**: 添加 `rag_rerank_top_k` 字段，默认 5 ✅ 已完成
2. **后端实现**: 修改 `retrieve.py` + 新增 `cross_encoder_rerank.py`（SiliconFlow API）✅ 已完成
3. **前端更新**: BotConfigPage 添加配置项 ✅ 已完成
4. **环境配置**: 添加 SILICONFLOW_API_KEY 环境变量 ✅ 已完成
5. **测试验证**: 回归测试确保 fallback 正常

## Open Questions

- rag_top_k 默认值 15 是否合适？（已确认：15 ✅）
- SILICONFLOW_API_KEY 如何管理？（建议：.env 文件 + 生产环境密钥管理）

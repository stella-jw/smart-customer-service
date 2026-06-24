# Smart Customer Service - Proposal

## Why

企业需要 24/7 的客户服务，但人工客服成本高、效率有限。智能客服可以：
- 即时响应用户问题
- 降低人力成本
- 提高客户满意度

现有解决方案要么太贵，要么不灵活。

## What Changes

基于 Family-Agent 的技术积累，构建企业级智能客服系统：

### 核心功能

| 功能 | 说明 |
|------|------|
| **知识库管理** | 企业上传/维护产品文档、FAQ |
| **RAG 问答** | 基于自有知识库的精准回答 |
| **多轮对话** | 支持追问、澄清、确认 |
| **数据分析** | 热点问题、满意度、改进建议 |

### 用户角色

| 角色 | 权限 |
|------|------|
| **Admin** | 管理知识库、配置客服行为、查看报表 |
| **User** | 提问、查看历史、评价回答 |

## Capabilities

### New Capabilities

- `knowledge-base`：企业知识库管理（上传/解析/维护）
- `rag-chatbot`：基于 RAG 的智能问答
- `admin-dashboard`：企业管理后台
- `analytics`：对话数据分析

### Modified Capabilities

- `family-agent`：可以基于此框架扩展客服功能

## Impact

- 新增 `backend/` API 服务
- 新增 `web/admin/` 管理后台
- 复用 Family-Agent 的 LangGraph + ChromaDB 架构

## 技术栈

| 组件 | 技术选型 |
|------|----------|
| 后端框架 | FastAPI（复用） |
| 前端 | Vue 3 + TypeScript |
| 向量数据库 | ChromaDB（复用） |
| LLM | MiniMax / OpenAI |
| 文档解析 | PDF.js / python-docx |

## 发展阶段

| 阶段 | 目标 | 周期 |
|------|------|------|
| Phase 1 | RAG 基础问答 | 1-2周 |
| Phase 2 | 企业端知识库管理 | 2-3周 |
| Phase 3 | 数据分析与报表 | 1-2周 |
| Phase 4 | 高级功能（多轮/转人工） | 2-3周 |

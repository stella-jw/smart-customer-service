# Smart Customer Service - Implementation Tasks

## Phase 1: RAG 基础问答 (1-2周)

### 1.1 项目结构搭建
- [x] 1.1.1 创建 `smart-customer-service/` 目录结构
- [x] 1.1.2 初始化 FastAPI 后端项目
- [x] 1.1.3 配置依赖 (langgraph, chromadb, fastapi, python-docx)
- [x] 1.1.4 初始化 Vue 3 前端项目

### 1.2 数据库设计
- [x] 1.2.1 实现 SQLite Schema (documents, qa_pairs, conversations, ratings)
- [x] 1.2.2 创建 ChromaDB collection schema
- [x] 1.2.3 实现数据库 CRUD 操作

### 1.3 文档处理
- [x] 1.3.1 实现 document_parser.py (支持 PDF, DOCX, TXT, MD)
- [x] 1.3.2 实现文本分块 (chunk_size=500, overlap=50)
- [x] 1.3.3 实现 embedding 生成与 ChromaDB 存储

### 1.4 RAG 问答流程
- [x] 1.4.1 实现 classify 节点 (判断 RAG/QA/Chat)
- [x] 1.4.2 实现 retrieve 节点 (向量检索 top_k=5)
- [x] 1.4.3 实现 generate 节点 (LLM 生成回答)
- [x] 1.4.4 实现 respond 节点 (格式化输出)

### 1.5 API 接口
- [x] 1.5.1 实现 `/api/chat` POST 接口
- [x] 1.5.2 实现 `/api/history` GET 接口
- [x] 1.5.3 实现 `/api/rate` POST 接口

### 1.6 Web 用户端
- [x] 1.6.1 实现用户问答界面 (chat.vue)
- [x] 1.6.2 实现对话历史界面 (history.vue)
- [x] 1.6.3 实现回答评价组件

---

## Phase 2: 企业端知识库管理 (2-3周)

### 2.1 Admin API
- [x] 2.1.1 实现 `/api/admin/document` POST (上传文档)
- [x] 2.1.2 实现 `/api/admin/document` GET (文档列表)
- [x] 2.1.3 实现 `/api/admin/document/{id}` DELETE
- [x] 2.1.4 实现 `/api/admin/qa` POST (添加 QA)
- [x] 2.1.5 实现 `/api/admin/qa` GET (QA 列表)

### 2.2 Admin Web 端
- [x] 2.2.1 实现知识库管理页面 (knowledge.vue)
- [x] 2.2.2 实现 QA 维护页面 (qa.vue)
- [x] 2.2.3 实现文档上传组件 (支持拖拽)
- [x] 2.2.4 实现文档状态展示 (pending/indexed/failed)

---

## Phase 3: 数据分析与报表 (1-2周)

### 3.1 Analytics API
- [x] 3.1.1 实现 `/api/admin/analytics` GET 接口
- [x] 3.1.2 实现热门问题统计
- [x] 3.1.3 实现满意度统计

### 3.2 Analytics Web
- [ ] 3.2.1 实现数据报表页面 (analytics.vue)
- [ ] 3.2.2 实现 ECharts 图表 (折线图/柱状图)
- [ ] 3.2.3 实现数据导出功能 (CSV)

---

## Phase 4: 高级功能 (2-3周)

### 4.1 多轮对话
- [ ] 4.1.1 实现上下文记忆
- [ ] 4.1.2 实现追问/澄清逻辑

### 4.2 转人工
- [ ] 4.2.1 实现转人工触发条件
- [ ] 4.2.2 实现人工客服接入 (预留接口)

### 4.3 高级分析
- [ ] 4.3.1 实现趋势分析
- [ ] 4.3.2 实现改进建议生成

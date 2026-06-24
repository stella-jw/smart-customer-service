# Smart Customer Service - Design Document

## Context

基于 Family-Agent 的技术架构，设计企业级智能客服系统。核心区别：

| 维度 | Family-Agent | 智能客服 |
|------|-------------|----------|
| 目标用户 | 个人/家庭 | 企业客户 |
| 知识来源 | 用户录入 | 企业文档 |
| 更新频率 | 实时 | 文档更新时 |
| 核心能力 | 记录+查询 | 检索+回答 |

## Goals / Non-Goals

**Goals:**
- 企业可自主管理知识库
- 基于 RAG 的精准问答
- 复用 Family-Agent 的技术栈
- 支持多种文档格式

**Non-Goals:**
- 不做人工客服接入（Phase 4 以后）
- 不做多租户隔离（Phase 1）
- 不做复杂工作流编排

## Architecture

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户端（Web）                          │
│   ┌─────────────┐    ┌─────────────┐                      │
│   │   问答界面   │    │  历史记录   │                      │
│   └─────────────┘    └─────────────┘                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Admin 端（Web）                        │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│   │  知识库管理  │    │   QA 维护   │    │   数据报表   │   │
│   └─────────────┘    └─────────────┘    └─────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      REST API（FastAPI）                    │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐             │
│   │ 文档上传  │   │   RAG   │   │  数据分析  │             │
│   └──────────┘   └──────────┘   └──────────┘             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph 工作流                          │
│   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐     │
│   │classify│──▶│retrieve│──▶│generate│──▶│respond │     │
│   └────────┘   └────────┘   └────────┘   └────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   ChromaDB + SQLite                       │
│        （向量检索）          （结构化数据）                 │
└─────────────────────────────────────────────────────────────┘
```

### 项目结构

```
smart-customer-service/
├── backend/
│   ├── api/
│   │   ├── main.py           # FastAPI 入口
│   │   ├── routers/
│   │   │   ├── chat.py       # 问答接口
│   │   │   ├── knowledge.py  # 知识库接口
│   │   │   └── admin.py      # 管理接口
│   │   └── service/
│   │       ├── document_parser.py
│   │       └── analytics.py
│   └── graph/
│       └── chatbot_graph.py   # LangGraph 工作流
├── web/
│   ├── user/                 # 用户端
│   │   ├── pages/chat.vue
│   │   └── pages/history.vue
│   └── admin/                # 管理端
│       ├── pages/knowledge.vue
│       ├── pages/qa.vue
│       └── pages/analytics.vue
└── data/
    ├── chroma_db/            # 向量数据库
    └── documents/            # 原始文档
```

## Database Design

### SQLite Schema

```sql
-- 文档表
CREATE TABLE documents (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    file_type VARCHAR(20),  -- pdf/docx/txt/md
    file_path VARCHAR(500),
    status ENUM('pending', 'indexed', 'failed') DEFAULT 'pending',
    chunk_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- QA 对表
CREATE TABLE qa_pairs (
    id VARCHAR(36) PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords VARCHAR(500),  -- 便于检索
    usage_count INT DEFAULT 0,
    satisfaction_rate FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 对话记录表
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(100),
    user_id VARCHAR(100),
    message TEXT,
    is_from_user BOOLEAN,
    source ENUM('rag', 'qa', 'llm') DEFAULT 'llm',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 评价记录表
CREATE TABLE ratings (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36),
    rating INT,  -- 1-5
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### ChromaDB Schema

```python
{
    "document_id": "uuid",
    "chunk_index": 0,
    "content": "文档片段内容",
    "source": "knowledge_base",
    "metadata": {
        "title": "产品手册",
        "section": "第三章",
        "url": "..."
    }
}
```

## RAG Pipeline

### 1. 文档处理

```python
async def process_document(file_path: str) -> list[str]:
    """
    1. 根据文件类型调用解析器
    2. 文本清洗
    3. 分块（chunk）
    4. 生成 embedding
    5. 存入 ChromaDB
    """
    pass
```

### 2. 问答流程

```python
def chatbot_graph():
    """
    classify → retrieve → generate → respond
    """
    # classify: 判断是 RAG 问答还是闲聊
    # retrieve: 从 ChromaDB 检索相关片段
    # generate: LLM 基于检索结果生成回答
    # respond: 格式化输出
```

## API Design

### 用户端接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | 发送问题 |
| `/api/history` | GET | 对话历史 |
| `/api/rate` | POST | 评价回答 |

### Admin 端接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/admin/document` | POST | 上传文档 |
| `/api/admin/document` | GET | 文档列表 |
| `/api/admin/document/{id}` | DELETE | 删除文档 |
| `/api/admin/qa` | POST | 添加 QA |
| `/api/admin/qa` | GET | QA 列表 |
| `/api/admin/analytics` | GET | 数据报表 |

## 技术决策

### 1. 文档解析

| 方案 | 优点 | 缺点 |
|------|------|------|
| PDF.js | 前端渲染简单 | 不解析文本 |
| python-docx | 解析 Word | 需要后端 |
| Marker | PDF→Markdown | 效果最好 |

**选择：后端 python-docx + 前端 PDF.js**

### 2. 分块策略

| 策略 | chunk_size | overlap |
|------|-----------|---------|
| 固定大小 | 500 chars | 50 chars |
| 按段落 | 段落完整 | 无 |

**选择：固定大小 + overlap（召回率高）**

### 3. 检索策略

```python
def retrieve(query: str, top_k: int = 5):
    # 1. 向量检索
    vectors = chromadb.query(query_texts=[query], n_results=top_k)

    # 2. 重排序（可选）
    # reranked = rerank(results, query)

    # 3. 返回 top_k
    return vectors
```

## Risks / Trade-offs

| 风险 | 影响 | 缓解 |
|------|------|------|
| 文档解析失败 | 部分内容无法检索 | 增强解析容错 |
| LLM 幻觉 | 回答不准确 | 限制回答范围 |
| 冷启动 | 新文档需要时间索引 | 异步处理 |

## Migration

### 从 Family-Agent 复用

| 模块 | 复用度 |
|------|--------|
| LangGraph | 80% |
| ChromaDB | 100% |
| FastAPI | 90% |
| Vue Web | 40%（复用组件）|

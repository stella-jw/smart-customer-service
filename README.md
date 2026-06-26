# 智能客服系统 (Smart Customer Service)

一个基于大模型的通用型企业智能客服系统，通过 Admin 端配置，让任何企业（医疗、电商、SaaS、IT）都能快速部署使用。

## 产品定位

**通用型企业智能客服** - 多租户架构，通过配置适配不同行业，企业可自主管理知识库。

## 核心功能

### 用户端

- **智能问答**：基于知识库和 QA 对的精准回答
- **多机器人切换**：用户可选择不同的客服机器人（需登录）
- **默认机器人**：未登录用户自动使用默认机器人
- **对话历史**：支持多会话管理和历史记录查看
- **评价反馈**：5分钟无操作后弹出评价窗口

### Admin 端

- **多机器人管理**：创建/配置多个行业客服机器人
- **默认机器人**：可设置默认机器人，支持一键切换
- **知识库管理**：上传/解析/索引企业文档（PDF/DOCX/TXT/MD/HTML）
- **QA 对维护**：添加/编辑/批量导入问答对
- **机器人配置**：人格/话术/功能开关/检索参数
- **数据分析**：对话量/命中率/满意度统计
- **行业模板**：电商/医疗/SaaS/IT 快速启动模板
- **向量查看器**：查看已切片的向量片段（chunks-viewer.html）

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户端（Web）                            │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│   │   问答界面   │    │  历史记录     │    │ 机器人切换    │    │
│   └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Admin 端（Web）                         │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│   │  机器人管理   │    │  知识库管理  │     │   QA 维护   │     │
│   └─────────────┘    └─────────────┘    └─────────────┘     │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│   │  机器人配置  │     │  数据报表    │    │  向量查看     │    │
│   └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      REST API（FastAPI）                     │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐                │
│   │  /chat   │   │ /api/bots│   │ /admin/* │                │
│   └──────────┘   └──────────┘   └──────────┘                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   LangGraph 工作流                               │
│                                                                 │
│  ┌───────────────┐                                              │
│  │     START     │                                              │
│  └──────┬────────┘                                              │
│         ▼                                                       │
│  ┌───────────────┐     ┌────────────┐                           │
│  │classify_intent│────▶│route_intent│                           │
│  └───────────────┘     └─────┬──────┘                           │
│        │                  ├──greeting──▶ respond                │
│        │                  ├──question──▶ qa_match ─┐            │
│        │                  └──other──────▶ generate─┼──▶ respond │
│        │                                    rag_retrieve──▶     │
│        │                                          generate──▶   │
│        │                                                        │
│        └──────────────────────────────────────────────────▶     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   ChromaDB + SQLite                         │
│   kb_chunks_{bot_id}    qa_embeddings_{bot_id}   SQLite     │
│        （向量检索）          （QA匹配）         （结构化数据）    │
└─────────────────────────────────────────────────────────────┘
```

### 问答流程

```
用户提问
    │
    ▼
┌───────────────────────────────────────┐
│  1. 意图分类 (classify_intent)         │
│     判断：greeting/question/other      │
└───────────────────────────────────────┘
    │
    ▼ (如果是 question)
┌───────────────────────────────────────┐
│  2. QA匹配 (qa_match)                 │
│     - ChromaDB 向量相似度搜索           │
│     - similarity >= 阈值 ?             │
│     - 命中 → 直接返回答案                │
└───────────────────────────────────────┘
    │
    ▼ (QA未命中)
┌───────────────────────────────────────┐
│  3. RAG检索 (rag_retrieve)            │
│     - 知识库向量搜索 (rag_top_k)        │
│     - [可选] SiliconFlow Rerank 精排   │
│     - 返回 rag_rerank_top_k 个结果     │
└───────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────┐
│  4. 响应生成 (generate_response)       │
│     - 结合检索结果生成回答              │
└───────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────┐
│  5. 最终回复 (respond)                 │
│     - 应用机器人话术配置               │
│     - 返回最终响应                      │
└───────────────────────────────────────┘
```

**注意**：每个机器人有独立的知识库和QA数据，通过 ChromaDB collection 隔离。

## 技术栈

| 组件 | 技术选型 |
|------|----------|
| 对话大模型 | MiniMax API（minimax-text-01） |
| 嵌入模型 | MiniMax Embedding API（embo-01, 1024维） |
| 工作流框架 | LangGraph |
| 向量数据库 | ChromaDB |
| 结构化数据库 | SQLite + SQLAlchemy |
| REST API | FastAPI |
| 前端 | Vue 3 + Vite + TypeScript |
| 文档解析 | PyPDF2/pdfplumber + python-docx |
| Rerank精排 | SiliconFlow Rerank API（BAAI/bge-reranker-v2-m3） |
| 可观测性 | LangSmith（LLM 应用 tracing 与调试） |

## 项目结构

```
smart-customer-service/
├── backend/
│   ├── api/
│   │   ├── main.py           # FastAPI 入口
│   │   └── routers/
│   │       ├── chat.py       # 用户端聊天接口
│   │       ├── admin.py      # Admin 管理接口
│   │       └── knowledge.py  # 知识库接口
│   ├── db/
│   │   ├── sqlite/
│   │   │   ├── models.py    # SQLAlchemy 模型
│   │   │   ├── crud.py       # CRUD 操作
│   │   │   └── init_db.py    # 数据库初始化
│   │   └── chroma/
│   │       └── manager.py    # 多租户 ChromaDB 管理
│   ├── graph/
│   │   ├── state.py          # 状态定义
│   │   ├── chatbot_graph.py  # LangGraph 工作流
│   │   └── nodes/            # 工作流节点
│   │       ├── classify.py   # 意图分类
│   │       ├── qa_match.py   # QA匹配
│   │       ├── retrieve.py   # RAG检索 + Rerank精排
│   │       ├── generate.py   # 响应生成
│   │       └── respond.py    # 最终回复
│   └── service/
│       ├── document_parser.py  # 文档解析
│       └── chunker.py          # 文本分块
├── web/
│   ├── src/
│   │   ├── api/              # API 调用
│   │   ├── stores/           # 状态管理 (botStore)
│   │   ├── router/           # 路由配置
│   │   ├── pages/
│   │   │   ├── user/        # 用户端页面 (ChatPage, HistoryPage)
│   │   │   └── admin/       # Admin 页面 (BotConfigPage...)
│   │   └── components/      # 公共组件 (BotSwitcher)
│   ├── chunks-viewer.html    # 向量片段查看器
│   └── vite.config.ts        # Vite 配置
├── data/
│   ├── chroma_db/             # 向量数据库
│   ├── documents/             # 原始文档
│   └── customer_service.db   # SQLite 数据库
├── migrations/               # 数据库迁移脚本
├── config.py                 # 配置文件
├── requirements.txt          # Python 依赖
└── README.md
```

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/stella-jw/smart-customer-service.git
cd smart-customer-service
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env  # 如有 .env.example
# 或手动创建 .env 文件，参考 .env 部分
```

**必须配置的环境变量：**

```bash
# MiniMax API Key（从 MiniMax 开放平台获取）
MINIMAX_API_KEY=your-minimax-api-key

# SiliconFlow API Key（从 https://www.siliconflow.cn 获取）
# 用于 Rerank 精排功能，如不配置则自动跳过精排
SILICONFLOW_API_KEY=your-siliconflow-api-key
```

**可选配置：**

```bash
# LangSmith（从 https://langchain.com/langsmith 免费获取）
# 用于 LLM 应用 tracing 与调试，可视化查看检索/生成链路
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=smart-customer-service
```

### 5. 初始化数据库

```bash
python -c "from backend.db.sqlite import init_database; init_database()"
```

### 6. 启动后端服务

```bash
uvicorn backend.api.main:app --reload --port 8000
```

### 7. 启动前端（可选）

```bash
cd web
npm install
npm run dev
```

## API 接口

### 用户端接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | 发送问题，获取回答 |
| `/api/history/{session_id}` | GET | 获取对话历史 |
| `/api/rate` | POST | 评价回答 |

### Admin 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/admin/bots` | GET/POST | 机器人列表/创建 |
| `/api/admin/bots/default` | GET | 获取当前默认机器人 |
| `/api/admin/bots/default/{bot_id}` | PUT | 设置默认机器人 |
| `/api/admin/bots/{id}` | GET/PUT/DELETE | 机器人详情/更新/删除 |
| `/api/admin/bots/{id}/config` | GET/PUT | 机器人配置 |
| `/api/admin/chunks/{bot_id}` | GET | 获取机器人的向量片段 |
| `/api/admin/documents` | GET/POST | 文档列表/上传 |
| `/api/admin/documents/{id}` | DELETE | 删除文档 |
| `/api/admin/qa` | GET/POST | QA对列表/创建 |
| `/api/admin/qa/{id}` | PUT/DELETE | QA对更新/删除 |
| `/api/admin/analytics/{bot_id}` | GET | 数据统计 |

### 用户端公开接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/bots` | GET | 获取机器人列表（公开，无需登录） |
| `/api/chat` | POST | 发送问题（bot_id 可选，不填则使用默认机器人） |

## 数据库 Schema

### SQLite 表

- **bots**: 机器人配置（含 `is_default` 字段标记默认机器人）
- **documents**: 知识库文档
- **qa_pairs**: 问答对
- **conversations**: 对话记录
- **ratings**: 评价记录
- **bot_configurations**: 机器人详细配置
- **industry_templates**: 行业模板

### ChromaDB Collections

- `kb_chunks_{bot_id}`: 知识库文档分块
- `qa_embeddings_{bot_id}`: QA 问题嵌入

## Admin 配置项

| 模块 | 配置项 |
|------|--------|
| 话术 | welcome/opening/fallback/timeout 消息 |
| 人格 | personality (专业/友好/幽默/同理心) |
| 语气 | response_tone (正式/亲切/简洁/详细) |
| 功能开关 | enable_rag / enable_qa_match / enable_chitchat / enable_rating |
| **检索参数** | **rag_top_k**（候选数量）/ **rag_rerank_top_k**（精排返回数量） |
| 评价设置 | require_feedback (是否必填评价) |

### RAG 检索参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `rag_top_k` | 15 | 内部向量搜索候选数量，建议 10-20 |
| `rag_rerank_top_k` | 5 | SiliconFlow Rerank 精排后返回数量，必须 ≤ rag_top_k |
| `qa_match_threshold` | 0.85 | QA 匹配相似度阈值 |

> **Rerank 精排机制**：当 `SILICONFLOW_API_KEY` 配置后，系统会先用 `rag_top_k` 进行向量搜索获取候选文档，再通过 SiliconFlow Rerank API 进行精排，返回最相关的 `rag_rerank_top_k` 个结果。未配置 API Key 时，自动 fallback 到原始向量搜索。

## 行业模板

| 行业 | 预置分类 | 建议分块 |
|------|----------|----------|
| 电商 | 产品咨询/物流/售后/优惠 | 400字符 |
| 医疗 | 预约/症状/药品/保险 | 600字符 |
| SaaS | 功能咨询/技术问题/账单 | 500字符 |
| IT服务 | 故障报修/技术支持/账号 | 500字符 |

## 数据库迁移

### 添加 rag_rerank_top_k 字段

```bash
python migrations/add_rag_rerank_column.py
```

### 添加默认机器人字段

```bash
python migrations/add_default_bot_column.py
```

## 常见问题

### Q: ChromaDB 只读错误

```bash
rm -rf ./data/chroma_db/
```

### Q: 文档解析失败

检查文件格式是否支持（PDF/DOCX/TXT/MD/HTML），确认文件未加密。

### Q: QA 匹配不生效

1. 检查 `qa_match_threshold` 配置（默认 0.85），降低阈值可提高匹配率
2. 确认 QA 对已正确添加到 ChromaDB（可通过 chunks-viewer.html 查看）
3. 如果是之前添加的 QA 对，需要删除后重新添加才能生效

### Q: Rerank 精排不生效

1. 确认 `.env` 中已配置 `SILICONFLOW_API_KEY`
2. 检查后端日志是否包含 `[Reranker] SiliconFlow 精排完成` 信息
3. 如未配置 API Key，系统自动 fallback 到原始向量搜索

### Q: 无法删除默认机器人

必须先设置另一个机器人为默认，才能删除当前默认机器人。

## 开发说明

### 添加新的工作流节点

1. 在 `backend/graph/nodes/` 创建节点文件
2. 在 `backend/graph/chatbot_graph.py` 注册节点
3. 添加条件边路由

### 添加新的文档解析器

1. 在 `backend/service/document_parser.py` 继承 `DocumentParser`
2. 注册到 `SUPPORTED_TYPES` 字典

## 许可证

MIT License

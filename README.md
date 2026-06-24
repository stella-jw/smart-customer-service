# 智能客服系统 (Smart Customer Service)

一个基于大模型的通用型企业智能客服系统，通过 Admin 端配置，让任何企业（医疗、电商、SaaS、IT）都能快速部署使用。

## 产品定位

**通用型企业智能客服** - 多租户架构，通过配置适配不同行业，企业可自主管理知识库。

## 核心功能

### 用户端

- **智能问答**：基于知识库和 QA 对的精准回答
- **对话历史**：支持多会话管理和历史记录查看
- **评价反馈**：5 星评价 + 反馈原因收集

### Admin 端

- **多机器人管理**：创建/配置多个行业客服机器人
- **知识库管理**：上传/解析/索引企业文档（PDF/DOCX/TXT/MD/HTML）
- **QA 对维护**：添加/编辑/批量导入问答对
- **机器人配置**：人格/话术/功能开关/检索参数
- **数据分析**：对话量/命中率/满意度统计
- **行业模板**：电商/医疗/SaaS/IT 快速启动模板

## 技术架构

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
│   │classify│──▶│qa_match│──▶│retrieve│──▶│respond │     │
│   └────────┘   └────────┘   └────────┘   └────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   ChromaDB + SQLite                       │
│        （向量检索）          （结构化数据）                 │
└─────────────────────────────────────────────────────────────┘
```

### 回答策略

```
用户问题 → classify(意图分类)
              ↓
        QA匹配 (阈值0.85)
              ↓ (未命中)
         RAG检索 (top_k=5)
              ↓ (未命中)
           兜底回复
```

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
│   │   │   └── crud.py       # CRUD 操作
│   │   └── chroma/
│   │       └── manager.py    # 多租户 ChromaDB 管理
│   ├── graph/
│   │   ├── state.py          # 状态定义
│   │   ├── chatbot_graph.py  # LangGraph 工作流
│   │   └── nodes/            # 工作流节点
│   │       ├── classify.py
│   │       ├── qa_match.py
│   │       ├── retrieve.py
│   │       ├── generate.py
│   │       └── respond.py
│   └── service/
│       ├── document_parser.py  # 文档解析
│       └── chunker.py          # 文本分块
├── web/
│   ├── user/                   # 用户端 Vue
│   │   ├── pages/
│   │   └── components/
│   └── admin/                  # Admin 端 Vue
│       ├── pages/
│       │   ├── Dashboard.vue
│       │   ├── KnowledgeBase.vue
│       │   ├── QAManagement.vue
│       │   └── BotConfig.vue
│       └── components/
├── data/
│   ├── chroma_db/             # 向量数据库
│   ├── documents/             # 原始文档
│   └── customer_service.db     # SQLite 数据库
├── config.py                  # 配置
├── requirements.txt           # Python 依赖
└── README.md
```

## 安装步骤

### 1. 克隆项目

```bash
cd /Users/yiliatang/AI/agent-demo/smart-customer-service
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

### 4. 配置 MiniMax API Key

```bash
cp .env.example .env
# 编辑 .env 文件，填入 MINIMAX_API_KEY
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
| `/api/admin/bots/{id}` | GET/PUT/DELETE | 机器人详情/更新/删除 |
| `/api/admin/bots/{id}/config` | GET/PUT | 机器人配置 |
| `/api/admin/documents` | GET/POST | 文档列表/上传 |
| `/api/admin/documents/{id}` | DELETE | 删除文档 |
| `/api/admin/qa` | GET/POST | QA对列表/创建 |
| `/api/admin/qa/{id}` | PUT/DELETE | QA对更新/删除 |
| `/api/admin/analytics/{bot_id}` | GET | 数据统计 |

## 数据库 Schema

### SQLite 表

- **bots**: 机器人配置
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
| 功能开关 | enable_rag / enable_qa_match / enable_chitchat |
| 检索参数 | rag_top_k / qa_match_threshold |

## 行业模板

| 行业 | 预置分类 | 建议分块 |
|------|----------|----------|
| 电商 | 产品咨询/物流/售后/优惠 | 400字符 |
| 医疗 | 预约/症状/药品/保险 | 600字符 |
| SaaS | 功能咨询/技术问题/账单 | 500字符 |
| IT服务 | 故障报修/技术支持/账号 | 500字符 |

## 常见问题

### Q: ChromaDB 只读错误

```bash
rm -rf ./data/chroma_db/
```

### Q: 文档解析失败

检查文件格式是否支持（PDF/DOCX/TXT/MD/HTML），确认文件未加密。

### Q: QA 匹配不生效

检查 `qa_match_threshold` 配置（默认 0.85），降低阈值可提高匹配率。

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

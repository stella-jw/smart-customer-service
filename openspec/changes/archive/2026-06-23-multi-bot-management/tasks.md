# Multi-Bot Management - Tasks

## 1. Layout Structure

### 1.1 Admin Layout
- [x] 1.1.1 创建 `AdminLayout.vue` 左右分栏布局
- [x] 1.1.2 左侧导航菜单（机器人管理、知识库、QA管理、机器人配置）
- [x] 1.1.3 右侧内容区域显示当前模块
- [x] 1.1.4 导航高亮当前选中项

---

## 2. Bot Management (机器人管理)

### 2.1 Bot Store (Pinia)
- [x] 2.1.1 创建 `stores/botStore.ts`
- [x] 2.1.2 实现 `currentBotId` 状态（localStorage 持久化）
- [x] 2.1.3 实现 `botList` 状态和 `fetchBots` action
- [x] 2.1.4 实现 `switchBot` action
- [x] 2.1.5 实现 `isAtLimit` computed 属性（限制5个）

### 2.2 Bot List Page
- [x] 2.2.1 创建 `pages/admin/BotsPage.vue`
- [x] 2.2.2 Bot 卡片列表展示（名称、行业、状态）
- [x] 2.2.3 显示每个 Bot 的统计（对话数、满意度）
- [x] 2.2.4 添加 Bot 按钮（上限5个时禁用）
- [x] 2.2.5 删除按钮 + 确认弹窗
- [x] 2.2.6 创建 Bot 弹窗表单

### 2.3 Bot Switcher (顶部下拉)
- [x] 2.3.1 创建 `components/BotSwitcher.vue`
- [x] 2.3.2 显示当前 Bot 名称
- [x] 2.3.3 下拉列表显示所有 Bot
- [x] 2.3.4 切换时调用 `botStore.switchBot()`

---

## 3. Knowledge Base Management (知识库管理)

### 3.1 Knowledge Base Page
- [x] 3.1.1 重构 `pages/admin/KnowledgeBasePage.vue`
- [x] 3.1.2 显示知识库文档列表
- [x] 3.1.3 每个文档显示所属机器人名称
- [x] 3.1.4 上传文档时可选择机器人
- [x] 3.1.5 删除文档功能
- [x] 3.1.6 不提供编辑文档功能

### 3.2 Document Upload
- [x] 3.2.1 上传弹窗选择目标机器人
- [x] 3.2.2 拖拽或点击上传
- [x] 3.2.3 文档状态（pending/parsing/indexed/failed）

---

## 4. QA Management (QA管理)

### 4.1 QA List Page
- [x] 4.1.1 重构 `pages/admin/QAManagementPage.vue`
- [x] 4.1.2 显示 QA 对列表（所属机器人）
- [x] 4.1.3 添加/编辑/删除 QA 对
- [x] 4.1.4 按机器人筛选 QA

---

## 5. Bot Configuration (机器人配置)

### 5.1 Config Page
- [x] 5.1.1 重构 `pages/admin/BotConfigPage.vue`
- [x] 5.1.2 配置当前机器人的 RAG 参数（top_k 等）
- [x] 5.1.3 配置 QA 匹配参数（阈值等）
- [x] 5.1.4 配置机器人人格和话术

---

## 6. API Updates

### 6.1 Bot API
- [x] 6.1.1 `GET /api/admin/bots` 获取所有机器人（已存在）
- [x] 6.1.2 `POST /api/admin/bots` 创建机器人（已存在）
- [x] 6.1.3 `PUT /api/admin/bots/{bot_id}` 更新机器人（已存在）
- [x] 6.1.4 `DELETE /api/admin/bots/{bot_id}` 删除机器人（已存在）

### 6.2 Document API
- [x] 6.2.1 `GET /api/admin/documents?bot_id={id}` 按机器人获取文档（已存在）
- [x] 6.2.2 `POST /api/admin/documents?bot_id={id}` 上传到指定机器人（已存在）

### 6.3 Analytics API
- [x] 6.3.1 `GET /api/admin/analytics/{bot_id}` 获取指定机器人统计（已存在）

# Admin Auth & Frontend Separation - Tasks

## 1. Backend - Admin 认证系统

### 1.1 数据库模型
- [x] 1.1.1 创建 `admins` 表 (id, username, password_hash, created_at)
- [x] 1.1.2 添加 SQLAlchemy Admin 模型
- [x] 1.1.3 添加 Admin CRUD 操作

### 1.2 JWT 认证
- [x] 1.2.1 实现密码哈希工具 (bcrypt)
- [x] 1.2.2 实现 JWT 生成函数 (24h expiry)
- [x] 1.2.3 实现 JWT 验证中间件
- [x] 1.2.4 创建 `/api/auth/login` 接口
- [x] 1.2.5 创建 `/api/auth/register` 接口

### 1.3 API 鉴权
- [x] 1.3.1 为所有 `/api/admin/*` 添加 `verify_admin_token` 依赖
- [x] 1.3.2 验证公开的 `/api/*` 不受影响

### 1.4 Bug 修复
- [x] 1.4.1 修复 `sessionmaker` 未导入错误
- [x] 1.4.2 修复 SQLAlchemy `metadata` 保留字冲突（重命名为 `doc_metadata`, `conv_metadata`）

---

## 2. Frontend - 项目分离

### 2.1 创建 Admin 前端项目
- [x] 2.1.1 初始化 `web/admin/` Vue 3 项目
- [x] 2.1.2 配置路由守卫 (Navigation Guard)
- [x] 2.1.3 创建登录页面 (`/admin/login`)
- [x] 2.1.4 创建注册页面 (`/admin/register`)

### 2.2 用户端保留
- [x] 2.2.1 保留 `web/user/` 作为独立项目
- [x] 2.2.2 确保用户端无需登录直接访问

### 2.3 登录组件
- [x] 2.3.1 实现 AdminLoginForm 组件
- [x] 2.3.2 实现 Token 存储 (localStorage)
- [x] 2.3.3 实现登出功能

### 2.4 注册页面
- [x] 2.4.1 独立注册页面 (`/admin/register`)
- [x] 2.4.2 密码校验：6-8位，必须包含大写字母、小写字母、数字、特殊字符
- [x] 2.4.3 确认密码校验

### 2.5 头部用户信息
- [x] 2.5.1 登录后右上角显示管理员用户名
- [x] 2.5.2 退出登录按钮

---

## 3. 前端 API 集成

### 3.1 Admin API 客户端
- [x] 3.1.1 创建 `api/admin/auth.ts` (登录/注册API)
- [x] 3.1.2 添加请求拦截器自动附加 Token
- [x] 3.1.3 处理 401 响应跳转登录页

### 3.2 路由守卫
- [x] 3.2.1 未登录访问 `/admin/*` 跳转登录页
- [x] 3.2.2 已登录访问 `/admin/login` 或 `/admin/register` 跳转后台首页

---

## 4. 机器人管理

### 4.1 机器人列表页
- [x] 4.1.1 创建 BotsPage 页面 (`/admin/bots`)
- [x] 4.1.2 显示机器人列表（名称、行业、状态）
- [x] 4.1.3 创建机器人（最多5个）
- [x] 4.1.4 删除机器人 + 确认弹窗

### 4.2 Dashboard 集成
- [x] 4.2.1 显示机器人数量 (X/5)
- [x] 4.2.2 点击跳转机器人管理页面

### 4.3 路由配置
- [x] 4.3.1 添加 `/admin/bots` 路由

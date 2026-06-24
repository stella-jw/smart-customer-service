## Why

当前 Admin 管理后台和客服前台混在一起，缺乏安全隔离。Admin 后台包含企业敏感配置（知识库、QA对、统计数据），必须限制访问；客服前台面向最终用户，需要无障碍使用体验。

## What Changes

1. **前端分离**：将现有的 `/admin` 路由拆分为独立的 Admin 前端项目，与用户端前台彻底分离
2. **Admin 认证**：为 Admin 后台添加 JWT 管理员登录机制
3. **用户端免登录**：客服前台保持无登录体验，用户直接使用
4. **API 鉴权**：Admin API 添加 Token 验证中间件，用户端 API 保持公开
5. **独立部署**：两个前端可独立部署、独立域名

## Capabilities

### New Capabilities

- `admin-auth`: 管理员认证系统（JWT登录、Token刷新、角色验证）
- `frontend-separation`: 前端项目分离（用户端 `/web/user`、管理端 `/web/admin`）
- `api-gateway`: API 路由鉴权（区分 Admin API 和用户端 API）

### Modified Capabilities

- `rag-chatbot`: 用户端问答流程保持不变，新增 `source_api` 标识区分调用来源

## Impact

- **前端**：`/web/` 拆分为 `/web/user/` 和 `/web/admin/` 两个独立子项目
- **后端**：`/api/admin/*` 全部添加 JWT 验证中间件
- **数据库**：新增 `admins` 表存储管理员账号
- **部署**：两个前端可独立部署到不同域名

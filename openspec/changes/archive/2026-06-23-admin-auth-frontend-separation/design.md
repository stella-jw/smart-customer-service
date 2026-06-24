## Context

当前智能客服系统的 Web 前端同时服务于用户和管理员，路由结构为 `/user/*` 和 `/admin/*`。这种混合架构存在以下问题：

1. **安全风险**：Admin API 和用户端 API 没有分离，任何人都可以调用管理接口
2. **部署不灵活**：无法独立部署/更新用户端和管理端
3. **用户体验**：用户端页面可能被误操作修改

## Goals / Non-Goals

**Goals:**
- 实现前端项目分离：用户端 `/web/user/`、管理端 `/web/admin/`
- Admin 后台添加 JWT 认证，登录后方可访问
- 用户端保持免登录体验
- API 层添加鉴权中间件区分调用来源

**Non-Goals:**
- 不实现多租户隔离（Phase 1 已是 Collection 隔离）
- 不实现 OAuth/SSO 第三方登录
- 不修改现有用户端问答流程

## Decisions

### Decision 1: 前端项目结构

**选择**：将 `/web/` 拆分为两个独立子项目

```
web/
├── user/          # 用户端 Vue 项目（免登录）
│   ├── src/
│   └── package.json
└── admin/         # 管理端 Vue 项目（JWT 登录）
    ├── src/
    └── package.json
```

**理由**：完全独立，可单独部署、单独开发、单独版本管理。

### Decision 2: 认证方案

**选择**：JWT（JSON Web Token）+ 管理员表

```
admins(id, username, password_hash, created_at)
```

**理由**：
- 轻量级，无需 Session 存储
- 支持 Token 过期和刷新
- 业界标准方案

**替代方案**：
- Session + Redis：适合高并发，但增加部署复杂度
- OAuth/SSO：适合多系统集成，当前场景过重

### Decision 3: API 鉴权中间件

**选择**：在 FastAPI 添加依赖注入中间件

```python
# Admin API 需要验证 JWT
@router.post("/admin/bots", dependencies=[verify_admin_token])

# 用户端 API 保持公开
@router.post("/chat")  # 无依赖
```

**理由**：FastAPI 原生支持依赖注入，代码清晰。

### Decision 4: 密码存储

**选择**：bcrypt 哈希

**理由**：行业标准，防彩虹表攻击。

## Risks / Trade-offs

| 风险 | 影响 | 缓解 |
|------|------|------|
| JWT Token 泄露 | 未授权访问 Admin | HTTPS 传输 + 短期过期(24h) |
| 忘记密码 | 无法登录 | 提供密码重置接口（未来扩展） |
| 前端代码重复 | 维护成本 | 抽取公共组件到 `web/common/` |

## Migration Plan

1. **Phase 1**: 创建 `web/admin/` 项目结构，添加登录页面
2. **Phase 2**: 实现 JWT 认证 API + Admin 中间件
3. **Phase 3**: 将现有 Admin 页面迁移到 `web/admin/`
4. **Phase 4**: 用户端 `/web/user/` 独立部署验证

**回滚方案**：如有问题，可快速切回合并版本（保留 `web/` 备份分支）。

## Open Questions

1. **是否需要双因素认证（2FA）？** 当前方案暂不考虑，后续可扩展
2. **管理员权限分级？** 当前只有超级管理员，后续可扩展角色表
3. **Session 并发登录限制？** JWT 无状态，暂不限制

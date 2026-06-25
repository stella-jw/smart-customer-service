## Context

当前系统只有管理员概念（通过 admin_token 区分），没有用户角色体系。匿名用户和登录用户都使用同一套逻辑，无法控制机器人访问权限。

## Goals / Non-Goals

**Goals:**
- 实现三种用户角色体系（匿名用户、内部用户、管理员）
- 管理员可访问管理后台，配置机器人权限
- 实现机器人访问控制列表（ACL）
- 支持按团队分配机器人访问权限

**Non-Goals:**
- 不支持OAuth、SSO等第三方登录
- 不支持权限的继承或嵌套（团队下再分组）

## Decisions

### 1. 用户角色定义

| 角色 | 标识 | 说明 |
|------|------|------|
| 匿名用户 | anonymous | 未登录，session绑定，使用默认机器人 |
| 内部用户 | internal | 已登录，可选择有权限的机器人 |
| 管理员 | admin | 已登录，可管理后台和配置权限 |

**备选方案**: 在 User 表中用 role 字段区分
**结论**: 采用 role 字段，简化判断逻辑

### 2. 机器人访问控制模型

采用 ACL（访问控制列表）模式：

```
BotAccess {
  bot_id: string
  access_type: "all" | "specific_users" | "specific_teams"
  allowed_users: string[]  // user_id列表
  allowed_teams: string[]  // team_id列表
}
```

**备选方案 A**: 每个机器人预设可见性（公开/私有/团队）
- 灵活性不足

**备选方案 B**: 用户预设可访问机器人列表
- 需要在用户表存储，扩展性差

**结论**: 采用 BotAccess 表，按机器人配置，灵活性高

### 3. 团队实现

```
Team {
  id: string
  name: string
  created_at: datetime
}

TeamMember {
  team_id: string
  user_id: string
}
```

### 4. API 设计

**认证相关**:
- `POST /api/auth/login` - 内部用户登录，返回 JWT
- `POST /api/auth/logout` - 登出

**用户相关**:
- `GET /api/users/me` - 获取当前用户信息
- `GET /api/users/available-bots` - 获取当前用户可用的机器人列表

**团队相关** (仅管理员):
- `GET /api/teams` - 获取团队列表
- `POST /api/teams` - 创建团队
- `PUT /api/teams/{id}` - 更新团队
- `DELETE /api/teams/{id}` - 删除团队
- `POST /api/teams/{id}/members` - 添加团队成员
- `DELETE /api/teams/{id}/members/{user_id}` - 移除团队成员

**机器人权限相关** (仅管理员):
- `GET /api/admin/bots/{bot_id}/access` - 获取机器人访问配置
- `PUT /api/admin/bots/{bot_id}/access` - 更新机器人访问配置

### 5. JWT Token 结构

```json
{
  "sub": "user_id",
  "role": "internal|admin",
  "team_ids": ["team1", "team2"],
  "exp": timestamp
}
```

## Risks / Trade-offs

- **风险**: 匿名用户通过伪造 session 访问非默认机器人
- **处理**: 机器人ACL在后端验证，前端传bot_id不可信

- **风险**: 删除团队后成员的团队权限
- **处理**: 删除团队时级联删除TeamMember记录

## Open Questions

- 内部用户如何创建？（管理员后台手动添加，还是注册流程？）
- 匿名用户会话是否保留访问记录？

## Why

目前智能客服系统只有一个机器人配置，所有用户都使用同一个机器人。未来可能需要多个不同配置的机器人（如医疗客服、电商客服、IT服务客服等）。需要支持：
1. Admin 可以设置默认机器人
2. 客户端用户可以根据需要选择使用哪个机器人
3. 未登录用户只能使用 Admin 设置的默认机器人
4. 登录用户可以自主切换机器人
5. **不同机器人的知识库和 QA 数据相互隔离**

## What Changes

1. **数据库变更**
   - `bots` 表添加 `is_default` 字段，用于标识默认机器人
   - 添加 API 支持设置/获取默认机器人

2. **Admin 后台**
   - Bot 列表页面添加"设为默认"按钮
   - 显示当前默认机器人的标识

3. **客户端聊天页面**
   - 未登录用户：自动使用默认机器人（不显示切换选项）
   - 已登录用户：显示机器人下拉列表，可自主切换

4. **聊天 API 变更**
   - `/api/chat` 支持不传 `bot_id`（自动使用默认机器人）
   - `/api/admin/bots/default` - 获取/设置默认机器人
   - `/api/bots` - 获取所有可用水机器人列表

## Capabilities

### New Capabilities
- `default-bot`: 默认机器人设置与管理
- `bot-selection`: 客户端机器人选择功能
- `multi-bot-api`: 多机器人支持的后端 API

### Modified Capabilities
- （无，现有 bot-management 规格不需要变更）

## Impact

- **数据库**: 需要执行 ALTER TABLE 添加 `is_default` 字段
- **API**: 新增 `/api/admin/bots/default` 和 `/api/bots` 端点
- **前端**: 客户端 ChatPage 和 HistoryPage 需要支持动态 bot_id
- **认证**: 需要识别用户登录状态，未登录用户不能切换机器人
- **知识库隔离**: 已通过 ChromaDB collection 命名（`kb_chunks_{bot_id}`）和 SQLite `bot_id` 字段实现，无需额外变更

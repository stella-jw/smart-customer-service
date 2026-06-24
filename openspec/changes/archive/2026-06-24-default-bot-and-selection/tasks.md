## 1. Database Migration

- [x] 1.1 Add `is_default` column to `bots` table: `ALTER TABLE bots ADD COLUMN is_default BOOLEAN DEFAULT 0`
- [x] 1.2 Create database migration script `migrations/add_default_bot_column.py`

## 2. Backend API - Default Bot CRUD

- [x] 2.1 Add `is_default` field to Bot SQLAlchemy model
- [x] 2.2 Update `get_bot` function to include `is_default` in query results
- [x] 2.3 Implement `set_default_bot(db, bot_id)` function in crud.py
- [x] 2.4 Implement `get_default_bot(db)` function in crud.py
- [x] 2.5 Add `GET /api/admin/bots/default` endpoint in admin router
- [x] 2.6 Add `PUT /api/admin/bots/default/{bot_id}` endpoint in admin router

## 3. Backend API - Bot List

- [x] 3.1 Add `GET /api/bots` endpoint for public bot list
- [x] 3.2 Update `get_all_bots` to include `is_default` in response

## 4. Backend API - Chat with Optional bot_id

- [x] 4.1 Make `bot_id` optional in ChatRequest model
- [x] 4.2 If `bot_id` not provided, fetch and use default bot
- [x] 4.3 Validate `bot_id` exists if provided
- [x] 4.4 Update chat endpoint to handle missing bot_id gracefully

## 5. Admin Frontend - Bot List Page

- [x] 5.1 Add "Set as Default" button to bot list item
- [x] 5.2 Show "默认" badge on top-right corner of default bot card
- [x] 5.3 Call `PUT /api/admin/bots/default/{bot_id}` when setting default
- [x] 5.4 Disable delete button for default bot (show tooltip: "无法删除默认机器人")
- [x] 5.5 API returns error when attempting to delete default bot: "无法删除默认机器人，请先设置另一个机器人为默认"

## 5b. Admin Frontend - Add Bot Form

- [x] 5b.1 Add "设为默认" checkbox at bottom of Add Bot form
- [x] 5b.2 When creating first bot, show confirmation dialog after success
- [x] 5b.3 Dialog content: "您还没有设置默认机器人。客户在聊天窗口时，如果没有设置默认机器人，将会看到报错信息。"
- [x] 5b.4 Dialog buttons: "取消" (close, don't set default) | "确认" (set as default)
- [x] 5b.5 If checkbox was checked during form submit, skip dialog and set as default directly

## 6. Client Frontend - Bot Selector

- [x] 6.1 Create `BotSelector.vue` component (BotSwitcher.vue already exists)
- [x] 6.2 Fetch available bots from `GET /api/bots`
- [x] 6.3 Show bot selector only for authenticated users
- [x] 6.4 Unauthenticated users automatically use default bot
- [x] 6.5 Persist selected bot in localStorage for authenticated users

## 7. Frontend - Chat Page Integration

- [x] 7.1 Update ChatPage to use selected bot_id
- [x] 7.2 Update HistoryPage to use selected bot_id
- [x] 7.3 If no bot selected and user is logged in, show selector
- [x] 7.4 If no bot selected and user is not logged in, use default bot

## 8. Testing

- [ ] 8.1 Test database migration
- [ ] 8.2 Test setting/getting default bot via API
- [ ] 8.3 Test chat with default bot (no bot_id)
- [ ] 8.4 Test chat with specific bot_id
- [ ] 8.5 Test bot selector in client UI
- [ ] 8.6 Test unauthenticated user uses default bot

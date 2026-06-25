## 1. Database

- [x] 1.1 Add `system_prompt` column to `BotConfiguration` table (Text type, nullable)
- [x] 1.2 Update model definition in `backend/db/sqlite/models.py`

## 2. Backend API

- [x] 2.1 Add `system_prompt` field to `BotConfigRequest` Pydantic model
- [x] 2.2 Update `update_bot_config` to accept `system_prompt`
- [x] 2.3 Update chat API to pass `system_prompt` to LLM
- [x] 2.4 Add `get_default_system_prompt(industry_type, personality)` function

## 3. Frontend - BotConfigPage

- [x] 3.1 Add system prompt textarea to bot configuration form
- [x] 3.2 Add character count display (max 1200)
- [x] 3.3 Add "恢复默认" button to reset to default prompt
- [x] 3.4 Show default prompt preview based on industry_type and personality
- [x] 3.5 Add system prompt validation (only Chinese, English, numbers, punctuation, email, phone)

## 4. LLM Integration

- [x] 4.1 Update LangGraph generate node to accept `system_prompt` parameter
- [x] 4.2 Pass `system_prompt` to LLM as `system` parameter
- [x] 4.3 Fall back to default prompt when `system_prompt` is empty

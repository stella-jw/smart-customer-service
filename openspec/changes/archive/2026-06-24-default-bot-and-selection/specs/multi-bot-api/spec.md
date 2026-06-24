# Multi-Bot API

## ADDED Requirements

### Requirement: Chat API supports optional bot_id
The `/api/chat` endpoint SHALL accept requests without a bot_id, defaulting to the system default bot.

#### Scenario: Chat without bot_id uses default
- **WHEN** POST /api/chat is called without bot_id field
- **THEN** the system uses the default bot for processing

#### Scenario: Chat with bot_id uses specified bot
- **WHEN** POST /api/chat is called with a valid bot_id
- **THEN** the specified bot is used for processing

#### Scenario: Chat with invalid bot_id returns error
- **WHEN** POST /api/chat is called with a non-existent bot_id
- **THEN** system returns 404 error

### Requirement: Admin can get default bot
The `/api/admin/bots/default` GET endpoint SHALL return the current default bot information.

#### Scenario: Get default bot
- **WHEN** GET /api/admin/bots/default is called
- **THEN** returns the default bot's id and name

### Requirement: Admin can set default bot
The `/api/admin/bots/default/{bot_id}` PUT endpoint SHALL set the specified bot as the default.

#### Scenario: Set default bot
- **WHEN** PUT /api/admin/bots/default/{bot_id} is called with valid bot_id
- **THEN** that bot becomes the default and returns success

#### Scenario: Set default with invalid bot_id
- **WHEN** PUT /api/admin/bots/default/{bot_id} is called with non-existent bot_id
- **THEN** returns 404 error

### Requirement: Public bot list API
The `/api/bots` GET endpoint SHALL return a list of all available bots for client selection.

#### Scenario: Get available bots
- **WHEN** GET /api/bots is called
- **THEN** returns list of bots with id and name

### Requirement: Bots table has is_default column
The bots database table SHALL have an is_default BOOLEAN column to track the default bot.

#### Scenario: Default flag stored correctly
- **WHEN** a bot is set as default
- **THEN** is_default=TRUE is stored in database
- **AND** previous default bot has is_default=FALSE

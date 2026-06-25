## ADDED Requirements

### Requirement: Bot has configurable system prompt
The system SHALL allow administrators to configure a system prompt for each bot. This prompt SHALL be used when calling the LLM to generate responses.

#### Scenario: Admin sets system prompt
- **WHEN** admin configures bot with system prompt "你是一个专业的电商客服..."
- **THEN** LLM SHALL receive "你是一个专业的电商客服..." as the system parameter

#### Scenario: Admin leaves system prompt empty
- **WHEN** admin does not configure system prompt
- **THEN** system SHALL use a default prompt based on industry_type and personality setting

#### Scenario: Default prompt based on industry and personality
- **WHEN** admin creates a new bot with industry "ecommerce" and personality "professional"
- **THEN** system SHALL populate default prompt "你是一家电商平台的专业客服助手，精通商品知识、订单处理和售后流程..."

### Requirement: System prompt is editable in bot configuration page
The bot configuration page SHALL provide a text input for system prompt with support for multi-line text.

#### Scenario: Edit system prompt
- **WHEN** admin navigates to bot configuration page
- **THEN** system SHALL display a textarea for system prompt input
- **AND** textarea SHALL support maximum 1200 characters

#### Scenario: System prompt validation accepts valid characters
- **WHEN** admin enters "你好，我是电商客服，支持邮箱 test@example.com 和电话 138-1234-5678"
- **THEN** system SHALL accept the input

#### Scenario: System prompt validation rejects invalid characters
- **WHEN** admin enters text containing backticks or code symbols like "\`\`\`"
- **THEN** system SHALL reject the input with error message "系统提示词不能包含特殊符号"

### Requirement: System prompt is stored per bot
Each bot SHALL have its own system prompt configuration stored in the database.

#### Scenario: Different bots have different prompts
- **WHEN** bot A has system prompt "你是一个医疗助手..."
- **AND** bot B has system prompt "你是一个IT技术支持..."
- **THEN** bot A's conversations SHALL use the medical prompt
- **AND** bot B's conversations SHALL use the IT support prompt

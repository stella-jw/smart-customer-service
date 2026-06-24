# Default Bot

## ADDED Requirements

### Requirement: Admin can set default bot
Admin SHALL be able to set any existing bot as the default bot via the Admin interface. Only one bot can be default at a time.

#### Scenario: Set bot as default from list
- **WHEN** Admin clicks "Set as Default" button on a bot in the bot list
- **THEN** that bot is marked as default and previous default bot loses default status

#### Scenario: Default bot indicator
- **WHEN** Admin views the bot list
- **THEN** the current default bot card displays a "默认" badge on the top-right corner

### Requirement: First bot prompts for default setting
When Admin adds the first bot to an empty system, the system SHALL prompt to confirm setting it as the default bot.

#### Scenario: First bot creation prompts for default
- **WHEN** Admin successfully creates the first bot (system has no bots before)
- **THEN** a confirmation dialog appears with message: "您还没有设置默认机器人。客户在聊天窗口时，如果没有设置默认机器人，将会看到报错信息。"
- **AND** dialog shows "取消" and "确认" buttons

#### Scenario: Confirm first bot as default
- **WHEN** Admin clicks "确认" in the first-bot dialog
- **THEN** the newly created bot is set as the default bot

#### Scenario: Cancel first bot default
- **WHEN** Admin clicks "取消" in the first-bot dialog
- **THEN** no bot is set as default
- **AND** Admin can manually set default later from bot list

### Requirement: Add Bot form has default checkbox
The Add Bot form SHALL include a "设为默认" checkbox at the bottom, unchecked by default.

#### Scenario: Default checkbox in form
- **WHEN** Admin opens the Add Bot form
- **THEN** a "设为默认" checkbox is visible at the bottom
- **AND** it is unchecked by default

### Requirement: System has a default bot
The system SHALL always have exactly one default bot. If no bot is explicitly set as default, the first created bot becomes the default.

#### Scenario: First bot is default
- **WHEN** no default bot exists and the first bot is created
- **THEN** that bot automatically becomes the default

### Requirement: Cannot delete default bot
The system SHALL NOT allow deletion of the default bot unless another bot is set as default first.

#### Scenario: Delete default bot blocked
- **WHEN** Admin attempts to delete the default bot
- **THEN** system returns error with message "无法删除默认机器人，请先设置另一个机器人为默认"
- **AND** bot is not deleted

#### Scenario: Delete default bot after switching
- **WHEN** Admin first sets another bot as default, then deletes the previous default
- **THEN** deletion succeeds

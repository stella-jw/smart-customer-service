# Bot Management

## ADDED Requirements

### Requirement: Admin can view bot list
The system SHALL display all bots in a list with key information.

#### Scenario: Display bot list
- **WHEN** admin navigates to Bot management page
- **THEN** system shows list of all bots with name, industry, status, document count, QA count

#### Scenario: Empty bot list
- **WHEN** admin has no bots
- **THEN** system shows empty state with "创建第一个机器人" prompt

---

### Requirement: Admin can create new bot
The system SHALL allow admin to create a new bot with name and industry type.

#### Scenario: Successful bot creation
- **WHEN** admin fills name and industry, clicks "创建"
- **THEN** system creates bot and shows it in list

#### Scenario: Bot limit reached
- **WHEN** admin has 5 bots and clicks "创建机器人"
- **THEN** button is disabled with tooltip "已达上限"

#### Scenario: Duplicate bot name
- **WHEN** admin creates bot with existing name
- **THEN** system returns 400 error "机器人名称已存在"

---

### Requirement: Admin can delete bot
The system SHALL allow admin to delete a bot after confirmation.

#### Scenario: Delete bot confirmation
- **WHEN** admin clicks delete on a bot
- **THEN** system shows confirmation modal "确定删除机器人 {name}？此操作不可恢复。"

#### Scenario: Delete with associated data
- **WHEN** admin deletes bot with documents and QA pairs
- **THEN** system deletes bot and all associated data (documents, QA pairs, ChromaDB collections)

---

### Requirement: Admin can switch current bot
The system SHALL allow admin to switch between bots using a dropdown.

#### Scenario: Switch bot via dropdown
- **WHEN** admin selects different bot from dropdown
- **THEN** system updates current bot and refreshes page data

#### Scenario: Switch persists after refresh
- **WHEN** admin switches to bot B, then refreshes page
- **THEN** system still shows bot B as selected

---

### Requirement: Bot count is limited to 5
The system SHALL enforce a maximum of 5 bots per installation.

#### Scenario: Show current count
- **WHEN** admin views bot management
- **THEN** system displays "X/5 机器人" count

#### Scenario: Disable add button at limit
- **WHEN** bot count reaches 5
- **THEN** "添加机器人" button is disabled with visual indication

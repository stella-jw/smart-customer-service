# Bot Selection

## ADDED Requirements

### Requirement: Unauthenticated users use default bot
Unauthenticated (not logged in) users SHALL automatically use the system default bot for all conversations.

#### Scenario: Unauthenticated user gets default bot
- **WHEN** an unauthenticated user sends a message without specifying bot_id
- **THEN** the system uses the default bot for processing

### Requirement: Authenticated users can select bot
Authenticated users SHALL be able to select which bot to use from a dropdown list in the client interface.

#### Scenario: User sees bot selector
- **WHEN** an authenticated user opens the chat page
- **THEN** a bot selector dropdown is displayed with all available bots

#### Scenario: User switches bot
- **WHEN** user selects a different bot from the dropdown
- **THEN** subsequent messages use the selected bot

### Requirement: Client shows bot list
The client SHALL fetch and display the list of available bots from the API.

#### Scenario: Fetch bot list
- **WHEN** client page loads
- **THEN** it fetches available bots from GET /api/bots endpoint

### Requirement: Bot selection persists
The selected bot SHALL persist across page refreshes for authenticated users.

#### Scenario: Bot selection persists
- **WHEN** user selects a bot and refreshes the page
- **THEN** the same bot remains selected

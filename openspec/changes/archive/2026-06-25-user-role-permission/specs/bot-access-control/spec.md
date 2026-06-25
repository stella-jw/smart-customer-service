## ADDED Requirements

### Requirement: Bot has configurable access control
Each bot SHALL have an access control configuration determining which users can access it.

#### Scenario: Access type "all"
- **WHEN** bot access_type is set to "all"
- **THEN** all users (including anonymous) SHALL have access to the bot

#### Scenario: Access type "specific_users"
- **WHEN** bot access_type is set to "specific_users"
- **THEN** only users in allowed_users list SHALL have access

#### Scenario: Access type "specific_teams"
- **WHEN** bot access_type is set to "specific_teams"
- **THEN** only users belonging to teams in allowed_teams list SHALL have access

### Requirement: Admin can configure bot access
Admin SHALL be able to view and update bot access configuration.

#### Scenario: Admin views bot access config
- **WHEN** admin requests bot access configuration
- **THEN** system SHALL return current access_type, allowed_users, and allowed_teams

#### Scenario: Admin updates bot access config
- **WHEN** admin updates bot access configuration
- **THEN** system SHALL persist the new configuration

### Requirement: Access check is enforced server-side
The system SHALL verify bot access permissions on every chat request, regardless of client-side bot_id.

#### Scenario: Chat with unauthorized bot
- **WHEN** user requests chat with a bot they don't have access to
- **THEN** system SHALL return 403 Forbidden

#### Scenario: Chat with authorized bot
- **WHEN** user requests chat with an authorized bot
- **THEN** system SHALL process the chat request

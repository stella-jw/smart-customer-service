## ADDED Requirements

### Requirement: System distinguishes three user roles
The system SHALL distinguish between three user roles: anonymous, internal, and admin.

#### Scenario: Anonymous user identification
- **WHEN** a user without valid credentials accesses the system
- **THEN** system SHALL identify the user as anonymous

#### Scenario: Internal user identification
- **WHEN** a user with valid internal credentials but non-admin role accesses the system
- **THEN** system SHALL identify the user as internal

#### Scenario: Admin user identification
- **WHEN** a user with valid admin credentials accesses the system
- **THEN** system SHALL identify the user as admin

### Requirement: Only admin can access admin backend
The system SHALL block non-admin users from accessing admin backend endpoints.

#### Scenario: Anonymous user blocked from admin
- **WHEN** anonymous user attempts to access any /api/admin/* endpoint
- **THEN** system SHALL return 403 Forbidden

#### Scenario: Internal user blocked from admin
- **WHEN** internal user attempts to access any /api/admin/* endpoint
- **THEN** system SHALL return 403 Forbidden

#### Scenario: Admin user allowed access
- **WHEN** admin user accesses /api/admin/* endpoint
- **THEN** system SHALL allow the request

### Requirement: Anonymous user uses default bot only
The system SHALL restrict anonymous users to only use the default bot for conversations.

#### Scenario: Anonymous user bot availability
- **WHEN** anonymous user requests available bots list
- **THEN** system SHALL return only the default bot

### Requirement: Internal user can choose from authorized bots
The system SHALL return only bots that the internal user has permission to access.

#### Scenario: Internal user bot availability
- **WHEN** internal user requests available bots list
- **THEN** system SHALL return bots where user is in allowed_users or user's team is in allowed_teams or access_type is "all"

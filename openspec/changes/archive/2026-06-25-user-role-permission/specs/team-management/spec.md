## ADDED Requirements

### Requirement: Admin can create teams
The system SHALL allow admins to create teams with a name.

#### Scenario: Admin creates team
- **WHEN** admin creates a new team with name
- **THEN** system SHALL create team record and return team_id

### Requirement: Admin can manage team members
The system SHALL allow admins to add and remove users from teams.

#### Scenario: Admin adds user to team
- **WHEN** admin adds a user to a team
- **THEN** system SHALL create TeamMember record linking user and team

#### Scenario: Admin removes user from team
- **WHEN** admin removes a user from a team
- **THEN** system SHALL delete the TeamMember record

#### Scenario: Admin deletes team
- **WHEN** admin deletes a team
- **THEN** system SHALL delete the team and all related TeamMember records

### Requirement: User can view their team memberships
The system SHALL allow users to view which teams they belong to.

#### Scenario: User views their teams
- **WHEN** user requests their team memberships
- **THEN** system SHALL return list of teams the user belongs to

### Requirement: Team deletion cascades to access permissions
When a team is deleted, users from that team lose team-based bot access.

#### Scenario: Team deleted, team-based bot access revoked
- **WHEN** a team with bot access is deleted
- **THEN** users from that team SHALL NOT have access via that team anymore

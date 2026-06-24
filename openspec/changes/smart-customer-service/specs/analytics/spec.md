## ADDED Requirements

### Requirement: Conversation Analytics
The system SHALL track and analyze conversation metrics.

#### Scenario: Conversation counting
- **WHEN** user sends a message
- **THEN** conversation is logged with timestamp, user_id, source

#### Scenario: Daily conversation stats
- **WHEN** admin views analytics
- **THEN** daily conversation counts are displayed as a line chart

### Requirement: Popular Query Analysis
The system SHALL identify most frequently asked questions.

#### Scenario: Top queries report
- **WHEN** admin views analytics dashboard
- **THEN** top 10 most frequent questions are listed
- **AND** each shows usage count and satisfaction rate

### Requirement: Satisfaction Tracking
The system SHALL track user satisfaction through ratings.

#### Scenario: Satisfaction calculation
- **WHEN** calculating satisfaction rate
- **THEN** average of all ratings for QA-sourced responses is computed
- **AND** displayed as percentage

### Requirement: Analytics API
The system SHALL provide an API endpoint for analytics data.

#### Scenario: Analytics endpoint
- **WHEN** GET `/api/admin/analytics` is called
- **THEN** returns JSON with: total_conversations, daily_stats, top_queries, satisfaction_rate

### Requirement: Data Export
The system SHALL allow admins to export analytics data.

#### Scenario: Export as CSV
- **WHEN** admin requests export
- **THEN** system generates CSV with conversation logs

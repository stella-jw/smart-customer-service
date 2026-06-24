# Admin Auth

## ADDED Requirements

### Requirement: Admin can register account
The system SHALL allow creating admin accounts with username and password.

#### Scenario: Successful registration
- **WHEN** admin submits valid username and password (min 8 chars)
- **THEN** system creates account with bcrypt-hashed password and returns success

#### Scenario: Username already exists
- **WHEN** admin submits username that already exists
- **THEN** system returns 400 error with message "用户名已存在"

#### Scenario: Password too short
- **WHEN** admin submits password with less than 8 characters
- **THEN** system returns 400 error with message "密码至少8位"

---

### Requirement: Admin can login
The system SHALL authenticate admin users and return JWT token on valid credentials.

#### Scenario: Successful login
- **WHEN** admin submits correct username and password
- **THEN** system returns JWT token with 24h expiry

#### Scenario: Wrong password
- **WHEN** admin submits correct username but wrong password
- **THEN** system returns 401 error with message "用户名或密码错误"

#### Scenario: User not found
- **WHEN** admin submits non-existent username
- **THEN** system returns 401 error with message "用户名或密码错误"

---

### Requirement: Admin can verify token
The system SHALL validate JWT tokens on protected endpoints.

#### Scenario: Valid token
- **WHEN** request includes valid Authorization header with Bearer token
- **THEN** system extracts admin_id and allows request to proceed

#### Scenario: Expired token
- **WHEN** request includes expired JWT token
- **THEN** system returns 401 error with message "Token已过期"

#### Scenario: Invalid token format
- **WHEN** request includes malformed Authorization header
- **THEN** system returns 401 error with message "无效的Token"

---

### Requirement: Admin can logout
The system SHALL allow admin to invalidate their token (client-side token removal).

#### Scenario: Logout request
- **WHEN** admin calls logout endpoint
- **THEN** client removes token from storage (server-side token blacklist optional for v1)

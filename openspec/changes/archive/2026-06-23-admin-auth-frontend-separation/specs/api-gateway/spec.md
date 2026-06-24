# API Gateway

## ADDED Requirements

### Requirement: User API is public
The system SHALL allow unauthenticated access to user-facing API endpoints.

#### Scenario: Public chat API
- **WHEN** unauthenticated request calls `POST /api/chat`
- **THEN** system processes request and returns response

#### Scenario: Public history API
- **WHEN** unauthenticated request calls `GET /api/history/{session_id}`
- **THEN** system processes request and returns response

#### Scenario: Public rate API
- **WHEN** unauthenticated request calls `POST /api/rate`
- **THEN** system processes request and returns success

---

### Requirement: Admin API requires authentication
The system SHALL reject unauthenticated requests to admin API endpoints.

#### Scenario: Unauthenticated admin bot list
- **WHEN** unauthenticated request calls `GET /api/admin/bots`
- **THEN** system returns 401 error with message "需要管理员登录"

#### Scenario: Unauthenticated admin document upload
- **WHEN** unauthenticated request calls `POST /api/admin/documents`
- **THEN** system returns 401 error with message "需要管理员登录"

#### Scenario: Unauthenticated admin QA
- **WHEN** unauthenticated request calls any `/api/admin/qa/*`
- **THEN** system returns 401 error with message "需要管理员登录"

---

### Requirement: Authenticated admin can access protected API
The system SHALL allow authenticated admin users to access protected API endpoints.

#### Scenario: Authenticated admin access
- **WHEN** authenticated admin includes valid JWT in request header
- **THEN** system processes request and returns data

#### Scenario: Admin accessing wrong bot
- **WHEN** admin token is valid but requests data for non-owned bot
- **THEN** system validates bot ownership and returns appropriate response (v1: skip ownership check)

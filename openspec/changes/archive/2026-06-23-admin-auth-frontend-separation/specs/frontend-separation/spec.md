# Frontend Separation

## ADDED Requirements

### Requirement: User frontend is login-free
The system SHALL provide a user-facing frontend that requires no authentication.

#### Scenario: Direct access to user chat
- **WHEN** user navigates to `/` or `/user/chat`
- **THEN** user sees chat interface immediately without login

#### Scenario: Direct access to user history
- **WHEN** user navigates to `/user/history`
- **THEN** user sees conversation history without login

---

### Requirement: Admin frontend requires login
The system SHALL provide an admin frontend that requires valid admin authentication.

#### Scenario: Unauthenticated access to admin
- **WHEN** unauthenticated user navigates to `/admin/*`
- **THEN** system redirects to `/admin/login` page

#### Scenario: Authenticated access to admin
- **WHEN** authenticated admin navigates to `/admin/*`
- **THEN** system shows admin dashboard/content

#### Scenario: Session expired
- **WHEN** admin's JWT token expires while using admin panel
- **THEN** system redirects to `/admin/login` with message "登录已过期"

---

### Requirement: Admin login page
The system SHALL provide a dedicated login page for admin users.

#### Scenario: Display login form
- **WHEN** user navigates to `/admin/login`
- **THEN** system displays username and password form

#### Scenario: Failed login
- **WHEN** admin submits invalid credentials
- **THEN** system shows error message and allows retry

---

### Requirement: Frontend projects are independent
The user frontend and admin frontend SHALL be separate projects that can be deployed independently.

#### Scenario: User frontend deployment
- **WHEN** deploying user frontend
- **THEN** it only contains user-facing pages (chat, history)

#### Scenario: Admin frontend deployment
- **WHEN** deploying admin frontend
- **THEN** it only contains admin pages (dashboard, knowledge, QA, config, login)

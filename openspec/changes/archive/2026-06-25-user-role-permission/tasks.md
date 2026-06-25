## 1. Database Models

- [x] 1.1 Add User model (id, username, password_hash, role, team_ids, created_at)
- [x] 1.2 Add Team model (id, name, created_at)
- [x] 1.3 Add TeamMember model (team_id, user_id)
- [x] 1.4 Add BotAccess model (bot_id, access_type, allowed_users, allowed_teams)
- [x] 1.5 Add migration script for new tables

## 2. Backend - Auth & User APIs

- [x] 2.1 Implement JWT token generation and validation
- [x] 2.2 Add POST /api/auth/login endpoint for internal users
- [x] 2.3 Add POST /api/auth/logout endpoint
- [x] 2.4 Add GET /api/users/me endpoint
- [x] 2.5 Add GET /api/users/available-bots endpoint (returns bots user can access)

## 3. Backend - Admin Team APIs

- [x] 3.1 Add GET /api/teams endpoint
- [x] 3.2 Add POST /api/teams endpoint (create team)
- [x] 3.3 Add PUT /api/teams/{id} endpoint (update team)
- [x] 3.4 Add DELETE /api/teams/{id} endpoint (delete team with cascade)
- [x] 3.5 Add POST /api/teams/{id}/members endpoint (add user to team)
- [x] 3.6 Add DELETE /api/teams/{id}/members/{user_id} endpoint (remove user)
- [x] 3.7 Add admin-only middleware to protect team APIs

## 4. Backend - Bot Access Control APIs

- [x] 4.1 Add GET /api/admin/bots/{bot_id}/access endpoint
- [x] 4.2 Add PUT /api/admin/bots/{bot_id}/access endpoint
- [x] 4.3 Implement check_bot_access() function for chat requests
- [x] 4.4 Add access validation to chat endpoint

## 5. Frontend - Auth & Login

- [x] 5.1 Update LoginPage to support internal user login (username/password)
- [x] 5.2 Add auth store for managing JWT token and user role
- [x] 5.3 Add authApi with login/logout methods
- [x] 5.4 Implement role-based route protection

## 6. Frontend - User & Bot Selection

- [x] 6.1 Update botStore to filter bots by user permissions
- [x] 6.2 Update BotSwitcher to only show accessible bots
- [x] 6.3 Hide bot switcher for anonymous users (use default bot only)

## 7. Frontend - Admin Team Management

- [x] 7.1 Create TeamsPage.vue for team CRUD operations
- [x] 7.2 Add team member management UI
- [x] 7.3 Create BotAccessPage.vue for configuring bot access
- [x] 7.4 Add route guard: only admin can access /admin/* routes

## 8. Admin Layout & Navigation

- [x] 8.1 Add "团队管理" nav item in AdminLayout (for admin only)
- [x] 8.2 Add "机器人权限" nav item in AdminLayout
- [x] 8.3 Update route configuration with admin role guard

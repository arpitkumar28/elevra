# Database Schema

The initial PostgreSQL schema covers:

- Identity: `users`, `roles`, `permissions`, `user_roles`, `role_permissions`
- Organizations: `organizations`
- Discovery: `opportunities`, `bookmarks`, `applications`
- Learning: `courses`, `lessons`, `notes`, `mock_tests`, `study_plans`
- AI: `ai_chats`
- Notifications: `notifications`
- Governance: `audit_logs`, `settings`, `analytics_events`

Migrations live in `services/backend/alembic`. PostgreSQL remains the system of record; Meilisearch
is a derived index and must be rebuilt from canonical records when necessary.

"""Initial production schema.

Revision ID: 20260718_0001
Revises:
Create Date: 2026-07-18
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260718_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id text PRIMARY KEY,
      email varchar(320) NOT NULL UNIQUE,
      full_name varchar(240) NOT NULL,
      password_hash varchar(512),
      avatar_url varchar(2048),
      graduation_year integer,
      locale varchar(16) NOT NULL DEFAULT 'en',
      timezone varchar(80) NOT NULL DEFAULT 'UTC',
      is_active boolean NOT NULL DEFAULT true,
      is_verified boolean NOT NULL DEFAULT false,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS roles (
      id text PRIMARY KEY,
      key varchar(80) NOT NULL UNIQUE,
      name varchar(160) NOT NULL,
      description text,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS permissions (
      id text PRIMARY KEY,
      key varchar(120) NOT NULL UNIQUE,
      description text NOT NULL,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS user_roles (
      user_id text NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      role_id text NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
      PRIMARY KEY (user_id, role_id)
    );
    CREATE TABLE IF NOT EXISTS role_permissions (
      role_id text NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
      permission_id text NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
      PRIMARY KEY (role_id, permission_id)
    );
    CREATE TABLE IF NOT EXISTS organizations (
      id text PRIMARY KEY,
      name varchar(240) NOT NULL,
      slug varchar(160) NOT NULL UNIQUE,
      website_url varchar(2048),
      metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS mock_tests (
      id text PRIMARY KEY,
      user_id text NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      exam_key varchar(120) NOT NULL,
      score_percent numeric(5,2) NOT NULL,
      analytics_json jsonb NOT NULL DEFAULT '{}'::jsonb,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS ai_chats (
      id text PRIMARY KEY,
      user_id text NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      agent_key varchar(80) NOT NULL,
      title varchar(240) NOT NULL,
      messages_json jsonb NOT NULL DEFAULT '[]'::jsonb,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS study_plans (
      id text PRIMARY KEY,
      user_id text NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      title varchar(240) NOT NULL,
      target_exam varchar(120),
      tasks_json jsonb NOT NULL DEFAULT '[]'::jsonb,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS settings (
      id text PRIMARY KEY,
      user_id text NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      key varchar(120) NOT NULL,
      value_json jsonb NOT NULL DEFAULT '{}'::jsonb,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS analytics_events (
      id text PRIMARY KEY,
      user_id text REFERENCES users(id) ON DELETE SET NULL,
      event_name varchar(160) NOT NULL,
      source varchar(80) NOT NULL,
      properties_json jsonb NOT NULL DEFAULT '{}'::jsonb,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_analytics_events_name ON analytics_events(event_name);
    """)


def downgrade() -> None:
    op.execute("""
    DROP TABLE IF EXISTS analytics_events, settings, study_plans, ai_chats,
      mock_tests, opportunities, organizations, role_permissions, user_roles,
      permissions, roles, users CASCADE;
    """)

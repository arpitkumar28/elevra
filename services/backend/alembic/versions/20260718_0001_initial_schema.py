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
    CREATE TABLE IF NOT EXISTS opportunities (
      id text PRIMARY KEY,
      organization_id text REFERENCES organizations(id),
      type varchar(40) NOT NULL,
      status varchar(40) NOT NULL DEFAULT 'pending_review',
      title varchar(320) NOT NULL,
      provider_name varchar(240) NOT NULL,
      description text NOT NULL,
      country varchar(80),
      grade_levels varchar[] NOT NULL DEFAULT '{}',
      tags varchar[] NOT NULL DEFAULT '{}',
      source_url varchar(2048),
      deadline_at varchar(40),
      popularity_score numeric(8,4) NOT NULL DEFAULT 0,
      metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS courses (
      id text PRIMARY KEY,
      title varchar(320) NOT NULL,
      slug varchar(180) NOT NULL UNIQUE,
      description text NOT NULL,
      subject varchar(120) NOT NULL,
      difficulty varchar(40) NOT NULL,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS lessons (
      id text PRIMARY KEY,
      course_id text NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
      title varchar(320) NOT NULL,
      content_url varchar(2048),
      position integer NOT NULL,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS notes (
      id text PRIMARY KEY,
      user_id text NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      lesson_id text REFERENCES lessons(id) ON DELETE SET NULL,
      title varchar(240) NOT NULL,
      body text NOT NULL,
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
    CREATE TABLE IF NOT EXISTS bookmarks (
      id text PRIMARY KEY,
      user_id text NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      opportunity_id text NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL,
      CONSTRAINT uq_bookmark_user_opportunity UNIQUE (user_id, opportunity_id)
    );
    CREATE TABLE IF NOT EXISTS notifications (
      id text PRIMARY KEY,
      user_id text NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      channel varchar(40) NOT NULL,
      title varchar(240) NOT NULL,
      body text NOT NULL,
      is_read boolean NOT NULL DEFAULT false,
      payload_json jsonb NOT NULL DEFAULT '{}'::jsonb,
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
    CREATE TABLE IF NOT EXISTS applications (
      id text PRIMARY KEY,
      user_id text NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      opportunity_id text NOT NULL REFERENCES opportunities(id),
      status varchar(80) NOT NULL DEFAULT 'draft',
      checklist_json jsonb NOT NULL DEFAULT '[]'::jsonb,
      created_at timestamptz NOT NULL,
      updated_at timestamptz NOT NULL
    );
    CREATE TABLE IF NOT EXISTS audit_logs (
      id text PRIMARY KEY,
      actor_user_id text REFERENCES users(id) ON DELETE SET NULL,
      action varchar(40) NOT NULL,
      resource_type varchar(120) NOT NULL,
      resource_id varchar(80),
      metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
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
    CREATE INDEX IF NOT EXISTS ix_opportunities_type_status_deadline
      ON opportunities(type, status, deadline_at);
    CREATE INDEX IF NOT EXISTS ix_analytics_events_name ON analytics_events(event_name);
    """)


def downgrade() -> None:
    op.execute("""
    DROP TABLE IF EXISTS analytics_events, settings, audit_logs, applications,
      study_plans, ai_chats,
      notifications, bookmarks, mock_tests, notes, lessons, courses, opportunities, organizations,
      role_permissions, user_roles, permissions, roles, users CASCADE;
    """)

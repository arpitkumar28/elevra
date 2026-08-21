-- Elevra's Supabase baseline. This reflects the active FastAPI SQLAlchemy
-- models; Alembic's older, conflicting roots are intentionally not replayed.
create extension if not exists vector;

create type public.exam_category as enum (
  'government', 'engineering', 'medical', 'management', 'university',
  'defence', 'banking', 'railway', 'teaching', 'state_exams', 'other'
);
create type public.publication_status as enum ('draft', 'published', 'archived');
create type public.opportunity_type as enum (
  'job', 'internship', 'scholarship', 'hackathon', 'competition',
  'fellowship', 'research', 'bootcamp', 'event', 'other'
);
create type public.opportunity_status as enum ('draft', 'published', 'closed', 'archived');

create table public.users (
  id varchar(36) primary key,
  name varchar(255) not null,
  email varchar(255) not null unique,
  password_hash varchar(255) not null,
  is_admin boolean not null default false,
  is_active boolean not null default true,
  role varchar(32) not null default 'student',
  email_verified boolean not null default false,
  locked_until timestamptz,
  created_at timestamptz not null default now()
);
create index ix_users_email on public.users (email);
create index ix_users_role on public.users (role);

create table public.student_profiles (
  id varchar(36) primary key,
  user_id varchar(36) not null unique references public.users(id) on delete cascade,
  goal text, bio text, display_name varchar(255), date_of_birth date,
  gender varchar(64), phone varchar(32), city varchar(128), state varchar(128),
  country varchar(128), education_level varchar(128), institution varchar(255),
  degree varchar(255), stream varchar(255), graduation_year integer,
  exam_interests jsonb not null default '[]'::jsonb,
  opportunity_interests jsonb not null default '[]'::jsonb,
  preferred_locations jsonb not null default '[]'::jsonb,
  remote_preference boolean not null default false,
  career_interests jsonb not null default '[]'::jsonb,
  target_roles jsonb not null default '[]'::jsonb,
  skills jsonb not null default '[]'::jsonb,
  experience_level varchar(64),
  notification_preferences jsonb not null default '{}'::jsonb
);
create index ix_student_profiles_user_id on public.student_profiles (user_id);

create table public.refresh_tokens (
  id varchar(36) primary key,
  user_id varchar(36) not null references public.users(id) on delete cascade,
  token_hash varchar(128) not null unique,
  session_id varchar(64), user_agent varchar(512), ip_address varchar(64),
  expires_at timestamptz not null, revoked_at timestamptz, replaced_by varchar(36),
  last_used_at timestamptz, created_at timestamptz not null default now(), updated_at timestamptz
);
create index ix_refresh_tokens_user_id on public.refresh_tokens (user_id);
create index ix_refresh_tokens_token_hash on public.refresh_tokens (token_hash);
create index ix_refresh_tokens_session_id on public.refresh_tokens (session_id);

create table public.account_tokens (
  id varchar(36) primary key,
  user_id varchar(36) not null references public.users(id) on delete cascade,
  purpose varchar(32) not null, token_hash varchar(64) not null unique,
  expires_at timestamptz not null, used_at timestamptz,
  created_at timestamptz not null default now()
);
create index ix_account_tokens_user_id on public.account_tokens (user_id);
create index ix_account_tokens_purpose on public.account_tokens (purpose);

create table public.exams (
  id varchar(36) primary key,
  name varchar(255) not null,
  slug varchar(255) not null unique,
  short_description varchar(512), description text,
  category public.exam_category not null,
  conducting_body varchar(255), official_website varchar(1024),
  eligibility_summary text, education_requirements text, age_limit varchar(255),
  application_start date, application_deadline date, exam_date date, result_date date,
  status public.publication_status not null default 'draft',
  source_url varchar(1024), source_name varchar(255),
  verified boolean not null default false, verified_at timestamptz,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index ix_exams_name on public.exams (name);
create index ix_exams_category on public.exams (category);
create index ix_exams_conducting_body on public.exams (conducting_body);
create index ix_exams_application_deadline on public.exams (application_deadline);
create index ix_exams_status on public.exams (status);
create index ix_exams_verified on public.exams (verified);

create table public.exam_syllabi (
  id varchar(36) primary key, exam_id varchar(255) not null references public.exams(id) on delete cascade,
  section_title varchar(255), content text, position integer default 0
);
create table public.exam_patterns (
  id varchar(36) primary key, exam_id varchar(255) not null references public.exams(id) on delete cascade,
  title varchar(255), description text, position integer default 0
);
create table public.exam_dates (
  id varchar(36) primary key, exam_id varchar(255) not null references public.exams(id) on delete cascade,
  title varchar(255), date varchar(255), notes text
);
create table public.exam_faqs (
  id varchar(36) primary key, exam_id varchar(255) not null references public.exams(id) on delete cascade,
  question varchar(1024), answer text
);
create index ix_exam_syllabi_exam_id on public.exam_syllabi (exam_id);
create index ix_exam_patterns_exam_id on public.exam_patterns (exam_id);
create index ix_exam_dates_exam_id on public.exam_dates (exam_id);
create index ix_exam_faqs_exam_id on public.exam_faqs (exam_id);

create table public.opportunities (
  id varchar(36) primary key,
  title varchar(255) not null, slug varchar(255) not null unique,
  type public.opportunity_type not null, organization varchar(255), description text,
  eligibility text, location varchar(255), remote boolean not null default false,
  application_url varchar(1024), source_url varchar(1024), deadline date,
  published_at timestamptz, status public.opportunity_status not null default 'draft',
  verified boolean not null default false, verified_at timestamptz,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index ix_opportunities_title on public.opportunities (title);
create index ix_opportunities_type on public.opportunities (type);
create index ix_opportunities_organization on public.opportunities (organization);
create index ix_opportunities_location on public.opportunities (location);
create index ix_opportunities_remote on public.opportunities (remote);
create index ix_opportunities_deadline on public.opportunities (deadline);
create index ix_opportunities_status on public.opportunities (status);
create index ix_opportunities_verified on public.opportunities (verified);

-- The FastAPI service is the sole database client. Prevent direct anon/authenticated
-- PostgREST access until explicit RLS policies are introduced.
alter table public.users enable row level security;
alter table public.student_profiles enable row level security;
alter table public.refresh_tokens enable row level security;
alter table public.account_tokens enable row level security;
alter table public.exams enable row level security;
alter table public.exam_syllabi enable row level security;
alter table public.exam_patterns enable row level security;
alter table public.exam_dates enable row level security;
alter table public.exam_faqs enable row level security;
alter table public.opportunities enable row level security;

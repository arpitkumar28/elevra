# Active ORM schema specification

Generated from `app.db.session.Base.metadata` and the model imports in `alembic/env.py`. This describes the active SQLAlchemy contract; it is not a claim that the migrations currently produce it.

## Tables

### `account_tokens`

| Column       | PostgreSQL type            | Nullability | Default                 | References                     |
| ------------ | -------------------------- | ----------- | ----------------------- | ------------------------------ |
| `id`         | `VARCHAR(36)`              | NOT NULL    | application: `<lambda>` | —                              |
| `user_id`    | `VARCHAR(36)`              | NOT NULL    | —                       | `users.id` (on delete CASCADE) |
| `purpose`    | `VARCHAR(32)`              | NOT NULL    | —                       | —                              |
| `token_hash` | `VARCHAR(64)`              | NOT NULL    | —                       | —                              |
| `expires_at` | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | —                       | —                              |
| `used_at`    | `TIMESTAMP WITH TIME ZONE` | NULL        | —                       | —                              |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | application: `<lambda>` | —                              |

Unique constraints:

- `token_hash`

Indexes:

- `ix_account_tokens_purpose` on `purpose`
- `ix_account_tokens_user_id` on `user_id`

### `applications`

| Column           | PostgreSQL type            | Nullability | Default              | References                     |
| ---------------- | -------------------------- | ----------- | -------------------- | ------------------------------ |
| `id`             | `VARCHAR(36)`              | NOT NULL    | application: `_id`   | —                              |
| `user_id`        | `VARCHAR(36)`              | NOT NULL    | —                    | `users.id` (on delete CASCADE) |
| `opportunity_id` | `VARCHAR(36)`              | NULL        | —                    | —                              |
| `title`          | `VARCHAR(255)`             | NOT NULL    | —                    | —                              |
| `organization`   | `VARCHAR(255)`             | NULL        | —                    | —                              |
| `external_url`   | `VARCHAR(2048)`            | NULL        | —                    | —                              |
| `status`         | `VARCHAR(32)`              | NOT NULL    | application: `saved` | —                              |
| `notes`          | `TEXT`                     | NULL        | —                    | —                              |
| `created_at`     | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`      | —                              |
| `updated_at`     | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`      | —                              |

Indexes:

- `ix_applications_opportunity_id` on `opportunity_id`
- `ix_applications_status` on `status`
- `ix_applications_user_id` on `user_id`

### `audit_logs`

| Column          | PostgreSQL type            | Nullability | Default             | References |
| --------------- | -------------------------- | ----------- | ------------------- | ---------- |
| `id`            | `VARCHAR(36)`              | NOT NULL    | application: `_id`  | —          |
| `actor_id`      | `VARCHAR(36)`              | NULL        | —                   | —          |
| `action`        | `VARCHAR(64)`              | NOT NULL    | —                   | —          |
| `entity`        | `VARCHAR(64)`              | NOT NULL    | —                   | —          |
| `entity_id`     | `VARCHAR(36)`              | NULL        | —                   | —          |
| `request_id`    | `VARCHAR(64)`              | NULL        | —                   | —          |
| `metadata_json` | `JSON`                     | NOT NULL    | application: `dict` | —          |
| `created_at`    | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`     | —          |

Indexes:

- `ix_audit_logs_action` on `action`
- `ix_audit_logs_actor_id` on `actor_id`
- `ix_audit_logs_entity` on `entity`
- `ix_audit_logs_entity_id` on `entity_id`
- `ix_audit_logs_request_id` on `request_id`

### `bookmarks`

| Column        | PostgreSQL type            | Nullability | Default            | References                     |
| ------------- | -------------------------- | ----------- | ------------------ | ------------------------------ |
| `id`          | `VARCHAR(36)`              | NOT NULL    | application: `_id` | —                              |
| `user_id`     | `VARCHAR(36)`              | NOT NULL    | —                  | `users.id` (on delete CASCADE) |
| `entity_type` | `VARCHAR(32)`              | NOT NULL    | —                  | —                              |
| `entity_id`   | `VARCHAR(36)`              | NOT NULL    | —                  | —                              |
| `created_at`  | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`    | —                              |

Unique constraints:

- `user_id`, `entity_type`, `entity_id`

Indexes:

- `ix_bookmarks_entity_id` on `entity_id`
- `ix_bookmarks_entity_type` on `entity_type`
- `ix_bookmarks_user_id` on `user_id`

### `courses`

| Column         | PostgreSQL type            | Nullability | Default              | References |
| -------------- | -------------------------- | ----------- | -------------------- | ---------- |
| `id`           | `VARCHAR(36)`              | NOT NULL    | application: `_id`   | —          |
| `title`        | `VARCHAR(255)`             | NOT NULL    | —                    | —          |
| `slug`         | `VARCHAR(255)`             | NOT NULL    | —                    | —          |
| `provider`     | `VARCHAR(255)`             | NOT NULL    | —                    | —          |
| `description`  | `TEXT`                     | NULL        | —                    | —          |
| `category`     | `VARCHAR(100)`             | NULL        | —                    | —          |
| `difficulty`   | `VARCHAR(50)`              | NULL        | —                    | —          |
| `duration`     | `VARCHAR(100)`             | NULL        | —                    | —          |
| `mode`         | `VARCHAR(50)`              | NULL        | —                    | —          |
| `skills`       | `JSON`                     | NOT NULL    | application: `list`  | —          |
| `certificate`  | `BOOLEAN`                  | NOT NULL    | application: `False` | —          |
| `course_url`   | `VARCHAR(2048)`            | NULL        | —                    | —          |
| `official_url` | `VARCHAR(2048)`            | NULL        | —                    | —          |
| `status`       | `VARCHAR(32)`              | NOT NULL    | application: `draft` | —          |
| `created_at`   | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`      | —          |
| `updated_at`   | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`      | —          |

Indexes:

- `ix_courses_category` on `category`
- `ix_courses_difficulty` on `difficulty`
- `ix_courses_mode` on `mode`
- `ix_courses_provider` on `provider`
- `ix_courses_slug` on `slug` (unique)
- `ix_courses_status` on `status`
- `ix_courses_title` on `title`

### `current_affairs`

| Column         | PostgreSQL type            | Nullability | Default              | References |
| -------------- | -------------------------- | ----------- | -------------------- | ---------- |
| `id`           | `VARCHAR(36)`              | NOT NULL    | application: `_id`   | —          |
| `title`        | `VARCHAR(320)`             | NOT NULL    | —                    | —          |
| `slug`         | `VARCHAR(255)`             | NOT NULL    | —                    | —          |
| `summary`      | `TEXT`                     | NOT NULL    | —                    | —          |
| `content`      | `TEXT`                     | NOT NULL    | —                    | —          |
| `category`     | `VARCHAR(100)`             | NOT NULL    | —                    | —          |
| `source`       | `VARCHAR(255)`             | NOT NULL    | —                    | —          |
| `source_url`   | `VARCHAR(2048)`            | NULL        | —                    | —          |
| `published_at` | `TIMESTAMP WITH TIME ZONE` | NULL        | —                    | —          |
| `status`       | `VARCHAR(32)`              | NOT NULL    | application: `draft` | —          |
| `created_at`   | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`      | —          |
| `updated_at`   | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`      | —          |

Indexes:

- `ix_current_affairs_category` on `category`
- `ix_current_affairs_published_at` on `published_at`
- `ix_current_affairs_slug` on `slug` (unique)
- `ix_current_affairs_status` on `status`
- `ix_current_affairs_title` on `title`

### `exam_dates`

| Column    | PostgreSQL type | Nullability | Default                 | References                     |
| --------- | --------------- | ----------- | ----------------------- | ------------------------------ |
| `id`      | `VARCHAR(36)`   | NOT NULL    | application: `<lambda>` | —                              |
| `exam_id` | `VARCHAR(255)`  | NOT NULL    | —                       | `exams.id` (on delete CASCADE) |
| `title`   | `VARCHAR(255)`  | NULL        | —                       | —                              |
| `date`    | `VARCHAR(255)`  | NULL        | —                       | —                              |
| `notes`   | `TEXT`          | NULL        | —                       | —                              |

Indexes:

- `ix_exam_dates_exam_id` on `exam_id`

### `exam_faqs`

| Column     | PostgreSQL type | Nullability | Default                 | References                     |
| ---------- | --------------- | ----------- | ----------------------- | ------------------------------ |
| `id`       | `VARCHAR(36)`   | NOT NULL    | application: `<lambda>` | —                              |
| `exam_id`  | `VARCHAR(255)`  | NOT NULL    | —                       | `exams.id` (on delete CASCADE) |
| `question` | `VARCHAR(1024)` | NULL        | —                       | —                              |
| `answer`   | `TEXT`          | NULL        | —                       | —                              |

Indexes:

- `ix_exam_faqs_exam_id` on `exam_id`

### `exam_patterns`

| Column        | PostgreSQL type | Nullability | Default                 | References                     |
| ------------- | --------------- | ----------- | ----------------------- | ------------------------------ |
| `id`          | `VARCHAR(36)`   | NOT NULL    | application: `<lambda>` | —                              |
| `exam_id`     | `VARCHAR(255)`  | NOT NULL    | —                       | `exams.id` (on delete CASCADE) |
| `title`       | `VARCHAR(255)`  | NULL        | —                       | —                              |
| `description` | `TEXT`          | NULL        | —                       | —                              |
| `position`    | `INTEGER`       | NULL        | application: `0`        | —                              |

Indexes:

- `ix_exam_patterns_exam_id` on `exam_id`

### `exam_syllabi`

| Column          | PostgreSQL type | Nullability | Default                 | References                     |
| --------------- | --------------- | ----------- | ----------------------- | ------------------------------ |
| `id`            | `VARCHAR(36)`   | NOT NULL    | application: `<lambda>` | —                              |
| `exam_id`       | `VARCHAR(255)`  | NOT NULL    | —                       | `exams.id` (on delete CASCADE) |
| `section_title` | `VARCHAR(255)`  | NULL        | —                       | —                              |
| `content`       | `TEXT`          | NULL        | —                       | —                              |
| `position`      | `INTEGER`       | NULL        | application: `0`        | —                              |

Indexes:

- `ix_exam_syllabi_exam_id` on `exam_id`

### `exams`

| Column                   | PostgreSQL type                                                                                                                                           | Nullability | Default                                | References |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | -------------------------------------- | ---------- |
| `id`                     | `VARCHAR(36)`                                                                                                                                             | NOT NULL    | application: `<lambda>`                | —          |
| `name`                   | `VARCHAR(255)`                                                                                                                                            | NOT NULL    | —                                      | —          |
| `slug`                   | `VARCHAR(255)`                                                                                                                                            | NOT NULL    | —                                      | —          |
| `short_description`      | `VARCHAR(512)`                                                                                                                                            | NULL        | —                                      | —          |
| `description`            | `TEXT`                                                                                                                                                    | NULL        | —                                      | —          |
| `category`               | `exam_category (`government`, `engineering`, `medical`, `management`, `university`, `defence`, `banking`, `railway`, `teaching`, `state_exams`, `other`)` | NOT NULL    | —                                      | —          |
| `conducting_body`        | `VARCHAR(255)`                                                                                                                                            | NULL        | —                                      | —          |
| `official_website`       | `VARCHAR(1024)`                                                                                                                                           | NULL        | —                                      | —          |
| `eligibility_summary`    | `TEXT`                                                                                                                                                    | NULL        | —                                      | —          |
| `education_requirements` | `TEXT`                                                                                                                                                    | NULL        | —                                      | —          |
| `age_limit`              | `VARCHAR(255)`                                                                                                                                            | NULL        | —                                      | —          |
| `application_start`      | `DATE`                                                                                                                                                    | NULL        | —                                      | —          |
| `application_deadline`   | `DATE`                                                                                                                                                    | NULL        | —                                      | —          |
| `exam_date`              | `DATE`                                                                                                                                                    | NULL        | —                                      | —          |
| `result_date`            | `DATE`                                                                                                                                                    | NULL        | —                                      | —          |
| `status`                 | `publication_status (`draft`, `published`, `archived`)`                                                                                                   | NOT NULL    | application: `PublicationStatus.draft` | —          |
| `source_url`             | `VARCHAR(1024)`                                                                                                                                           | NULL        | —                                      | —          |
| `source_name`            | `VARCHAR(255)`                                                                                                                                            | NULL        | —                                      | —          |
| `verified`               | `BOOLEAN`                                                                                                                                                 | NOT NULL    | application: `False`                   | —          |
| `verified_at`            | `TIMESTAMP WITH TIME ZONE`                                                                                                                                | NULL        | —                                      | —          |
| `created_at`             | `TIMESTAMP WITH TIME ZONE`                                                                                                                                | NOT NULL    | server: `now()`                        | —          |
| `updated_at`             | `TIMESTAMP WITH TIME ZONE`                                                                                                                                | NOT NULL    | server: `now()`                        | —          |

Indexes:

- `ix_exams_application_deadline` on `application_deadline`
- `ix_exams_category` on `category`
- `ix_exams_conducting_body` on `conducting_body`
- `ix_exams_name` on `name`
- `ix_exams_slug` on `slug` (unique)
- `ix_exams_status` on `status`
- `ix_exams_verified` on `verified`

### `notifications`

| Column       | PostgreSQL type            | Nullability | Default            | References                     |
| ------------ | -------------------------- | ----------- | ------------------ | ------------------------------ |
| `id`         | `VARCHAR(36)`              | NOT NULL    | application: `_id` | —                              |
| `user_id`    | `VARCHAR(36)`              | NOT NULL    | —                  | `users.id` (on delete CASCADE) |
| `type`       | `VARCHAR(64)`              | NOT NULL    | —                  | —                              |
| `title`      | `VARCHAR(255)`             | NOT NULL    | —                  | —                              |
| `body`       | `TEXT`                     | NOT NULL    | —                  | —                              |
| `read_at`    | `TIMESTAMP WITH TIME ZONE` | NULL        | —                  | —                              |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`    | —                              |

Indexes:

- `ix_notifications_type` on `type`
- `ix_notifications_user_id` on `user_id`

### `opportunities`

| Column            | PostgreSQL type                                                                                                                             | Nullability | Default                                | References |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | -------------------------------------- | ---------- |
| `id`              | `VARCHAR(36)`                                                                                                                               | NOT NULL    | application: `<lambda>`                | —          |
| `title`           | `VARCHAR(255)`                                                                                                                              | NOT NULL    | —                                      | —          |
| `slug`            | `VARCHAR(255)`                                                                                                                              | NOT NULL    | —                                      | —          |
| `type`            | `opportunity_type (`job`, `internship`, `scholarship`, `hackathon`, `competition`, `fellowship`, `research`, `bootcamp`, `event`, `other`)` | NOT NULL    | —                                      | —          |
| `organization`    | `VARCHAR(255)`                                                                                                                              | NULL        | —                                      | —          |
| `description`     | `TEXT`                                                                                                                                      | NULL        | —                                      | —          |
| `eligibility`     | `TEXT`                                                                                                                                      | NULL        | —                                      | —          |
| `location`        | `VARCHAR(255)`                                                                                                                              | NULL        | —                                      | —          |
| `remote`          | `BOOLEAN`                                                                                                                                   | NOT NULL    | application: `False`                   | —          |
| `application_url` | `VARCHAR(1024)`                                                                                                                             | NULL        | —                                      | —          |
| `source_url`      | `VARCHAR(1024)`                                                                                                                             | NULL        | —                                      | —          |
| `deadline`        | `DATE`                                                                                                                                      | NULL        | —                                      | —          |
| `published_at`    | `TIMESTAMP WITH TIME ZONE`                                                                                                                  | NULL        | —                                      | —          |
| `status`          | `opportunity_status (`draft`, `published`, `closed`, `archived`)`                                                                           | NOT NULL    | application: `OpportunityStatus.draft` | —          |
| `verified`        | `BOOLEAN`                                                                                                                                   | NOT NULL    | application: `False`                   | —          |
| `verified_at`     | `TIMESTAMP WITH TIME ZONE`                                                                                                                  | NULL        | —                                      | —          |
| `created_at`      | `TIMESTAMP WITH TIME ZONE`                                                                                                                  | NOT NULL    | server: `now()`                        | —          |
| `updated_at`      | `TIMESTAMP WITH TIME ZONE`                                                                                                                  | NOT NULL    | server: `now()`                        | —          |

Indexes:

- `ix_opportunities_deadline` on `deadline`
- `ix_opportunities_location` on `location`
- `ix_opportunities_organization` on `organization`
- `ix_opportunities_remote` on `remote`
- `ix_opportunities_slug` on `slug` (unique)
- `ix_opportunities_status` on `status`
- `ix_opportunities_title` on `title`
- `ix_opportunities_type` on `type`
- `ix_opportunities_verified` on `verified`

### `question_options`

| Column        | PostgreSQL type | Nullability | Default              | References                         |
| ------------- | --------------- | ----------- | -------------------- | ---------------------------------- |
| `id`          | `VARCHAR(36)`   | NOT NULL    | application: `_id`   | —                                  |
| `question_id` | `VARCHAR(36)`   | NOT NULL    | —                    | `questions.id` (on delete CASCADE) |
| `text`        | `TEXT`          | NOT NULL    | —                    | —                                  |
| `is_correct`  | `BOOLEAN`       | NOT NULL    | application: `False` | —                                  |
| `position`    | `INTEGER`       | NOT NULL    | application: `0`     | —                                  |

Indexes:

- `ix_question_options_question_id` on `question_id`

### `questions`

| Column        | PostgreSQL type | Nullability | Default            | References                     |
| ------------- | --------------- | ----------- | ------------------ | ------------------------------ |
| `id`          | `VARCHAR(36)`   | NOT NULL    | application: `_id` | —                              |
| `test_id`     | `VARCHAR(36)`   | NOT NULL    | —                  | `tests.id` (on delete CASCADE) |
| `text`        | `TEXT`          | NOT NULL    | —                  | —                              |
| `explanation` | `TEXT`          | NULL        | —                  | —                              |
| `position`    | `INTEGER`       | NOT NULL    | application: `0`   | —                              |

Indexes:

- `ix_questions_test_id` on `test_id`

### `refresh_tokens`

| Column         | PostgreSQL type            | Nullability | Default                 | References                     |
| -------------- | -------------------------- | ----------- | ----------------------- | ------------------------------ |
| `id`           | `VARCHAR(36)`              | NOT NULL    | application: `<lambda>` | —                              |
| `user_id`      | `VARCHAR(36)`              | NOT NULL    | —                       | `users.id` (on delete CASCADE) |
| `token_hash`   | `VARCHAR(128)`             | NOT NULL    | —                       | —                              |
| `session_id`   | `VARCHAR(64)`              | NULL        | —                       | —                              |
| `user_agent`   | `VARCHAR(512)`             | NULL        | —                       | —                              |
| `ip_address`   | `VARCHAR(64)`              | NULL        | —                       | —                              |
| `expires_at`   | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | —                       | —                              |
| `revoked_at`   | `TIMESTAMP WITH TIME ZONE` | NULL        | —                       | —                              |
| `replaced_by`  | `VARCHAR(36)`              | NULL        | —                       | —                              |
| `last_used_at` | `TIMESTAMP WITH TIME ZONE` | NULL        | —                       | —                              |
| `created_at`   | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | application: `<lambda>` | —                              |
| `updated_at`   | `TIMESTAMP WITH TIME ZONE` | NULL        | —                       | —                              |

Indexes:

- `ix_refresh_tokens_session_id` on `session_id`
- `ix_refresh_tokens_token_hash` on `token_hash` (unique)
- `ix_refresh_tokens_user_id` on `user_id`

### `student_profiles`

| Column                     | PostgreSQL type | Nullability | Default                 | References                     |
| -------------------------- | --------------- | ----------- | ----------------------- | ------------------------------ |
| `id`                       | `VARCHAR(36)`   | NOT NULL    | application: `<lambda>` | —                              |
| `user_id`                  | `VARCHAR(36)`   | NOT NULL    | —                       | `users.id` (on delete CASCADE) |
| `goal`                     | `TEXT`          | NULL        | —                       | —                              |
| `bio`                      | `TEXT`          | NULL        | —                       | —                              |
| `display_name`             | `VARCHAR(255)`  | NULL        | —                       | —                              |
| `date_of_birth`            | `DATE`          | NULL        | —                       | —                              |
| `gender`                   | `VARCHAR(64)`   | NULL        | —                       | —                              |
| `phone`                    | `VARCHAR(32)`   | NULL        | —                       | —                              |
| `city`                     | `VARCHAR(128)`  | NULL        | —                       | —                              |
| `state`                    | `VARCHAR(128)`  | NULL        | —                       | —                              |
| `country`                  | `VARCHAR(128)`  | NULL        | —                       | —                              |
| `education_level`          | `VARCHAR(128)`  | NULL        | —                       | —                              |
| `institution`              | `VARCHAR(255)`  | NULL        | —                       | —                              |
| `degree`                   | `VARCHAR(255)`  | NULL        | —                       | —                              |
| `stream`                   | `VARCHAR(255)`  | NULL        | —                       | —                              |
| `graduation_year`          | `INTEGER`       | NULL        | —                       | —                              |
| `exam_interests`           | `JSON`          | NOT NULL    | application: `list`     | —                              |
| `opportunity_interests`    | `JSON`          | NOT NULL    | application: `list`     | —                              |
| `preferred_locations`      | `JSON`          | NOT NULL    | application: `list`     | —                              |
| `remote_preference`        | `BOOLEAN`       | NOT NULL    | application: `False`    | —                              |
| `career_interests`         | `JSON`          | NOT NULL    | application: `list`     | —                              |
| `target_roles`             | `JSON`          | NOT NULL    | application: `list`     | —                              |
| `skills`                   | `JSON`          | NOT NULL    | application: `list`     | —                              |
| `experience_level`         | `VARCHAR(64)`   | NULL        | —                       | —                              |
| `notification_preferences` | `JSON`          | NOT NULL    | application: `dict`     | —                              |

Indexes:

- `ix_student_profiles_user_id` on `user_id` (unique)

### `test_answers`

| Column        | PostgreSQL type | Nullability | Default            | References                                 |
| ------------- | --------------- | ----------- | ------------------ | ------------------------------------------ |
| `id`          | `VARCHAR(36)`   | NOT NULL    | application: `_id` | —                                          |
| `attempt_id`  | `VARCHAR(36)`   | NOT NULL    | —                  | `test_attempts.id` (on delete CASCADE)     |
| `question_id` | `VARCHAR(36)`   | NOT NULL    | —                  | `questions.id` (on delete CASCADE)         |
| `option_id`   | `VARCHAR(36)`   | NULL        | —                  | `question_options.id` (on delete SET NULL) |

Unique constraints:

- `attempt_id`, `question_id`

Indexes:

- `ix_test_answers_attempt_id` on `attempt_id`
- `ix_test_answers_question_id` on `question_id`

### `test_attempts`

| Column            | PostgreSQL type            | Nullability | Default                 | References                     |
| ----------------- | -------------------------- | ----------- | ----------------------- | ------------------------------ |
| `id`              | `VARCHAR(36)`              | NOT NULL    | application: `_id`      | —                              |
| `test_id`         | `VARCHAR(36)`              | NOT NULL    | —                       | `tests.id` (on delete CASCADE) |
| `user_id`         | `VARCHAR(36)`              | NOT NULL    | —                       | `users.id` (on delete CASCADE) |
| `started_at`      | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | application: `<lambda>` | —                              |
| `submitted_at`    | `TIMESTAMP WITH TIME ZONE` | NULL        | —                       | —                              |
| `score`           | `INTEGER`                  | NULL        | —                       | —                              |
| `total_questions` | `INTEGER`                  | NOT NULL    | application: `0`        | —                              |

Indexes:

- `ix_test_attempts_test_id` on `test_id`
- `ix_test_attempts_user_id` on `user_id`

### `tests`

| Column             | PostgreSQL type            | Nullability | Default              | References |
| ------------------ | -------------------------- | ----------- | -------------------- | ---------- |
| `id`               | `VARCHAR(36)`              | NOT NULL    | application: `_id`   | —          |
| `title`            | `VARCHAR(255)`             | NOT NULL    | —                    | —          |
| `slug`             | `VARCHAR(255)`             | NOT NULL    | —                    | —          |
| `description`      | `TEXT`                     | NULL        | —                    | —          |
| `type`             | `VARCHAR(32)`              | NOT NULL    | —                    | —          |
| `duration_minutes` | `INTEGER`                  | NOT NULL    | —                    | —          |
| `status`           | `VARCHAR(32)`              | NOT NULL    | application: `draft` | —          |
| `created_at`       | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`      | —          |
| `updated_at`       | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`      | —          |

Indexes:

- `ix_tests_slug` on `slug` (unique)
- `ix_tests_status` on `status`
- `ix_tests_title` on `title`
- `ix_tests_type` on `type`

### `users`

| Column           | PostgreSQL type            | Nullability | Default                 | References |
| ---------------- | -------------------------- | ----------- | ----------------------- | ---------- |
| `id`             | `VARCHAR(36)`              | NOT NULL    | application: `<lambda>` | —          |
| `name`           | `VARCHAR(255)`             | NOT NULL    | —                       | —          |
| `email`          | `VARCHAR(255)`             | NOT NULL    | —                       | —          |
| `password_hash`  | `VARCHAR(255)`             | NOT NULL    | —                       | —          |
| `is_admin`       | `BOOLEAN`                  | NOT NULL    | application: `False`    | —          |
| `is_active`      | `BOOLEAN`                  | NOT NULL    | application: `True`     | —          |
| `role`           | `VARCHAR(32)`              | NOT NULL    | application: `student`  | —          |
| `email_verified` | `BOOLEAN`                  | NOT NULL    | application: `False`    | —          |
| `locked_until`   | `TIMESTAMP WITH TIME ZONE` | NULL        | —                       | —          |
| `created_at`     | `TIMESTAMP WITH TIME ZONE` | NOT NULL    | server: `now()`         | —          |

Indexes:

- `ix_users_email` on `email` (unique)
- `ix_users_role` on `role`

## Extension requirements

- Alembic revision `20260813_enable_pgvector` creates PostgreSQL extension `vector`.
- No active ORM column uses the pgvector type; extension availability is nevertheless part of the existing migration contract.

## Scope

This specification covers active ORM metadata only. Legacy entities in `app.domain.models.entities` use a separate declarative base and are not loaded by `alembic/env.py`.

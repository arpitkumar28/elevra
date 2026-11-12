# Transactional account email

Elevra uses Resend for password-reset and email-verification messages. Email
delivery is disabled unless all required variables are configured. A blank API
key or encryption key means requests return a non-enumerating response and no
account token/outbox row is created.

## Required provider setup

1. Create a Resend account and verify a sending domain in its dashboard.
2. Create an API key scoped to sending email for the verified domain. Do not use
   a full-access key where a sending-only key is available.
3. Configure these server-side variables in the backend service:

| Variable | Purpose |
| --- | --- |
| `RESEND_API_KEY` | Resend sending API key. Keep it server-side. |
| `EMAIL_FROM` | Verified sender, for example `Elevra <noreply@mail.example.com>`. |
| `EMAIL_FRONTEND_URL` | Public HTTPS origin of the web app, without a query or fragment. |
| `EMAIL_OUTBOX_ENCRYPTION_KEY` | Fernet key used to encrypt one-time token values in the outbox. |
| `EMAIL_PROVIDER_TIMEOUT_SECONDS` | Request timeout; default 8 seconds. |
| `EMAIL_OUTBOX_MAX_ATTEMPTS` | Retry limit; default 5. |
| `EMAIL_OUTBOX_LEASE_SECONDS` | Worker lease; default 45 seconds and must exceed the provider timeout. |

Generate a Fernet key once, store it in the backend secret manager, and preserve
it across deploys:

```bash
cd services/backend
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Never commit the generated key or the Resend API key. Do not regenerate the
encryption key while pending outbox rows exist; doing so prevents those messages
from being decrypted. Key rotation requires a controlled re-encryption of
pending rows before the old key is removed.

## Flow and safety properties

- Registration creates a 24-hour email-verification token when email delivery
  is enabled. The raw token is returned only to the email-rendering path; the
  account-token table stores only its SHA-256 hash.
- Password reset uses a one-hour token. Request responses do not reveal whether
  the submitted address belongs to an account.
- One-time token values are encrypted with Fernet before they are persisted in
  `email_outbox`. The table has row-level security enabled and is not exposed
  by public API routes.
- The worker sends through Resend's `POST /emails` endpoint using a stable
  `Idempotency-Key` derived from the outbox ID. This prevents duplicate sends
  when retrying the same outbox item during the provider's idempotency window.
- Provider requests have bounded timeouts. Transient network, 408, 409, 425,
  429, and 5xx failures are retried with exponential backoff. Permanent 4xx
  failures invalidate the associated one-time token and mark the outbox row
  failed.
- Once Resend accepts the email, the outbox clears the encrypted token. A
  provider acceptance is not a guarantee that the recipient's mailbox placed
  the message in the inbox.
- Verification and reset links require an explicit user action. Merely opening
  the link does not consume the token.

## Endpoints

| Purpose | Request | Confirm |
| --- | --- | --- |
| Password reset | `POST /api/v1/auth/password-reset/request` | `POST /api/v1/auth/password-reset/confirm` |
| Email verification | `POST /api/v1/auth/verify-email/request` | `POST /api/v1/auth/verify-email/confirm` |

The web app provides `/reset-password` and `/verify-email` pages for these
flows. If the URL contains a token, the page removes it from browser history
after reading it and requires an explicit user action before confirmation.

## Processing and retries

The first delivery attempt runs as a FastAPI background task after the request
transaction commits. For messages that need retrying, run the worker from
`services/backend`:

```bash
python -m app.workers.email_outbox --limit 50
```

A platform scheduler can invoke this command periodically. Keep the schedule
and backend service on the same database and secret configuration. The worker
processes only due rows and can safely be run more than once. Without a
scheduler, failed messages remain in the outbox until a worker sweep is run;
the initial background task alone is not a durable retry scheduler.

## Migration and deployment

The feature adds Alembic revision `20261112_auth_email_outbox`. It must be
applied through the normal reviewed migration workflow. Do not run it directly
against production. First verify the exact target database, current revision,
provider backup/PITR point, and recovery steps; then validate on staging.

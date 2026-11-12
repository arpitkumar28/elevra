"""CLI worker for retrying pending account-security email.

Run from services/backend with:
    python -m app.workers.email_outbox --limit 50
"""

from __future__ import annotations

import argparse
import logging

from app.services.email_delivery import email_delivery_is_configured, process_due_emails


def main() -> int:
    parser = argparse.ArgumentParser(description="Deliver pending Elevra account emails")
    parser.add_argument("--limit", type=int, default=50, help="Maximum messages to attempt (1-500)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    if not email_delivery_is_configured():
        parser.error(
            "Email delivery is disabled. Configure RESEND_API_KEY, EMAIL_FROM, "
            "EMAIL_FRONTEND_URL, and EMAIL_OUTBOX_ENCRYPTION_KEY."
        )
    processed = process_due_emails(limit=args.limit)
    logging.getLogger("app.email").info("email_outbox_sweep_complete processed=%s", processed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

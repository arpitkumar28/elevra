# REST API Standards

Elevra APIs are versioned under `/api/v1` and must serve Next.js, Flutter, and future public API clients.

## Required Endpoint Behavior

- Authentication: JWT bearer tokens for private endpoints.
- Authorization: permission checks for admin and super-admin operations.
- Validation: Pydantic request and response models.
- Documentation: OpenAPI generated from FastAPI route metadata.
- Rate limiting: default limiter plus stricter endpoint-level limits for expensive operations.
- Pagination: `page`, `page_size`, `sort`, and `direction`.
- Filtering: explicit typed query parameters, not arbitrary SQL fragments.
- Search: delegated to the search service for ranked, typo-tolerant discovery.
- Logging: structured JSON logs with request IDs in production.

## Core Route Groups

- `/api/v1/system`: health and readiness.
- `/api/v1/auth`: session, OAuth exchange, token lifecycle.
- `/api/v1/opportunities`: discovery, bookmarking, approval workflows.
- `/api/v1/admin`: analytics, review queues, crawler monitoring, notification operations.

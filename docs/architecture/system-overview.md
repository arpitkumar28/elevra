# System Overview

Elevra is organized around independently deployable product and platform capabilities.

```mermaid
flowchart LR
  Student["Student"] --> Web["Student Web App"]
  Student --> Mobile["Flutter Mobile App"]
  Admin["Operations Team"] --> AdminApp["Admin Dashboard"]
  Web --> API["FastAPI Backend"]
  Mobile --> API
  AdminApp --> API
  API --> Postgres["PostgreSQL"]
  API --> Redis["Redis"]
  API --> SearchService["Search Service"]
  SearchService --> Meili["Meilisearch"]
  Scheduler["Scheduler and Notification Engine"] --> Crawler["Crawler"]
  Scheduler --> API
  Crawler --> SearchService
  API --> AI["AI Engine"]
  API --> S3["S3 Compatible Storage"]
```

Core services should communicate through typed HTTP contracts initially, with event-driven
workflows introduced when throughput or coupling requires it.

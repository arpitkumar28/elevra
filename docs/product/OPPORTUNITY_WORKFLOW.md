# Opportunity workflow — backend and database phase

## Opportunity lifecycle

- `draft`: private while an admin prepares the listing.
- `pending_review`: submitted for review and not visible in public discovery.
- `verified`: a reviewer has checked the official source and approved the listing.
- `published`: visible in the public opportunity listing.
- `closed`: removed from discovery while the detail remains readable for saved links and application history.
- `rejected`: reviewer declined the listing with a required explanation.
- `archived`: retained for history and not publicly discoverable.

Allowed actions:

| From | Action | To |
|---|---|---|
| draft / rejected | submit | pending_review |
| pending_review | approve | verified |
| pending_review | request-changes | draft |
| pending_review | reject | rejected |
| verified | publish | published |
| published | unpublish | verified |
| published | close | closed |
| draft / rejected / verified / published / closed | archive | archived |

Submission requires an organization, a description or summary, an application
URL, a source name and a source URL. Requesting changes or rejecting requires
a review note of at least five characters. Review actions retain the reviewer,
review timestamp and source-check timestamp.

Only published opportunities appear in public listings. Closed details remain
readable for existing bookmarks and application records.

## Student application tracker

Tracking an Elevra opportunity requires that the opportunity be published.
The server copies the canonical title, organization and application URL from
the opportunity record. A PostgreSQL transaction advisory lock protects the
student/opportunity duplicate check against concurrent requests.

A new tracker starts in `saved` and writes an initial event. Each subsequent
status transition writes an `application_events` row, including the previous
status, new status and optional note. The first transition to `applied` stamps
`applied_at`; a student can also store a `follow_up_date`.

The tracker reflects a student's self-reported progress. It does not submit
applications to employers or verify employer-side outcomes. Event history is
scoped to the owning student.

## Public API changes

- `GET /api/v1/opportunities` remains public and now supports deadline range
  filters and `sort=newest|deadline_soonest`.
- Public listing returns only `published` records.
- `GET /api/v1/opportunities/{slug}` also returns `closed` records for saved
  links and application history.
- Admin lifecycle actions are under
  `/api/v1/admin/content/opportunities/{id}/actions/{action}`.
- `GET /api/v1/applications/{id}/events` returns the signed-in student's own
  tracker history.

## Migration and deployment

The forward migration `20261111_opportunity_workflow` follows
`20261110_enable_public_rls`. It extends the existing opportunity enum,
adds opportunity review metadata, adds application follow-up fields, creates
`application_events`, and enables RLS on that new table.

The migration has not been executed against staging or production by this
change. Run it only through the reviewed migration workflow after verifying
the target database and a current backup. The API change also needs the Phase 2
admin interface and Phase 3 student tracker UI before the complete visual
workflow is ready for users.

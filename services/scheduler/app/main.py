from app.schemas import NotificationDispatchRequest, ScheduledWorkflow
from fastapi import FastAPI

app = FastAPI(title="Elevra Scheduler Service", version="0.1.0")


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "scheduler"}


@app.get("/workflows", response_model=list[ScheduledWorkflow])
async def list_workflows() -> list[ScheduledWorkflow]:
    return [
        ScheduledWorkflow(
            key="deadline-notifications",
            cron="*/15 * * * *",
            purpose="Dispatch upcoming deadline reminders across push, email, and in-app channels.",
        ),
        ScheduledWorkflow(
            key="crawler-refresh",
            cron="0 */4 * * *",
            purpose="Refresh verified opportunity sources and submit records for review.",
        ),
        ScheduledWorkflow(
            key="ai-evaluation",
            cron="0 2 * * *",
            purpose=(
                "Run model quality samples, safety checks, "
                "and recommendation drift monitoring."
            ),
        ),
    ]


@app.post("/notifications/dispatch", status_code=202)
async def dispatch_notification(request: NotificationDispatchRequest) -> dict[str, object]:
    return {"status": "queued", "request": request.model_dump()}

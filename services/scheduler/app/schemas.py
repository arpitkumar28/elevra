"""Scheduler and notification workflow contracts."""

from pydantic import BaseModel, Field


class ScheduledWorkflow(BaseModel):
    key: str
    cron: str
    purpose: str
    enabled: bool = True


class NotificationDispatchRequest(BaseModel):
    user_id: str
    template_key: str
    channel: str = Field(pattern="^(push|email|in_app)$")
    payload: dict[str, object] = Field(default_factory=dict)

"""Domain enums used by persistence and API contracts."""

from enum import StrEnum


class OpportunityStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class OpportunityType(StrEnum):
    SCHOLARSHIP = "scholarship"
    INTERNSHIP = "internship"
    COMPETITION = "competition"
    COURSE = "course"
    EXAM = "exam"


class NotificationChannel(StrEnum):
    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    LOGIN = "login"

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class DependencyStatus(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    service: str
    dependencies: dict[str, DependencyStatus]

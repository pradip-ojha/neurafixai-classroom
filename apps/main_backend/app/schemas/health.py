from pydantic import BaseModel


class DependencyStatus(BaseModel):
    name: str
    ok: bool
    latency_ms: float | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    service: str
    status: str
    request_id: str


class ReadyResponse(HealthResponse):
    dependencies: list[DependencyStatus]


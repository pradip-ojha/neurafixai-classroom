from fastapi.testclient import TestClient

from app.main import app
from app.schemas.health import DependencyStatus


def test_health_returns_request_id() -> None:
    client = TestClient(app)

    response = client.get("/health", headers={"X-Request-ID": "test-request"})

    assert response.status_code == 200
    assert response.json()["service"] == "main_backend"
    assert response.json()["request_id"] == "test-request"
    assert response.headers["X-Request-ID"] == "test-request"
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_api_v1_health_alias() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_reports_dependencies(monkeypatch) -> None:
    async def ok_database() -> DependencyStatus:
        return DependencyStatus(name="postgres", ok=True, latency_ms=1.0)

    async def ok_redis() -> DependencyStatus:
        return DependencyStatus(name="redis", ok=True, latency_ms=1.0)

    monkeypatch.setattr("app.api.v1.routes.health.check_database", ok_database)
    monkeypatch.setattr("app.api.v1.routes.health.check_redis", ok_redis)

    client = TestClient(app)
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert {item["name"] for item in response.json()["dependencies"]} == {"postgres", "redis"}


def test_ready_returns_503_when_dependency_fails(monkeypatch) -> None:
    async def failed_database() -> DependencyStatus:
        return DependencyStatus(name="postgres", ok=False, error="ConnectionError")

    async def ok_redis() -> DependencyStatus:
        return DependencyStatus(name="redis", ok=True, latency_ms=1.0)

    monkeypatch.setattr("app.api.v1.routes.health.check_database", failed_database)
    monkeypatch.setattr("app.api.v1.routes.health.check_redis", ok_redis)

    client = TestClient(app)
    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"


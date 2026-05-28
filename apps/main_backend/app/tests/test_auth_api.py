from fastapi.testclient import TestClient

from app.main import app


def test_auth_validation_uses_standard_error_envelope() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/auth/login", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["request_id"]


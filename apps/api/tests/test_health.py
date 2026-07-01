from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_service_status() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "meetmind-api"
    assert body["version"] == "0.1.0"
    assert body["checks"]["database"] == "ok"


def test_app_uses_expected_title() -> None:
    assert app.title == "MeetMind API"

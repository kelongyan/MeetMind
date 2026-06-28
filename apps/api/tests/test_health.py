from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_service_status() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "meetmind-api",
        "version": "0.1.0",
    }


def test_app_uses_expected_title() -> None:
    assert app.title == "MeetMind API"

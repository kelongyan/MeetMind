from fastapi.testclient import TestClient

from app.main import app


def test_local_web_origin_can_call_api() -> None:
    client = TestClient(app)

    response = client.options(
        "/api/meetings",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

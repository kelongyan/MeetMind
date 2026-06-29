from fastapi.testclient import TestClient

from app.main import app


def test_create_processing_job_and_read_status() -> None:
    client = TestClient(app)
    meeting_response = client.post("/api/meetings", json={"title": "Job source"})
    meeting_id = meeting_response.json()["id"]

    create_response = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "transcribe", "provider": "local-test"},
    )

    assert create_response.status_code == 201
    job = create_response.json()
    assert job["id"]
    assert job["meeting_id"] == meeting_id
    assert job["job_type"] == "transcribe"
    assert job["status"] == "queued"
    assert job["progress"] == 0
    assert job["provider"] == "local-test"

    get_response = client.get(f"/api/jobs/{job['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "queued"

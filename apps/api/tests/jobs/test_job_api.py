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


def test_list_processing_jobs_for_meeting() -> None:
    client = TestClient(app)
    meeting_id = client.post("/api/meetings", json={"title": "Job list"}).json()[
        "id"
    ]
    first_job = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "transcribe", "provider": "local-test"},
    ).json()
    second_job = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "structure", "provider": "local-test"},
    ).json()

    response = client.get(f"/api/meetings/{meeting_id}/jobs")

    assert response.status_code == 200
    assert [job["id"] for job in response.json()] == [
        first_job["id"],
        second_job["id"],
    ]


def test_create_processing_job_rejects_asset_from_another_meeting() -> None:
    client = TestClient(app)
    source_meeting_id = client.post(
        "/api/meetings", json={"title": "Source meeting"}
    ).json()["id"]
    target_meeting_id = client.post(
        "/api/meetings", json={"title": "Target meeting"}
    ).json()["id"]
    asset_id = client.post(
        f"/api/meetings/{source_meeting_id}/assets",
        files={"file": ("notes.txt", b"Source transcript", "text/plain")},
    ).json()["asset"]["id"]

    response = client.post(
        f"/api/meetings/{target_meeting_id}/process",
        json={"job_type": "structure", "input_asset_id": asset_id},
    )

    assert response.status_code == 409
    assert "asset" in response.json()["detail"].casefold()

from fastapi.testclient import TestClient

from app.main import app


def test_update_job_failure_and_retry_without_duplicate_asset() -> None:
    client = TestClient(app)
    meeting_response = client.post("/api/meetings", json={"title": "Retry"})
    meeting_id = meeting_response.json()["id"]
    upload_response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={"file": ("retry.wav", b"fake wave", "audio/wav")},
    )
    asset_id = upload_response.json()["asset"]["id"]
    job_id = upload_response.json()["job"]["id"]

    running_response = client.patch(
        f"/api/jobs/{job_id}",
        json={"status": "running", "progress": 40},
    )
    assert running_response.status_code == 200
    assert running_response.json()["status"] == "running"
    assert running_response.json()["progress"] == 40

    failed_response = client.patch(
        f"/api/jobs/{job_id}",
        json={
            "status": "failed",
            "progress": 40,
            "retryable": True,
            "failure_code": "asr_timeout",
            "failure_message": "The local worker timed out.",
        },
    )
    assert failed_response.status_code == 200
    assert failed_response.json()["status"] == "failed"
    assert failed_response.json()["retryable"] is True
    assert failed_response.json()["failed_at"]
    assert failed_response.json()["failure_code"] == "asr_timeout"
    assert failed_response.json()["failure_message"] == "The local worker timed out."

    retry_response = client.post(f"/api/jobs/{job_id}/retry")

    assert retry_response.status_code == 201
    retry_job = retry_response.json()
    assert retry_job["id"] != job_id
    assert retry_job["status"] == "queued"
    assert retry_job["progress"] == 0
    assert retry_job["input_asset_id"] == asset_id
    assert retry_job["retry_of_job_id"] == job_id
    assert retry_job["attempt_number"] == 2
    assert retry_job["failure_code"] is None
    assert retry_job["failure_message"] is None

    assets_response = client.get(f"/api/meetings/{meeting_id}/assets")
    assert [asset["id"] for asset in assets_response.json()] == [asset_id]


def test_non_retryable_failed_job_cannot_be_retried() -> None:
    client = TestClient(app)
    meeting_response = client.post("/api/meetings", json={"title": "No retry"})
    meeting_id = meeting_response.json()["id"]
    job_response = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "structure"},
    )
    job_id = job_response.json()["id"]
    client.patch(
        f"/api/jobs/{job_id}",
        json={
            "status": "failed",
            "retryable": False,
            "failure_code": "unsupported_media",
            "failure_message": "The media format cannot be processed.",
        },
    )

    response = client.post(f"/api/jobs/{job_id}/retry")

    assert response.status_code == 409
    assert response.json()["detail"] == "Job is marked as non-retryable"


def test_failed_job_requires_failure_code_and_message() -> None:
    client = TestClient(app)
    meeting_response = client.post("/api/meetings", json={"title": "Failure"})
    meeting_id = meeting_response.json()["id"]
    job_response = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "structure"},
    )
    job_id = job_response.json()["id"]

    response = client.patch(f"/api/jobs/{job_id}", json={"status": "failed"})

    assert response.status_code == 422

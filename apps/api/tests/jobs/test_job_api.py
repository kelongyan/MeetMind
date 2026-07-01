from fastapi.testclient import TestClient

from app.main import app


def test_create_processing_job_and_read_status(auth_headers: dict[str, str]) -> None:
    client = TestClient(app)
    meeting_response = client.post(
        "/api/meetings", json={"title": "Job source"}, headers=auth_headers
    )
    meeting_id = meeting_response.json()["id"]

    create_response = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "structure", "provider": "local-test"},
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    job = create_response.json()
    assert job["id"]
    assert job["meeting_id"] == meeting_id
    assert job["job_type"] == "structure"
    assert job["status"] == "queued"
    assert job["progress"] == 0
    assert job["provider"] == "local-test"

    get_response = client.get(f"/api/jobs/{job['id']}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "queued"


def test_list_processing_jobs_for_meeting(auth_headers: dict[str, str]) -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Job list"}, headers=auth_headers
    ).json()["id"]
    first_job = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "structure", "provider": "local-test"},
        headers=auth_headers,
    ).json()
    second_job = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "embed", "provider": "local-test"},
        headers=auth_headers,
    ).json()

    response = client.get(f"/api/meetings/{meeting_id}/jobs", headers=auth_headers)

    assert response.status_code == 200
    assert [job["id"] for job in response.json()["items"]] == [
        first_job["id"],
        second_job["id"],
    ]


def test_create_processing_job_rejects_asset_from_another_meeting(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    source_meeting_id = client.post(
        "/api/meetings", json={"title": "Source meeting"}, headers=auth_headers
    ).json()["id"]
    target_meeting_id = client.post(
        "/api/meetings", json={"title": "Target meeting"}, headers=auth_headers
    ).json()["id"]
    asset_id = client.post(
        f"/api/meetings/{source_meeting_id}/assets",
        files={"file": ("notes.txt", b"Source transcript", "text/plain")},
        headers=auth_headers,
    ).json()["asset"]["id"]

    response = client.post(
        f"/api/meetings/{target_meeting_id}/process",
        json={"job_type": "structure", "input_asset_id": asset_id},
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert "asset" in response.json()["detail"].casefold()


def test_create_transcribe_job_requires_audio_or_video_asset(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Transcribe asset"}, headers=auth_headers
    ).json()["id"]
    text_asset_id = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={"file": ("notes.txt", b"Source transcript", "text/plain")},
        headers=auth_headers,
    ).json()["asset"]["id"]
    audio_asset_id = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={"file": ("sample.wav", b"audio bytes", "audio/wav")},
        headers=auth_headers,
    ).json()["asset"]["id"]

    missing_asset_response = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "transcribe"},
        headers=auth_headers,
    )
    text_asset_response = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "transcribe", "input_asset_id": text_asset_id},
        headers=auth_headers,
    )
    audio_asset_response = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "transcribe", "input_asset_id": audio_asset_id},
        headers=auth_headers,
    )

    assert missing_asset_response.status_code == 409
    assert "asset" in missing_asset_response.json()["detail"].casefold()
    assert text_asset_response.status_code == 409
    assert "audio or video" in text_asset_response.json()["detail"].casefold()
    assert audio_asset_response.status_code == 201

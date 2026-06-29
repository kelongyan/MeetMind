from hashlib import sha256
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture
def upload_storage_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    storage_dir = tmp_path / "storage"
    monkeypatch.setattr(settings, "upload_storage_dir", str(storage_dir))
    return storage_dir


def test_upload_meeting_file_creates_asset_and_queued_job(
    upload_storage_dir: Path,
) -> None:
    client = TestClient(app)
    meeting_response = client.post("/api/meetings", json={"title": "Upload"})
    meeting_id = meeting_response.json()["id"]
    content = b"Project kickoff transcript."

    response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={"file": ("kickoff.txt", content, "text/plain")},
    )

    assert response.status_code == 201
    body = response.json()
    asset = body["asset"]
    job = body["job"]
    assert body["duplicate"] is False
    assert asset["meeting_id"] == meeting_id
    assert asset["asset_type"] == "transcript"
    assert asset["original_filename"] == "kickoff.txt"
    assert asset["mime_type"] == "text/plain"
    assert asset["size_bytes"] == len(content)
    assert asset["sha256"] == sha256(content).hexdigest()
    assert asset["storage_uri"].startswith(f"local://{meeting_id}/")
    assert (upload_storage_dir / meeting_id / f"{asset['sha256']}.txt").exists()
    assert job["meeting_id"] == meeting_id
    assert job["input_asset_id"] == asset["id"]
    assert job["job_type"] == "structure"
    assert job["status"] == "queued"
    assert job["progress"] == 0

    list_response = client.get(f"/api/meetings/{meeting_id}/assets")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [asset["id"]]


def test_upload_rejects_unsupported_file_type(upload_storage_dir: Path) -> None:
    client = TestClient(app)
    meeting_response = client.post("/api/meetings", json={"title": "Bad upload"})
    meeting_id = meeting_response.json()["id"]

    response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={"file": ("payload.exe", b"not allowed", "application/octet-stream")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported file type"
    assert not upload_storage_dir.exists()
    assert client.get(f"/api/meetings/{meeting_id}/assets").json() == []


def test_duplicate_upload_reuses_existing_asset_without_new_job(
    upload_storage_dir: Path,
) -> None:
    client = TestClient(app)
    meeting_response = client.post("/api/meetings", json={"title": "Duplicate"})
    meeting_id = meeting_response.json()["id"]
    files = {
        "file": ("notes.vtt", b"WEBVTT\n\n00:00.000 --> 00:01.000\nHi", "text/vtt")
    }

    first_response = client.post(f"/api/meetings/{meeting_id}/assets", files=files)
    second_response = client.post(f"/api/meetings/{meeting_id}/assets", files=files)

    assert first_response.status_code == 201
    assert second_response.status_code == 200
    first_body = first_response.json()
    second_body = second_response.json()
    assert second_body["duplicate"] is True
    assert second_body["asset"]["id"] == first_body["asset"]["id"]
    assert second_body["job"] is None
    assert len(list((upload_storage_dir / meeting_id).iterdir())) == 1

    assets_response = client.get(f"/api/meetings/{meeting_id}/assets")
    assert [item["id"] for item in assets_response.json()] == [
        first_body["asset"]["id"]
    ]

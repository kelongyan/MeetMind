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


def test_create_read_update_and_delete_meeting(auth_headers: dict[str, str]) -> None:
    client = TestClient(app)

    create_response = client.post(
        "/api/meetings",
        json={
            "title": "Phase 1 planning",
            "description": "Backend domain kickoff",
            "language": "zh-CN",
            "workspace_id": "workspace-local",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    meeting = create_response.json()
    assert meeting["id"]
    assert meeting["title"] == "Phase 1 planning"
    assert meeting["description"] == "Backend domain kickoff"
    assert meeting["language"] == "zh-CN"
    assert meeting["workspace_id"] == "workspace-local"
    assert meeting["status"] == "uploaded"

    list_response = client.get("/api/meetings", headers=auth_headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()["items"]] == [meeting["id"]]

    get_response = client.get(f"/api/meetings/{meeting['id']}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Phase 1 planning"

    update_response = client.patch(
        f"/api/meetings/{meeting['id']}",
        json={"title": "Updated planning"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated planning"

    delete_response = client.delete(
        f"/api/meetings/{meeting['id']}", headers=auth_headers
    )
    assert delete_response.status_code == 204

    missing_response = client.get(
        f"/api/meetings/{meeting['id']}", headers=auth_headers
    )
    assert missing_response.status_code == 404


def test_delete_meeting_removes_local_upload_files(
    upload_storage_dir: Path, auth_headers: dict[str, str]
) -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Delete files"}, headers=auth_headers
    ).json()["id"]
    upload_response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={"file": ("notes.txt", b"cleanup me", "text/plain")},
        headers=auth_headers,
    )
    asset = upload_response.json()["asset"]
    uploaded_path = upload_storage_dir / meeting_id / f"{asset['sha256']}.txt"
    assert uploaded_path.exists()

    delete_response = client.delete(f"/api/meetings/{meeting_id}", headers=auth_headers)

    assert delete_response.status_code == 204
    assert not uploaded_path.exists()
    assert not (upload_storage_dir / meeting_id).exists()


def test_publish_meeting_requires_citations_for_key_outputs(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings",
        json={"title": "Publish readiness", "language": "en"},
        headers=auth_headers,
    ).json()["id"]
    client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 0,
            "end_ms": 3000,
            "text": "Nina owns the launch checklist.",
            "confidence": 0.95,
        },
        headers=auth_headers,
    )
    action = client.post(
        f"/api/meetings/{meeting_id}/action-items",
        json={
            "description": "Prepare the launch checklist.",
            "owner_text": "Nina",
            "status": "confirmed",
            "confirmed_by_user_id": "local-user",
        },
        headers=auth_headers,
    ).json()

    blocked_response = client.post(
        f"/api/meetings/{meeting_id}/publish", headers=auth_headers
    )

    assert blocked_response.status_code == 409
    assert blocked_response.json()["detail"] == (
        "Cannot publish meeting while key outputs are missing citations"
    )

    segment = client.get(
        f"/api/meetings/{meeting_id}/transcript", headers=auth_headers
    ).json()["items"][0]
    client.post(
        f"/api/meetings/{meeting_id}/citations",
        json={
            "target_type": "action_item",
            "target_id": action["id"],
            "segment_id": segment["id"],
            "start_ms": segment["start_ms"],
            "end_ms": segment["end_ms"],
            "quote": segment["text"],
            "confidence": 0.91,
        },
        headers=auth_headers,
    )

    publish_response = client.post(
        f"/api/meetings/{meeting_id}/publish", headers=auth_headers
    )

    assert publish_response.status_code == 200
    assert publish_response.json()["status"] == "published"

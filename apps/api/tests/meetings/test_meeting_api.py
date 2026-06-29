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


def test_create_read_update_and_delete_meeting() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/api/meetings",
        json={
            "title": "Phase 1 planning",
            "description": "Backend domain kickoff",
            "language": "zh-CN",
            "workspace_id": "workspace-local",
        },
    )

    assert create_response.status_code == 201
    meeting = create_response.json()
    assert meeting["id"]
    assert meeting["title"] == "Phase 1 planning"
    assert meeting["description"] == "Backend domain kickoff"
    assert meeting["language"] == "zh-CN"
    assert meeting["workspace_id"] == "workspace-local"
    assert meeting["status"] == "uploaded"

    list_response = client.get("/api/meetings")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [meeting["id"]]

    get_response = client.get(f"/api/meetings/{meeting['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Phase 1 planning"

    update_response = client.patch(
        f"/api/meetings/{meeting['id']}",
        json={"title": "Updated planning", "status": "media_processing"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated planning"
    assert update_response.json()["status"] == "media_processing"

    delete_response = client.delete(f"/api/meetings/{meeting['id']}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/meetings/{meeting['id']}")
    assert missing_response.status_code == 404


def test_delete_meeting_removes_local_upload_files(upload_storage_dir: Path) -> None:
    client = TestClient(app)
    meeting_id = client.post("/api/meetings", json={"title": "Delete files"}).json()[
        "id"
    ]
    upload_response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={"file": ("notes.txt", b"cleanup me", "text/plain")},
    )
    asset = upload_response.json()["asset"]
    uploaded_path = upload_storage_dir / meeting_id / f"{asset['sha256']}.txt"
    assert uploaded_path.exists()

    delete_response = client.delete(f"/api/meetings/{meeting_id}")

    assert delete_response.status_code == 204
    assert not uploaded_path.exists()
    assert not (upload_storage_dir / meeting_id).exists()

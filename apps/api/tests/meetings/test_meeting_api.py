from fastapi.testclient import TestClient

from app.main import app


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

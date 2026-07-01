from fastapi.testclient import TestClient

from app.main import app


def test_export_markdown_returns_asset_with_downloadable_content(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    meeting_id, segment_id, action_id = _create_meeting_with_data(client, auth_headers)

    export_response = client.post(
        f"/api/meetings/{meeting_id}/export", headers=auth_headers
    )
    assert export_response.status_code == 201
    asset = export_response.json()
    assert asset["asset_type"] == "export"
    assert asset["meeting_id"] == meeting_id

    download_response = client.get(
        f"/api/meetings/{meeting_id}/export/download", headers=auth_headers
    )
    assert download_response.status_code == 200
    assert download_response.headers["content-type"].startswith("text/markdown")
    markdown = download_response.text
    assert "# " in markdown  # Has a title heading
    assert "Nina" in markdown or "rollout" in markdown


def test_export_replaces_previous_export_asset(auth_headers: dict[str, str]) -> None:
    client = TestClient(app)
    meeting_id, _segment_id, _action_id = _create_meeting_with_data(
        client, auth_headers
    )

    first = client.post(
        f"/api/meetings/{meeting_id}/export", headers=auth_headers
    ).json()
    second = client.post(
        f"/api/meetings/{meeting_id}/export", headers=auth_headers
    ).json()

    assert first["id"] != second["id"]

    assets_response = client.get(
        f"/api/meetings/{meeting_id}/assets", headers=auth_headers
    )
    export_assets = [
        a for a in assets_response.json()["items"] if a["asset_type"] == "export"
    ]
    assert len(export_assets) == 1
    assert export_assets[0]["id"] == second["id"]


def test_export_download_returns_404_when_no_export_exists(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Empty", "language": "en"}, headers=auth_headers
    ).json()["id"]

    response = client.get(
        f"/api/meetings/{meeting_id}/export/download", headers=auth_headers
    )
    assert response.status_code == 404


def _create_meeting_with_data(
    client: TestClient, auth_headers: dict[str, str]
) -> tuple[str, str, str]:
    meeting_id = client.post(
        "/api/meetings",
        json={"title": "Launch review", "language": "en"},
        headers=auth_headers,
    ).json()["id"]
    segment = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 0,
            "end_ms": 5000,
            "text": "Nina will own the rollout checklist before Friday.",
            "confidence": 0.95,
        },
        headers=auth_headers,
    ).json()
    action = client.post(
        f"/api/meetings/{meeting_id}/action-items",
        json={
            "description": "Prepare the rollout checklist.",
            "owner_text": "Nina",
            "due_text": "Friday",
        },
        headers=auth_headers,
    ).json()
    client.post(
        f"/api/meetings/{meeting_id}/citations",
        json={
            "target_type": "action_item",
            "target_id": action["id"],
            "segment_id": segment["id"],
            "start_ms": 0,
            "end_ms": 5000,
            "quote": "Nina will own the rollout checklist before Friday.",
            "confidence": 0.9,
        },
        headers=auth_headers,
    )
    return meeting_id, segment["id"], action["id"]

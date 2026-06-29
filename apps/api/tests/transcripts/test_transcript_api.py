from fastapi.testclient import TestClient

from app.main import app


def test_create_and_list_transcript_segments_in_time_order() -> None:
    client = TestClient(app)
    meeting_response = client.post("/api/meetings", json={"title": "Transcript"})
    meeting_id = meeting_response.json()["id"]

    later_response = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 3000,
            "end_ms": 4200,
            "text": "Then we review citations.",
            "confidence": 0.91,
            "chunk_index": 1,
        },
    )
    earlier_response = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 2400,
            "text": "We start with the backend model.",
            "confidence": 0.95,
            "chunk_index": 0,
        },
    )

    assert later_response.status_code == 201
    assert earlier_response.status_code == 201

    list_response = client.get(f"/api/meetings/{meeting_id}/transcript")
    assert list_response.status_code == 200
    segments = list_response.json()
    assert [segment["text"] for segment in segments] == [
        "We start with the backend model.",
        "Then we review citations.",
    ]
    assert [segment["start_ms"] for segment in segments] == [1000, 3000]


def test_create_transcript_rejects_source_asset_from_another_meeting() -> None:
    client = TestClient(app)
    source_meeting_id = client.post(
        "/api/meetings", json={"title": "Source asset"}
    ).json()["id"]
    target_meeting_id = client.post(
        "/api/meetings", json={"title": "Target transcript"}
    ).json()["id"]
    asset_id = client.post(
        f"/api/meetings/{source_meeting_id}/assets",
        files={"file": ("notes.txt", b"Source transcript", "text/plain")},
    ).json()["asset"]["id"]

    response = client.post(
        f"/api/meetings/{target_meeting_id}/transcript",
        json={
            "start_ms": 0,
            "end_ms": 1000,
            "text": "This should not attach to another meeting asset.",
            "source_asset_id": asset_id,
        },
    )

    assert response.status_code == 409
    assert "asset" in response.json()["detail"].casefold()

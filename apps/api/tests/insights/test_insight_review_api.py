from fastapi.testclient import TestClient

from app.main import app


def test_update_insight_edits_content_and_dismisses_without_losing_citation(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Insight review"}, headers=auth_headers
    ).json()["id"]
    segment = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 4000,
            "text": "The team decided to keep the beta scope narrow.",
            "confidence": 0.93,
        },
        headers=auth_headers,
    ).json()
    insight = client.post(
        f"/api/meetings/{meeting_id}/insights",
        json={
            "type": "decision",
            "title": "Beta scope",
            "body": "The beta scope is narrow.",
            "confidence": 0.86,
        },
        headers=auth_headers,
    ).json()
    client.post(
        f"/api/meetings/{meeting_id}/citations",
        json={
            "target_type": "insight_item",
            "target_id": insight["id"],
            "segment_id": segment["id"],
            "start_ms": 1000,
            "end_ms": 4000,
            "quote": "The team decided to keep the beta scope narrow.",
            "confidence": 0.9,
        },
        headers=auth_headers,
    )

    response = client.patch(
        f"/api/meetings/{meeting_id}/insights/{insight['id']}",
        json={
            "title": "Beta scope confirmed",
            "body": "The team confirmed a narrow beta scope.",
            "status": "dismissed",
        },
        headers=auth_headers,
    )
    citations = client.get(
        f"/api/meetings/{meeting_id}/citations", headers=auth_headers
    ).json()["items"]

    assert response.status_code == 200
    assert response.json()["title"] == "Beta scope confirmed"
    assert response.json()["body"] == "The team confirmed a narrow beta scope."
    assert response.json()["status"] == "dismissed"
    assert len(citations) == 1
    assert citations[0]["target_id"] == insight["id"]

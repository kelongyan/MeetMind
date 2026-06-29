from fastapi.testclient import TestClient

from app.main import app


def test_create_and_list_insights_action_items_and_citations() -> None:
    client = TestClient(app)
    meeting_response = client.post("/api/meetings", json={"title": "Insights"})
    meeting_id = meeting_response.json()["id"]

    segment_response = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 3000,
            "text": "Alex will prepare the database benchmark by Friday.",
            "confidence": 0.9,
        },
    )
    segment_id = segment_response.json()["id"]

    insight_response = client.post(
        f"/api/meetings/{meeting_id}/insights",
        json={
            "type": "decision",
            "title": "Benchmark scope agreed",
            "body": "The team agreed to benchmark database performance.",
            "confidence": 0.86,
            "model_name": "test-model",
            "model_version": "2026-06",
            "prompt_version": "phase1-test",
        },
    )
    action_response = client.post(
        f"/api/meetings/{meeting_id}/action-items",
        json={
            "description": "Prepare the database benchmark.",
            "owner_text": "Alex",
            "due_text": "Friday",
            "confidence": 0.88,
            "created_by_ai": True,
        },
    )

    assert insight_response.status_code == 201
    assert action_response.status_code == 201
    insight_id = insight_response.json()["id"]
    action_id = action_response.json()["id"]

    citation_response = client.post(
        f"/api/meetings/{meeting_id}/citations",
        json={
            "target_type": "action_item",
            "target_id": action_id,
            "segment_id": segment_id,
            "start_ms": 1000,
            "end_ms": 3000,
            "quote": "Alex will prepare the database benchmark by Friday.",
            "confidence": 0.9,
        },
    )
    assert citation_response.status_code == 201

    insights_response = client.get(f"/api/meetings/{meeting_id}/insights")
    actions_response = client.get(f"/api/meetings/{meeting_id}/action-items")
    citations_response = client.get(f"/api/meetings/{meeting_id}/citations")

    assert [item["id"] for item in insights_response.json()] == [insight_id]
    assert [item["id"] for item in actions_response.json()] == [action_id]
    assert citations_response.json()[0]["target_id"] == action_id
    assert citations_response.json()[0]["segment_id"] == segment_id

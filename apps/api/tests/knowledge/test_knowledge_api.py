from fastapi.testclient import TestClient

from app.main import app


def test_workspace_search_returns_cited_meeting_results() -> None:
    client = TestClient(app)
    meeting_id, segment_id, _action_id = _create_workspace_meeting(
        client,
        workspace_id="workspace-a",
        title="Launch review",
        transcript_text="Nina owns the launch checklist before Friday.",
    )
    _create_workspace_meeting(
        client,
        workspace_id="workspace-b",
        title="Private review",
        transcript_text="Nina owns the private checklist.",
    )

    response = client.get(
        "/api/knowledge/search",
        params={"workspace_id": "workspace-a", "query": "owns launch"},
    )

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["meeting_id"] == meeting_id
    assert results[0]["meeting_title"] == "Launch review"
    assert results[0]["source_type"] == "transcript_segment"
    assert results[0]["segment_id"] == segment_id
    assert results[0]["snippet"] == "Nina owns the launch checklist before Friday."


def test_decision_list_returns_historical_decisions_with_citations() -> None:
    client = TestClient(app)
    meeting_id, segment_id, _action_id = _create_workspace_meeting(
        client,
        workspace_id="workspace-a",
        title="Architecture review",
        transcript_text="We decided to keep Postgres for v0.1.",
    )
    decision = client.post(
        f"/api/meetings/{meeting_id}/insights",
        json={
            "type": "decision",
            "title": "Keep Postgres",
            "body": "The team decided to keep Postgres for v0.1.",
            "status": "confirmed",
        },
    ).json()
    citation = client.post(
        f"/api/meetings/{meeting_id}/citations",
        json={
            "target_type": "insight_item",
            "target_id": decision["id"],
            "segment_id": segment_id,
            "start_ms": 0,
            "end_ms": 1000,
            "quote": "We decided to keep Postgres for v0.1.",
            "confidence": 0.93,
        },
    ).json()

    response = client.get(
        "/api/knowledge/decisions", params={"workspace_id": "workspace-a"}
    )

    assert response.status_code == 200
    decisions = response.json()
    assert len(decisions) == 1
    assert decisions[0]["id"] == decision["id"]
    assert decisions[0]["meeting_id"] == meeting_id
    assert decisions[0]["meeting_title"] == "Architecture review"
    assert decisions[0]["citations"][0]["id"] == citation["id"]


def test_duplicate_action_candidates_are_reported_without_merging() -> None:
    client = TestClient(app)
    _first_meeting_id, _first_segment_id, first_action_id = _create_workspace_meeting(
        client,
        workspace_id="workspace-a",
        title="Planning one",
        transcript_text="Nina will prepare the launch checklist.",
    )
    _second_meeting_id, _second_segment_id, second_action_id = (
        _create_workspace_meeting(
            client,
            workspace_id="workspace-a",
            title="Planning two",
            transcript_text="Nina should prepare launch checklist updates.",
        )
    )

    response = client.get(
        "/api/knowledge/duplicate-actions",
        params={"workspace_id": "workspace-a"},
    )

    assert response.status_code == 200
    groups = response.json()
    assert len(groups) == 1
    assert {item["id"] for item in groups[0]["items"]} == {
        first_action_id,
        second_action_id,
    }
    assert groups[0]["reason"] == "similar_owner_and_description"


def _create_workspace_meeting(
    client: TestClient, *, workspace_id: str, title: str, transcript_text: str
) -> tuple[str, str, str]:
    meeting_id = client.post(
        "/api/meetings",
        json={"title": title, "language": "en", "workspace_id": workspace_id},
    ).json()["id"]
    segment = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 0,
            "end_ms": 1000,
            "text": transcript_text,
            "confidence": 0.95,
        },
    ).json()
    action = client.post(
        f"/api/meetings/{meeting_id}/action-items",
        json={
            "description": "Prepare launch checklist.",
            "owner_text": "Nina",
            "due_text": "Friday",
        },
    ).json()
    client.post(
        f"/api/meetings/{meeting_id}/citations",
        json={
            "target_type": "action_item",
            "target_id": action["id"],
            "segment_id": segment["id"],
            "start_ms": 0,
            "end_ms": 1000,
            "quote": transcript_text,
            "confidence": 0.9,
        },
    )
    return meeting_id, segment["id"], action["id"]

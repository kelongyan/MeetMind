from uuid import UUID

from fastapi.testclient import TestClient

from app.db.models import MeetingSection, QAMessage, QAMessageRole
from app.db.session import SessionLocal
from app.main import app


def test_create_and_list_insights_action_items_and_citations(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    meeting_response = client.post(
        "/api/meetings", json={"title": "Insights"}, headers=auth_headers
    )
    meeting_id = meeting_response.json()["id"]

    segment_response = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 3000,
            "text": "Alex will prepare the database benchmark by Friday.",
            "confidence": 0.9,
        },
        headers=auth_headers,
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
        headers=auth_headers,
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
        headers=auth_headers,
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
        headers=auth_headers,
    )
    assert citation_response.status_code == 201

    insights_response = client.get(
        f"/api/meetings/{meeting_id}/insights", headers=auth_headers
    )
    actions_response = client.get(
        f"/api/meetings/{meeting_id}/action-items", headers=auth_headers
    )
    citations_response = client.get(
        f"/api/meetings/{meeting_id}/citations", headers=auth_headers
    )

    assert [item["id"] for item in insights_response.json()["items"]] == [insight_id]
    assert [item["id"] for item in actions_response.json()["items"]] == [action_id]
    assert citations_response.json()["items"][0]["target_id"] == action_id
    assert citations_response.json()["items"][0]["segment_id"] == segment_id


def test_create_action_item_enforces_initial_status_rules(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Action create rules"}, headers=auth_headers
    ).json()["id"]

    # Creating with status=confirmed and no confirmed_by_user_id now succeeds —
    # the router auto-injects the authenticated user's ID (Phase 5.1).
    auto_confirmed_response = client.post(
        f"/api/meetings/{meeting_id}/action-items",
        json={
            "description": "Prepare the rollout checklist.",
            "status": "confirmed",
        },
        headers=auth_headers,
    )
    terminal_status_response = client.post(
        f"/api/meetings/{meeting_id}/action-items",
        json={
            "description": "Prepare the rollout checklist.",
            "status": "done",
            "confirmed_by_user_id": "user-1",
        },
        headers=auth_headers,
    )
    confirmed_response = client.post(
        f"/api/meetings/{meeting_id}/action-items",
        json={
            "description": "Prepare the rollout checklist.",
            "status": "confirmed",
            "confirmed_by_user_id": "user-1",
        },
        headers=auth_headers,
    )

    assert auto_confirmed_response.status_code == 201
    assert auto_confirmed_response.json()["status"] == "confirmed"
    assert auto_confirmed_response.json()["confirmed_by_user_id"]
    assert auto_confirmed_response.json()["confirmed_at"] is not None
    assert terminal_status_response.status_code == 409
    assert "initial status" in terminal_status_response.json()["detail"].casefold()
    assert confirmed_response.status_code == 201
    assert confirmed_response.json()["status"] == "confirmed"
    assert confirmed_response.json()["confirmed_by_user_id"] == "user-1"
    assert confirmed_response.json()["confirmed_at"] is not None


def test_create_insight_and_action_item_reject_section_from_another_meeting(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    source_meeting_id = client.post(
        "/api/meetings", json={"title": "Source section"}, headers=auth_headers
    ).json()["id"]
    target_meeting_id = client.post(
        "/api/meetings", json={"title": "Target insight"}, headers=auth_headers
    ).json()["id"]
    section_id = _create_section(source_meeting_id)

    insight_response = client.post(
        f"/api/meetings/{target_meeting_id}/insights",
        json={
            "section_id": str(section_id),
            "type": "decision",
            "title": "Wrong section",
            "body": "This should not attach to another meeting section.",
        },
        headers=auth_headers,
    )
    action_response = client.post(
        f"/api/meetings/{target_meeting_id}/action-items",
        json={
            "section_id": str(section_id),
            "description": "This should not attach to another meeting section.",
        },
        headers=auth_headers,
    )

    assert insight_response.status_code == 409
    assert "section" in insight_response.json()["detail"].casefold()
    assert action_response.status_code == 409
    assert "section" in action_response.json()["detail"].casefold()


def test_update_insight_and_action_item_reject_section_from_another_meeting(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    source_meeting_id = client.post(
        "/api/meetings", json={"title": "Source section"}, headers=auth_headers
    ).json()["id"]
    target_meeting_id = client.post(
        "/api/meetings", json={"title": "Target update"}, headers=auth_headers
    ).json()["id"]
    section_id = _create_section(source_meeting_id)
    insight = client.post(
        f"/api/meetings/{target_meeting_id}/insights",
        json={
            "type": "decision",
            "title": "Local insight",
            "body": "This starts in the target meeting.",
        },
        headers=auth_headers,
    ).json()
    action = client.post(
        f"/api/meetings/{target_meeting_id}/action-items",
        json={"description": "This starts in the target meeting."},
        headers=auth_headers,
    ).json()

    insight_response = client.patch(
        f"/api/meetings/{target_meeting_id}/insights/{insight['id']}",
        json={"section_id": str(section_id)},
        headers=auth_headers,
    )
    action_response = client.patch(
        f"/api/meetings/{target_meeting_id}/action-items/{action['id']}",
        json={"section_id": str(section_id)},
        headers=auth_headers,
    )

    assert insight_response.status_code == 409
    assert "section" in insight_response.json()["detail"].casefold()
    assert action_response.status_code == 409
    assert "section" in action_response.json()["detail"].casefold()


def test_create_citation_rejects_answer_from_another_meeting(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    source_meeting_id = client.post(
        "/api/meetings", json={"title": "Source answer"}, headers=auth_headers
    ).json()["id"]
    target_meeting_id = client.post(
        "/api/meetings", json={"title": "Target citation"}, headers=auth_headers
    ).json()["id"]
    segment_id = client.post(
        f"/api/meetings/{target_meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 3000,
            "text": "The target meeting has its own evidence.",
        },
        headers=auth_headers,
    ).json()["id"]
    answer_id = _create_answer_message(source_meeting_id)

    response = client.post(
        f"/api/meetings/{target_meeting_id}/citations",
        json={
            "target_type": "answer",
            "target_id": str(answer_id),
            "segment_id": segment_id,
            "start_ms": 1000,
            "end_ms": 3000,
            "quote": "The target meeting has its own evidence.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert "answer" in response.json()["detail"].casefold()


def _create_section(meeting_id: str) -> UUID:
    with SessionLocal() as session:
        section = MeetingSection(
            meeting_id=UUID(meeting_id),
            title="Source section",
            summary="Only for the source meeting.",
        )
        session.add(section)
        session.commit()
        session.refresh(section)
        return section.id


def _create_answer_message(meeting_id: str) -> UUID:
    with SessionLocal() as session:
        answer = QAMessage(
            meeting_id=UUID(meeting_id),
            conversation_id=UUID("00000000-0000-0000-0000-000000000001"),
            role=QAMessageRole.ASSISTANT,
            content="Source meeting answer.",
            citation_ids=[],
        )
        session.add(answer)
        session.commit()
        session.refresh(answer)
        return answer.id

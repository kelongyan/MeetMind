from uuid import UUID

from fastapi.testclient import TestClient

from app.db.models import EmbeddingSourceType
from app.db.session import SessionLocal
from app.main import app
from app.providers.embedding.base import EmbeddingResponse
from app.retrieval.service import rebuild_meeting_embeddings


class KeywordEmbedder:
    provider_name = "keyword-test"
    model_name = "keyword-1536"

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        return EmbeddingResponse(
            vectors=[_vector_for_text(text) for text in texts],
            model_name=self.model_name,
        )


def test_action_item_confirm_progress_done_preserves_citation(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    meeting_id, _segment_id, action_id = _create_meeting_action_with_citation(
        client, auth_headers
    )

    confirmed = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={
            "status": "confirmed",
            "confirmed_by_user_id": "user-1",
        },
        headers=auth_headers,
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"
    assert confirmed.json()["confirmed_by_user_id"] == "user-1"
    assert confirmed.json()["confirmed_at"] is not None

    in_progress = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={"status": "in_progress"},
        headers=auth_headers,
    )
    done = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={"status": "done"},
        headers=auth_headers,
    )
    citations = client.get(
        f"/api/meetings/{meeting_id}/citations", headers=auth_headers
    ).json()["items"]

    assert in_progress.status_code == 200
    assert done.status_code == 200
    assert done.json()["status"] == "done"
    assert len(citations) == 1
    assert citations[0]["target_id"] == action_id


def test_invalid_status_transition_is_rejected(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    meeting_id, _segment_id, action_id = _create_meeting_action_with_citation(
        client, auth_headers
    )

    # Confirming without explicit confirmed_by_user_id succeeds — router
    # auto-injects the authenticated user's ID (Phase 5.1).
    auto_confirmed = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={"status": "confirmed"},
        headers=auth_headers,
    )
    assert auto_confirmed.status_code == 200
    assert auto_confirmed.json()["status"] == "confirmed"
    assert auto_confirmed.json()["confirmed_by_user_id"]

    invalid_transition = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={"status": "proposed"},
        headers=auth_headers,
    )

    assert invalid_transition.status_code == 409
    assert "transition" in invalid_transition.json()["detail"]


def test_canceled_action_item_is_not_indexed_as_qa_action_source(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    meeting_id, _segment_id, action_id = _create_meeting_action_with_citation(
        client, auth_headers
    )
    response = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={"status": "canceled"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    with SessionLocal() as session:
        result = rebuild_meeting_embeddings(
            session, UUID(meeting_id), embedder=KeywordEmbedder()
        )

    assert EmbeddingSourceType.ACTION_ITEM not in result.source_counts


def test_list_global_action_items_can_filter_by_status(
    auth_headers: dict[str, str],
) -> None:
    client = TestClient(app)
    first_meeting_id, _first_segment_id, first_action_id = (
        _create_meeting_action_with_citation(client, auth_headers)
    )
    second_meeting_id, _second_segment_id, second_action_id = (
        _create_meeting_action_with_citation(client, auth_headers)
    )
    client.patch(
        f"/api/meetings/{first_meeting_id}/action-items/{first_action_id}",
        json={"status": "confirmed", "confirmed_by_user_id": "user-1"},
        headers=auth_headers,
    )
    client.patch(
        f"/api/meetings/{second_meeting_id}/action-items/{second_action_id}",
        json={"status": "canceled"},
        headers=auth_headers,
    )

    all_response = client.get("/api/action-items", headers=auth_headers)
    confirmed_response = client.get(
        "/api/action-items?status=confirmed", headers=auth_headers
    )

    assert all_response.status_code == 200
    assert len(all_response.json()["items"]) == 2
    assert confirmed_response.status_code == 200
    assert [item["id"] for item in confirmed_response.json()["items"]] == [
        first_action_id
    ]


def _create_meeting_action_with_citation(
    client: TestClient, auth_headers: dict[str, str]
) -> tuple[str, str, str]:
    meeting_id = client.post(
        "/api/meetings",
        json={"title": "Lifecycle review", "language": "en"},
        headers=auth_headers,
    ).json()["id"]
    segment = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
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
            "confidence": 0.9,
        },
        headers=auth_headers,
    ).json()
    client.post(
        f"/api/meetings/{meeting_id}/citations",
        json={
            "target_type": "action_item",
            "target_id": action["id"],
            "segment_id": segment["id"],
            "start_ms": 1000,
            "end_ms": 5000,
            "quote": "Nina will own the rollout checklist before Friday.",
            "confidence": 0.92,
        },
        headers=auth_headers,
    )
    return meeting_id, segment["id"], action["id"]


def _vector_for_text(text: str) -> list[float]:
    vector = [0.0] * 1536
    vector[0 if "rollout" in text.lower() else 1] = 1.0
    return vector

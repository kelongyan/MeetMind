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


def test_action_item_confirm_progress_done_preserves_citation() -> None:
    client = TestClient(app)
    meeting_id, _segment_id, action_id = _create_meeting_action_with_citation(client)

    confirmed = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={
            "status": "confirmed",
            "confirmed_by_user_id": "user-1",
        },
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"
    assert confirmed.json()["confirmed_by_user_id"] == "user-1"
    assert confirmed.json()["confirmed_at"] is not None

    in_progress = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={"status": "in_progress"},
    )
    done = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={"status": "done"},
    )
    citations = client.get(f"/api/meetings/{meeting_id}/citations").json()

    assert in_progress.status_code == 200
    assert done.status_code == 200
    assert done.json()["status"] == "done"
    assert len(citations) == 1
    assert citations[0]["target_id"] == action_id


def test_confirm_requires_user_record_and_invalid_transition_is_rejected() -> None:
    client = TestClient(app)
    meeting_id, _segment_id, action_id = _create_meeting_action_with_citation(client)

    missing_user = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={"status": "confirmed"},
    )
    invalid_transition = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={"status": "done"},
    )

    assert missing_user.status_code == 409
    assert "confirmed_by_user_id" in missing_user.json()["detail"]
    assert invalid_transition.status_code == 409
    assert "transition" in invalid_transition.json()["detail"]


def test_canceled_action_item_is_not_indexed_as_qa_action_source() -> None:
    client = TestClient(app)
    meeting_id, _segment_id, action_id = _create_meeting_action_with_citation(client)
    response = client.patch(
        f"/api/meetings/{meeting_id}/action-items/{action_id}",
        json={"status": "canceled"},
    )
    assert response.status_code == 200

    with SessionLocal() as session:
        result = rebuild_meeting_embeddings(
            session, UUID(meeting_id), embedder=KeywordEmbedder()
        )

    assert EmbeddingSourceType.ACTION_ITEM not in result.source_counts


def _create_meeting_action_with_citation(client: TestClient) -> tuple[str, str, str]:
    meeting_id = client.post(
        "/api/meetings", json={"title": "Lifecycle review", "language": "en"}
    ).json()["id"]
    segment = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 5000,
            "text": "Nina will own the rollout checklist before Friday.",
            "confidence": 0.95,
        },
    ).json()
    action = client.post(
        f"/api/meetings/{meeting_id}/action-items",
        json={
            "description": "Prepare the rollout checklist.",
            "owner_text": "Nina",
            "due_text": "Friday",
            "confidence": 0.9,
        },
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
    )
    return meeting_id, segment["id"], action["id"]


def _vector_for_text(text: str) -> list[float]:
    vector = [0.0] * 1536
    vector[0 if "rollout" in text.lower() else 1] = 1.0
    return vector

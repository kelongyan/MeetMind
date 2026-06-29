from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.db.models import EmbeddingSourceType, InsightItem, InsightType, MeetingSection
from app.db.session import SessionLocal
from app.main import app
from app.providers.embedding.base import EmbeddingResponse
from app.retrieval.service import (
    ensure_meeting_embeddings,
    rebuild_meeting_embeddings,
    search_meeting_evidence,
)


class KeywordEmbedder:
    provider_name = "keyword-test"
    model_name = "keyword-1536"

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        vectors: list[list[float]] = []
        for text in texts:
            normalized = text.lower()
            vector = [0.0] * 1536
            if "rollout" in normalized:
                vector[0] = 1.0
            if "budget" in normalized:
                vector[1] = 1.0
            if not any(vector):
                vector[2] = 1.0
            vectors.append(vector)
        return EmbeddingResponse(vectors=vectors, model_name=self.model_name)


class StaticEmbedder:
    provider_name = "static-test"
    model_name = "static-1536"

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        vector = [0.0] * 1536
        vector[1] = 1.0
        return EmbeddingResponse(
            vectors=[list(vector) for _text in texts], model_name=self.model_name
        )


def test_rebuild_embeddings_retrieves_citable_sources_by_meeting() -> None:
    client = TestClient(app)
    meeting_id, _segment_id, _action_id = _create_meeting_with_action_item(
        client,
        title="Launch review",
        transcript_text="Nina will own the rollout checklist before Friday.",
        action_description="Prepare the rollout checklist.",
        owner_text="Nina",
        quote="Nina will own the rollout checklist before Friday.",
    )
    other_meeting_id, _other_segment_id, _other_action_id = (
        _create_meeting_with_action_item(
            client,
            title="Budget review",
            transcript_text="Morgan will own the rollout checklist for budget.",
            action_description="Prepare the rollout budget.",
            owner_text="Morgan",
            quote="Morgan will own the rollout checklist for budget.",
        )
    )
    embedder = KeywordEmbedder()

    with SessionLocal() as session:
        result = rebuild_meeting_embeddings(
            session, UUID(meeting_id), embedder=embedder
        )
        rebuild_meeting_embeddings(session, UUID(other_meeting_id), embedder=embedder)

        hits = search_meeting_evidence(
            session,
            UUID(meeting_id),
            "Who owns the rollout checklist?",
            embedder=embedder,
            limit=5,
        )

    assert result.created_count >= 2
    assert EmbeddingSourceType.TRANSCRIPT_SEGMENT in result.source_counts
    assert EmbeddingSourceType.ACTION_ITEM in result.source_counts
    assert hits
    assert {hit.meeting_id for hit in hits} == {UUID(meeting_id)}
    assert any(hit.source_type == EmbeddingSourceType.ACTION_ITEM for hit in hits)
    assert hits[0].segment_id is not None
    assert "rollout checklist" in hits[0].quote.lower()


def test_rebuild_embeddings_includes_sections_and_insights() -> None:
    client = TestClient(app)
    meeting_id = client.post("/api/meetings", json={"title": "Roadmap"}).json()["id"]
    embedder = KeywordEmbedder()

    with SessionLocal() as session:
        session.add(
            MeetingSection(
                meeting_id=UUID(meeting_id),
                title="Rollout scope",
                summary="The team reviewed rollout milestones.",
                start_ms=1000,
                end_ms=5000,
            )
        )
        session.add(
            InsightItem(
                meeting_id=UUID(meeting_id),
                type=InsightType.DECISION,
                title="Rollout approved",
                body="The team approved the rollout milestones.",
            )
        )
        session.commit()

        result = rebuild_meeting_embeddings(
            session, UUID(meeting_id), embedder=embedder
        )

    assert result.source_counts[EmbeddingSourceType.MEETING_SECTION] == 1
    assert result.source_counts[EmbeddingSourceType.INSIGHT_ITEM] == 1


def test_ensure_embeddings_rebuilds_when_embedding_model_changes() -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Model refresh"}
    ).json()["id"]
    client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 3000,
            "text": "Nina will own the rollout checklist.",
            "confidence": 0.95,
        },
    )

    with SessionLocal() as session:
        rebuild_meeting_embeddings(session, UUID(meeting_id), embedder=StaticEmbedder())
        ensure_meeting_embeddings(session, UUID(meeting_id), embedder=KeywordEmbedder())
        hits = search_meeting_evidence(
            session,
            UUID(meeting_id),
            "Who owns the rollout checklist?",
            embedder=KeywordEmbedder(),
            limit=5,
        )

    assert hits
    assert any("rollout checklist" in hit.quote.lower() for hit in hits)


def test_rebuild_embeddings_preserves_published_meeting_status() -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Published evidence"}
    ).json()["id"]
    client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 3000,
            "text": "Nina will own the rollout checklist.",
            "confidence": 0.95,
        },
    )
    client.patch(f"/api/meetings/{meeting_id}", json={"status": "published"})

    with SessionLocal() as session:
        rebuild_meeting_embeddings(
            session, UUID(meeting_id), embedder=KeywordEmbedder()
        )

    response = client.get(f"/api/meetings/{meeting_id}")

    assert response.json()["status"] == "published"


def test_new_transcript_segment_after_embedding_build_is_searchable() -> None:
    client = TestClient(app)
    meeting_id = client.post("/api/meetings", json={"title": "Live notes"}).json()[
        "id"
    ]
    client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 3000,
            "text": "The budget review is complete.",
            "confidence": 0.92,
        },
    )
    embedder = KeywordEmbedder()

    with SessionLocal() as session:
        rebuild_meeting_embeddings(session, UUID(meeting_id), embedder=embedder)

    client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 4000,
            "end_ms": 7000,
            "text": "Nina will own the rollout checklist.",
            "confidence": 0.95,
        },
    )

    with SessionLocal() as session:
        ensure_meeting_embeddings(session, UUID(meeting_id), embedder=embedder)
        hits = search_meeting_evidence(
            session,
            UUID(meeting_id),
            "Who owns the rollout checklist?",
            embedder=embedder,
            limit=5,
        )

    assert hits
    assert any("rollout checklist" in hit.quote.lower() for hit in hits)


def test_new_action_item_after_embedding_build_is_searchable() -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Action refresh"}
    ).json()["id"]
    segment = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 3000,
            "text": "Nina accepted the follow-up task.",
            "confidence": 0.94,
        },
    ).json()
    embedder = KeywordEmbedder()

    with SessionLocal() as session:
        rebuild_meeting_embeddings(session, UUID(meeting_id), embedder=embedder)

    action = client.post(
        f"/api/meetings/{meeting_id}/action-items",
        json={
            "description": "Prepare the rollout checklist.",
            "owner_text": "Nina",
            "due_text": "Friday",
            "confidence": 0.88,
        },
    ).json()
    client.post(
        f"/api/meetings/{meeting_id}/citations",
        json={
            "target_type": "action_item",
            "target_id": action["id"],
            "segment_id": segment["id"],
            "start_ms": 1000,
            "end_ms": 3000,
            "quote": "Nina accepted the follow-up task.",
            "confidence": 0.9,
        },
    )

    with SessionLocal() as session:
        ensure_meeting_embeddings(session, UUID(meeting_id), embedder=embedder)
        hits = search_meeting_evidence(
            session,
            UUID(meeting_id),
            "Who owns the rollout checklist?",
            embedder=embedder,
            limit=5,
        )

    assert hits
    assert any(hit.source_type == EmbeddingSourceType.ACTION_ITEM for hit in hits)


def test_new_insight_after_embedding_build_is_searchable() -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Insight refresh"}
    ).json()["id"]
    segment = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 3000,
            "text": "The team accepted the proposed change.",
            "confidence": 0.94,
        },
    ).json()
    embedder = KeywordEmbedder()

    with SessionLocal() as session:
        rebuild_meeting_embeddings(session, UUID(meeting_id), embedder=embedder)

    insight = client.post(
        f"/api/meetings/{meeting_id}/insights",
        json={
            "type": "decision",
            "title": "Rollout approved",
            "body": "The rollout checklist can move forward.",
            "confidence": 0.88,
        },
    ).json()
    client.post(
        f"/api/meetings/{meeting_id}/citations",
        json={
            "target_type": "insight_item",
            "target_id": insight["id"],
            "segment_id": segment["id"],
            "start_ms": 1000,
            "end_ms": 3000,
            "quote": "The team accepted the proposed change.",
            "confidence": 0.9,
        },
    )

    with SessionLocal() as session:
        ensure_meeting_embeddings(session, UUID(meeting_id), embedder=embedder)
        hits = search_meeting_evidence(
            session,
            UUID(meeting_id),
            "Was the rollout approved?",
            embedder=embedder,
            limit=5,
        )

    assert hits
    assert any(hit.source_type == EmbeddingSourceType.INSIGHT_ITEM for hit in hits)


def test_text_upload_after_embedding_build_is_searchable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "upload_storage_dir", str(tmp_path / "storage"))
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Upload refresh"}
    ).json()["id"]
    client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 3000,
            "text": "The budget review is complete.",
            "confidence": 0.92,
        },
    )
    embedder = KeywordEmbedder()

    with SessionLocal() as session:
        rebuild_meeting_embeddings(session, UUID(meeting_id), embedder=embedder)

    upload_response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={
            "file": (
                "rollout.txt",
                b"Nina will own the rollout checklist.",
                "text/plain",
            )
        },
    )

    with SessionLocal() as session:
        ensure_meeting_embeddings(session, UUID(meeting_id), embedder=embedder)
        hits = search_meeting_evidence(
            session,
            UUID(meeting_id),
            "Who owns the rollout checklist?",
            embedder=embedder,
            limit=5,
        )

    assert upload_response.status_code == 201
    assert hits
    assert any("rollout checklist" in hit.quote.lower() for hit in hits)


def _create_meeting_with_action_item(
    client: TestClient,
    *,
    title: str,
    transcript_text: str,
    action_description: str,
    owner_text: str,
    quote: str,
) -> tuple[str, str, str]:
    meeting_id = client.post("/api/meetings", json={"title": title}).json()["id"]
    segment = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 5000,
            "text": transcript_text,
            "confidence": 0.92,
        },
    ).json()
    action = client.post(
        f"/api/meetings/{meeting_id}/action-items",
        json={
            "description": action_description,
            "owner_text": owner_text,
            "due_text": "Friday",
            "confidence": 0.88,
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
            "quote": quote,
            "confidence": 0.9,
        },
    )
    return meeting_id, segment["id"], action["id"]

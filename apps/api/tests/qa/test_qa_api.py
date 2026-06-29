from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app
from app.providers.embedding.base import EmbeddingResponse
from app.providers.embedding.dependencies import get_embedder
from app.providers.qa.base import AnswerSynthesisResponse
from app.providers.qa.dependencies import get_answer_synthesizer


class KeywordEmbedder:
    provider_name = "keyword-test"
    model_name = "keyword-1536"

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * 1536
            if "rollout" in text.lower():
                vector[0] = 1.0
            else:
                vector[1] = 1.0
            vectors.append(vector)
        return EmbeddingResponse(vectors=vectors, model_name=self.model_name)


class FakeAnswerSynthesizer:
    provider_name = "fake-answer"
    model_name = "fake-answer-model"

    def synthesize(self, request: object) -> AnswerSynthesisResponse:
        assert request.meeting_id
        assert request.question == "Who owns the rollout checklist?"
        assert request.evidence
        return AnswerSynthesisResponse(
            content="Nina owns the rollout checklist.",
            selected_evidence_ids=[request.evidence[0].id],
            model_name=self.model_name,
        )


class FailingAnswerSynthesizer:
    provider_name = "failing-answer"
    model_name = "failing-answer-model"

    def synthesize(self, request: object) -> AnswerSynthesisResponse:
        raise RuntimeError("answer provider unavailable")


def test_ask_meeting_question_returns_answer_with_citation() -> None:
    app.dependency_overrides[get_embedder] = lambda: KeywordEmbedder()
    app.dependency_overrides[get_answer_synthesizer] = (
        lambda: FakeAnswerSynthesizer()
    )
    client = TestClient(app)
    meeting_id, segment_id = _create_meeting_with_rollout_action(client)

    try:
        response = client.post(
            f"/api/meetings/{meeting_id}/qa",
            json={"question": "Who owns the rollout checklist?"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["question"]["role"] == "user"
    assert body["question"]["content"] == "Who owns the rollout checklist?"
    assert body["answer"]["role"] == "assistant"
    assert body["answer"]["content"] == "Nina owns the rollout checklist."
    assert body["answer"]["model_name"] == "fake-answer-model"
    assert len(body["citations"]) == 1
    assert body["citations"][0]["target_type"] == "answer"
    assert body["citations"][0]["target_id"] == body["answer"]["id"]
    assert body["citations"][0]["segment_id"] == segment_id
    assert body["answer"]["citation_ids"] == [body["citations"][0]["id"]]
    assert UUID(body["conversation_id"])


def test_answer_provider_failure_returns_502_without_saving_messages() -> None:
    app.dependency_overrides[get_embedder] = lambda: KeywordEmbedder()
    app.dependency_overrides[get_answer_synthesizer] = (
        lambda: FailingAnswerSynthesizer()
    )
    client = TestClient(app, raise_server_exceptions=False)
    meeting_id, _segment_id = _create_meeting_with_rollout_action(client)

    try:
        response = client.post(
            f"/api/meetings/{meeting_id}/qa",
            json={"question": "Who owns the rollout checklist?"},
        )
        messages_response = client.get(f"/api/meetings/{meeting_id}/qa")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json()["detail"] == "failing-answer provider call failed"
    assert messages_response.json() == []


def test_ask_meeting_question_refuses_when_no_citable_evidence() -> None:
    app.dependency_overrides[get_embedder] = lambda: KeywordEmbedder()
    client = TestClient(app)
    meeting_id = client.post("/api/meetings", json={"title": "Empty"}).json()["id"]

    try:
        response = client.post(
            f"/api/meetings/{meeting_id}/qa",
            json={"question": "Who owns the rollout checklist?"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]["content"] == (
        "证据不足，无法根据当前会议内容回答这个问题。"
    )
    assert body["citations"] == []
    assert body["answer"]["citation_ids"] == []


def _create_meeting_with_rollout_action(client: TestClient) -> tuple[str, str]:
    meeting_id = client.post(
        "/api/meetings", json={"title": "Launch review", "language": "en"}
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
            "confidence": 0.89,
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
            "confidence": 0.9,
        },
    )
    return meeting_id, segment["id"]

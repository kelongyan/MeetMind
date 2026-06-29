import json
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app
from app.providers.embedding.base import EmbeddingResponse
from app.providers.embedding.dependencies import get_embedder
from app.providers.qa.base import AnswerSynthesisResponse
from app.providers.qa.dependencies import get_answer_synthesizer


class GoldenSampleEmbedder:
    provider_name = "golden-sample"
    model_name = "golden-sample-1536"

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * 1536
            normalized = text.casefold()
            if "rollout" in normalized or "checklist" in normalized:
                vector[0] = 1.0
            else:
                vector[1] = 1.0
            vectors.append(vector)
        return EmbeddingResponse(vectors=vectors, model_name=self.model_name)


class GoldenSampleSynthesizer:
    provider_name = "golden-sample"
    model_name = "golden-sample-answer"

    def synthesize(self, request: object) -> AnswerSynthesisResponse:
        assert request.evidence
        return AnswerSynthesisResponse(
            content="Nina owns the rollout checklist.",
            selected_evidence_ids=[request.evidence[0].id],
            model_name=self.model_name,
        )


def test_phase8_golden_sample_runs_from_upload_to_qa() -> None:
    sample = _load_sample()
    app.dependency_overrides[get_embedder] = lambda: GoldenSampleEmbedder()
    app.dependency_overrides[get_answer_synthesizer] = (
        lambda: GoldenSampleSynthesizer()
    )
    client = TestClient(app)

    try:
        meeting_id = client.post(
            "/api/meetings",
            json={
                "title": sample["title"],
                "language": sample["language"],
            },
        ).json()["id"]
        upload_response = client.post(
            f"/api/meetings/{meeting_id}/assets",
            files={
                "file": (
                    sample["upload_filename"],
                    sample["upload_text"].encode("utf-8"),
                    "text/plain",
                )
            },
        )
        segment = client.post(
            f"/api/meetings/{meeting_id}/transcript",
            json=sample["transcript_segments"][0],
        ).json()
        action = client.post(
            f"/api/meetings/{meeting_id}/action-items",
            json=sample["action_items"][0],
        ).json()
        client.post(
            f"/api/meetings/{meeting_id}/citations",
            json={
                **sample["citations"][0],
                "target_id": action["id"],
                "segment_id": segment["id"],
            },
        )

        qa_response = client.post(
            f"/api/meetings/{meeting_id}/qa",
            json={"question": sample["question"]},
        )
    finally:
        app.dependency_overrides.clear()

    assert upload_response.status_code == 201
    assert upload_response.json()["job"]["job_type"] == "structure"
    assert qa_response.status_code == 200
    body = qa_response.json()
    assert sample["expected_answer_contains"] in body["answer"]["content"]
    assert len(body["citations"]) == 1
    assert UUID(body["conversation_id"])


def _load_sample() -> dict[str, object]:
    sample_path = (
        Path(__file__).resolve().parents[4]
        / "samples"
        / "meetings"
        / "phase8-golden-sample.json"
    )
    return json.loads(sample_path.read_text(encoding="utf-8"))

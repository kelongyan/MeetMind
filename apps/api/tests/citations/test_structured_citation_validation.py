import json
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.structuring import service


class BadCitationExtractor:
    provider_name = "bad-citation-llm"

    def __init__(self, content: str) -> None:
        self.content = content
        self.calls = 0

    def extract(self, request: object) -> SimpleNamespace:
        self.calls += 1
        return SimpleNamespace(
            content=self.content,
            model_name="bad-citation-model",
            model_version="2026-06",
        )


def test_structuring_rejects_citation_time_range_outside_segment() -> None:
    client = TestClient(app)
    meeting_id, segment_id, job_id = _create_meeting(client)
    extractor = BadCitationExtractor(_out_of_range_extraction(segment_id))

    with SessionLocal() as session:
        with pytest.raises(Exception, match="citation"):
            service.run_structuring_job(session, job_id, extractor=extractor)

    assert extractor.calls == 2
    assert client.get(f"/api/jobs/{job_id}").json()["status"] == "failed"
    assert client.get(f"/api/meetings/{meeting_id}/citations").json()["items"] == []


def _create_meeting(client: TestClient) -> tuple[str, str, UUID]:
    meeting_response = client.post("/api/meetings", json={"title": "Citation bounds"})
    meeting_id = meeting_response.json()["id"]
    segment_response = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 2000,
            "text": "Morgan confirmed the rollout risk.",
        },
    )
    job_response = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "structure", "provider": "bad-citation-llm"},
    )
    return meeting_id, segment_response.json()["id"], UUID(job_response.json()["id"])


def _out_of_range_extraction(segment_id: str) -> str:
    return json.dumps(
        {
            "meeting_brief": None,
            "discussion_points": [],
            "decisions": [],
            "risks": [
                {
                    "title": "Rollout risk",
                    "body": "A rollout risk was confirmed.",
                    "confidence": 0.82,
                    "citations": [
                        {
                            "segment_id": segment_id,
                            "start_ms": 0,
                            "end_ms": 3000,
                            "quote": "Morgan confirmed the rollout risk.",
                            "confidence": 0.9,
                        }
                    ],
                }
            ],
            "open_questions": [],
            "action_items": [],
        }
    )

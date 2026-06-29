import json
from types import SimpleNamespace
from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app
from app.providers.llm.dependencies import get_llm_extractor


class EndpointExtractor:
    provider_name = "endpoint-fake-llm"

    def __init__(self, content: str) -> None:
        self.content = content

    def extract(self, request: object) -> SimpleNamespace:
        return SimpleNamespace(
            content=self.content,
            model_name="endpoint-structure-model",
            model_version="2026-06",
        )


def test_structuring_endpoint_uses_llm_provider_dependency() -> None:
    client = TestClient(app)
    meeting_id, segment_id, job_id = _create_meeting(client)
    app.dependency_overrides[get_llm_extractor] = lambda: EndpointExtractor(
        _valid_extraction(segment_id)
    )

    try:
        response = client.post(f"/api/jobs/{job_id}/structure")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["job"]["status"] == "succeeded"
    assert body["job"]["provider"] == "endpoint-fake-llm"
    assert body["action_items"][0]["prompt_version"] == "phase4-structure-v1"
    assert body["action_items"][0]["model_name"] == "endpoint-structure-model"
    assert body["citations"][0]["segment_id"] == segment_id


def _create_meeting(client: TestClient) -> tuple[str, str, UUID]:
    meeting_response = client.post("/api/meetings", json={"title": "Endpoint"})
    meeting_id = meeting_response.json()["id"]
    segment_response = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 0,
            "end_ms": 3000,
            "text": "Nina will publish the launch checklist tomorrow.",
        },
    )
    job_response = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "structure", "provider": "endpoint-fake-llm"},
    )
    return meeting_id, segment_response.json()["id"], UUID(job_response.json()["id"])


def _valid_extraction(segment_id: str) -> str:
    return json.dumps(
        {
            "meeting_brief": None,
            "discussion_points": [],
            "decisions": [],
            "risks": [],
            "open_questions": [],
            "action_items": [
                {
                    "description": "Publish the launch checklist.",
                    "owner_text": "Nina",
                    "due_text": "tomorrow",
                    "confidence": 0.87,
                    "citations": [
                        {
                            "segment_id": segment_id,
                            "start_ms": 0,
                            "end_ms": 3000,
                            "quote": "Nina will publish the launch checklist tomorrow.",
                            "confidence": 0.92,
                        }
                    ],
                }
            ],
        }
    )

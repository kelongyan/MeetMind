import json
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.structuring import service


class FakeExtractor:
    provider_name = "fake-llm"

    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls: list[object] = []

    def extract(self, request: object) -> SimpleNamespace:
        self.calls.append(request)
        index = min(len(self.calls) - 1, len(self.responses) - 1)
        return SimpleNamespace(
            content=self.responses[index],
            model_name="fake-structure-model",
            model_version="2026-06",
        )


def test_run_structuring_job_writes_proposed_outputs_and_citations() -> None:
    client = TestClient(app)
    meeting_id, segment_ids, job_id = _create_meeting_with_structure_job(client)
    extractor = FakeExtractor([_valid_extraction(segment_ids)])

    with SessionLocal() as session:
        result = service.run_structuring_job(session, job_id, extractor=extractor)

    assert result.job.status == "succeeded"
    assert result.job.provider == "fake-llm"
    assert result.job.progress == 100
    assert len(result.insights) == 4
    assert len(result.action_items) == 1
    assert len(result.citations) == 5
    assert {item.status for item in result.insights} == {"proposed"}
    assert {item.prompt_version for item in result.insights} == {
        "phase4-structure-v1"
    }
    assert {item.model_name for item in result.insights} == {
        "fake-structure-model"
    }
    assert result.action_items[0].status == "proposed"
    assert result.action_items[0].created_by_ai is True
    assert result.action_items[0].prompt_version == "phase4-structure-v1"
    assert result.action_items[0].model_name == "fake-structure-model"

    meeting_response = client.get(f"/api/meetings/{meeting_id}")
    insights_response = client.get(f"/api/meetings/{meeting_id}/insights")
    actions_response = client.get(f"/api/meetings/{meeting_id}/action-items")
    citations_response = client.get(f"/api/meetings/{meeting_id}/citations")

    assert meeting_response.json()["status"] == "ready_for_review"
    assert len(insights_response.json()) == 4
    assert len(actions_response.json()) == 1
    assert len(citations_response.json()) == 5
    assert actions_response.json()[0]["prompt_version"] == "phase4-structure-v1"


def test_invalid_llm_json_retries_once_before_persisting_outputs() -> None:
    client = TestClient(app)
    meeting_id, segment_ids, job_id = _create_meeting_with_structure_job(client)
    extractor = FakeExtractor(["{not valid json", _valid_extraction(segment_ids)])

    with SessionLocal() as session:
        result = service.run_structuring_job(session, job_id, extractor=extractor)

    assert result.job.status == "succeeded"
    assert len(extractor.calls) == 2
    retry_request = extractor.calls[1]
    assert "JSON" in retry_request.retry_instruction
    assert client.get(f"/api/meetings/{meeting_id}/action-items").json()[0][
        "description"
    ] == "Prepare the migration plan."


def test_missing_required_citation_fails_job_without_partial_outputs() -> None:
    client = TestClient(app)
    meeting_id, _segment_ids, job_id = _create_meeting_with_structure_job(client)
    extractor = FakeExtractor([_missing_citation_extraction()])

    with SessionLocal() as session:
        with pytest.raises(Exception, match="citation"):
            service.run_structuring_job(session, job_id, extractor=extractor)

    job_response = client.get(f"/api/jobs/{job_id}")
    meeting_response = client.get(f"/api/meetings/{meeting_id}")
    insights_response = client.get(f"/api/meetings/{meeting_id}/insights")
    actions_response = client.get(f"/api/meetings/{meeting_id}/action-items")
    citations_response = client.get(f"/api/meetings/{meeting_id}/citations")

    assert len(extractor.calls) == 2
    assert job_response.json()["status"] == "failed"
    assert job_response.json()["failure_code"] == "structuring_failed"
    assert "citation" in job_response.json()["failure_message"]
    assert meeting_response.json()["status"] == "failed_structuring"
    assert insights_response.json() == []
    assert actions_response.json() == []
    assert citations_response.json() == []


def test_repeated_structuring_run_replaces_previous_generated_results() -> None:
    client = TestClient(app)
    meeting_id, segment_ids, first_job_id = _create_meeting_with_structure_job(client)

    with SessionLocal() as session:
        service.run_structuring_job(
            session,
            first_job_id,
            extractor=FakeExtractor([_valid_extraction(segment_ids)]),
        )

    second_job_response = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "structure", "provider": "fake-llm"},
    )
    second_job_id = UUID(second_job_response.json()["id"])

    with SessionLocal() as session:
        service.run_structuring_job(
            session,
            second_job_id,
            extractor=FakeExtractor([_valid_extraction(segment_ids)]),
        )

    assert len(client.get(f"/api/meetings/{meeting_id}/insights").json()) == 4
    assert len(client.get(f"/api/meetings/{meeting_id}/action-items").json()) == 1
    assert len(client.get(f"/api/meetings/{meeting_id}/citations").json()) == 5


def _create_meeting_with_structure_job(
    client: TestClient,
) -> tuple[str, list[str], UUID]:
    meeting_response = client.post(
        "/api/meetings",
        json={"title": "Phase 4 planning", "language": "en"},
    )
    meeting_id = meeting_response.json()["id"]
    first_segment = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 1000,
            "end_ms": 4000,
            "text": "We decided to use PostgreSQL for the first release.",
            "confidence": 0.94,
        },
    ).json()
    second_segment = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 5000,
            "end_ms": 9000,
            "text": (
                "Alex will prepare the migration plan by Friday and we still "
                "need to confirm backups."
            ),
            "confidence": 0.91,
        },
    ).json()
    job_response = client.post(
        f"/api/meetings/{meeting_id}/process",
        json={"job_type": "structure", "provider": "fake-llm"},
    )
    return meeting_id, [first_segment["id"], second_segment["id"]], UUID(
        job_response.json()["id"]
    )


def _valid_extraction(segment_ids: list[str]) -> str:
    return json.dumps(
        {
            "meeting_brief": {
                "title": "Phase 4 planning summary",
                "summary": "The team chose PostgreSQL and assigned migration work.",
                "confidence": 0.9,
                "citations": [
                    {
                        "segment_id": segment_ids[0],
                        "start_ms": 1000,
                        "end_ms": 4000,
                        "quote": "We decided to use PostgreSQL for the first release.",
                        "confidence": 0.94,
                    }
                ],
            },
            "discussion_points": [],
            "decisions": [
                {
                    "title": "Use PostgreSQL",
                    "body": "The team decided to use PostgreSQL for the first release.",
                    "confidence": 0.91,
                    "citations": [
                        {
                            "segment_id": segment_ids[0],
                            "start_ms": 1000,
                            "end_ms": 4000,
                            "quote": (
                                "We decided to use PostgreSQL for the first release."
                            ),
                            "confidence": 0.94,
                        }
                    ],
                }
            ],
            "risks": [
                {
                    "title": "Backup plan unresolved",
                    "body": "The team still needs to confirm backup handling.",
                    "confidence": 0.82,
                    "citations": [
                        {
                            "segment_id": segment_ids[1],
                            "start_ms": 5000,
                            "end_ms": 9000,
                            "quote": "we still need to confirm backups",
                            "confidence": 0.86,
                        }
                    ],
                }
            ],
            "open_questions": [
                {
                    "title": "Who confirms backups?",
                    "body": "Backup ownership remains open.",
                    "confidence": 0.8,
                    "citations": [
                        {
                            "segment_id": segment_ids[1],
                            "start_ms": 5000,
                            "end_ms": 9000,
                            "quote": "need to confirm backups",
                            "confidence": 0.86,
                        }
                    ],
                }
            ],
            "action_items": [
                {
                    "description": "Prepare the migration plan.",
                    "owner_text": "Alex",
                    "due_text": "Friday",
                    "confidence": 0.88,
                    "citations": [
                        {
                            "segment_id": segment_ids[1],
                            "start_ms": 5000,
                            "end_ms": 9000,
                            "quote": "Alex will prepare the migration plan by Friday",
                            "confidence": 0.9,
                        }
                    ],
                }
            ],
        }
    )


def _missing_citation_extraction() -> str:
    return json.dumps(
        {
            "meeting_brief": None,
            "discussion_points": [],
            "decisions": [],
            "risks": [],
            "open_questions": [],
            "action_items": [
                {
                    "description": "Prepare the migration plan.",
                    "owner_text": "Alex",
                    "due_text": "Friday",
                    "confidence": 0.88,
                    "citations": [],
                }
            ],
        }
    )

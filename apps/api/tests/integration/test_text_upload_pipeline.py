import json
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.providers.llm.dependencies import get_llm_extractor


class UploadedTranscriptExtractor:
    provider_name = "uploaded-transcript-test"

    def extract(self, request: object) -> SimpleNamespace:
        segment = request.transcript[0]
        return SimpleNamespace(
            content=json.dumps(
                {
                    "meeting_brief": None,
                    "discussion_points": [],
                    "decisions": [],
                    "risks": [],
                    "open_questions": [],
                    "action_items": [
                        {
                            "description": "Prepare the rollout checklist.",
                            "owner_text": "Nina",
                            "due_text": "Friday",
                            "confidence": 0.91,
                            "citations": [
                                {
                                    "segment_id": str(segment.segment_id),
                                    "start_ms": segment.start_ms,
                                    "end_ms": segment.end_ms,
                                    "quote": segment.text,
                                    "confidence": 0.94,
                                }
                            ],
                        }
                    ],
                }
            ),
            model_name="uploaded-transcript-model",
            model_version="2026-06",
        )


def test_text_upload_imports_transcript_and_runs_structuring() -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Text import", "language": "en"}
    ).json()["id"]

    upload_response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={
            "file": (
                "rollout.txt",
                b"Nina owns the rollout checklist before Friday.",
                "text/plain",
            )
        },
    )
    job_id = upload_response.json()["job"]["id"]
    transcript_response = client.get(f"/api/meetings/{meeting_id}/transcript")
    app.dependency_overrides[get_llm_extractor] = (
        lambda: UploadedTranscriptExtractor()
    )

    try:
        structure_response = client.post(f"/api/jobs/{job_id}/structure")
    finally:
        app.dependency_overrides.clear()

    assert upload_response.status_code == 201
    assert upload_response.json()["job"]["job_type"] == "structure"
    assert transcript_response.status_code == 200
    transcript = transcript_response.json()
    assert len(transcript) == 1
    assert transcript[0]["text"] == "Nina owns the rollout checklist before Friday."
    assert transcript[0]["start_ms"] == 0
    assert transcript[0]["end_ms"] == 1000
    assert structure_response.status_code == 200
    body = structure_response.json()
    assert body["job"]["status"] == "succeeded"
    assert body["action_items"][0]["owner_text"] == "Nina"
    assert body["citations"][0]["quote"] == transcript[0]["text"]


def test_text_upload_can_auto_run_structuring_pipeline() -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "Auto text import", "language": "en"}
    ).json()["id"]
    app.dependency_overrides[get_llm_extractor] = (
        lambda: UploadedTranscriptExtractor()
    )

    try:
        upload_response = client.post(
            f"/api/meetings/{meeting_id}/assets?auto_process=true",
            files={
                "file": (
                    "rollout.txt",
                    b"Nina owns the rollout checklist before Friday.",
                    "text/plain",
                )
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert upload_response.status_code == 201
    body = upload_response.json()
    assert body["job"]["job_type"] == "structure"
    assert body["job"]["status"] == "succeeded"

    meeting_response = client.get(f"/api/meetings/{meeting_id}")
    action_items_response = client.get(f"/api/meetings/{meeting_id}/action-items")
    citations_response = client.get(f"/api/meetings/{meeting_id}/citations")

    assert meeting_response.json()["status"] == "ready_for_review"
    assert action_items_response.json()[0]["owner_text"] == "Nina"
    assert citations_response.json()[0]["quote"] == (
        "Nina owns the rollout checklist before Friday."
    )


def test_vtt_upload_imports_timed_transcript_segments() -> None:
    client = TestClient(app)
    meeting_id = client.post(
        "/api/meetings", json={"title": "VTT import", "language": "en"}
    ).json()["id"]

    upload_response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={
            "file": (
                "notes.vtt",
                b"WEBVTT\n\n00:00:01.000 --> 00:00:03.500\nNina owns it.\n",
                "text/vtt",
            )
        },
    )
    transcript_response = client.get(f"/api/meetings/{meeting_id}/transcript")

    assert upload_response.status_code == 201
    transcript = transcript_response.json()
    assert len(transcript) == 1
    assert transcript[0]["start_ms"] == 1000
    assert transcript[0]["end_ms"] == 3500
    assert transcript[0]["text"] == "Nina owns it."

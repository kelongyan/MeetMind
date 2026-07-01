import logging

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.observability.provider_telemetry import observe_provider_call, reset_summary


def test_provider_status_reports_configuration_without_secrets(
    monkeypatch, auth_headers: dict[str, str]
) -> None:
    monkeypatch.setattr(settings, "asr_provider", "openai")
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "embedding_provider", "local")
    monkeypatch.setattr(settings, "qa_answer_provider", "extractive")
    monkeypatch.setattr(settings, "openai_api_key", "sk-secret-value")

    response = TestClient(app).get(
        "/api/operations/provider-status", headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["providers"][0] == {
        "capability": "asr",
        "provider": "openai",
        "model": "whisper-1",
        "configured": True,
        "message": "OpenAI ASR is configured.",
    }
    assert body["providers"][1]["capability"] == "llm"
    assert body["providers"][1]["configured"] is True
    assert "sk-secret-value" not in response.text


def test_provider_status_marks_missing_openai_key_as_unconfigured(
    monkeypatch, auth_headers: dict[str, str]
) -> None:
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", None)

    response = TestClient(app).get(
        "/api/operations/provider-status", headers=auth_headers
    )

    assert response.status_code == 200
    llm_status = next(
        item for item in response.json()["providers"] if item["capability"] == "llm"
    )
    assert llm_status["configured"] is False
    assert llm_status["message"] == "OpenAI LLM requires OPENAI_API_KEY."


def test_provider_telemetry_summary_counts_calls_latency_failures_and_cost(
    caplog, auth_headers: dict[str, str]
) -> None:
    reset_summary()

    with caplog.at_level(logging.INFO, logger="meetmind.provider"):
        observe_provider_call(
            operation="llm.extract",
            provider="fake-llm",
            model="fake-model",
            prompt_version="phase-d-test",
            estimated_units=2000,
            cost_per_1k_units_usd=0.03,
            call=lambda: "ok",
        )

        try:
            observe_provider_call(
                operation="llm.extract",
                provider="fake-llm",
                model="fake-model",
                prompt_version="phase-d-test",
                estimated_units=1000,
                cost_per_1k_units_usd=0.03,
                call=lambda: (_ for _ in ()).throw(RuntimeError("timeout")),
            )
        except Exception:
            pass

    response = TestClient(app).get(
        "/api/operations/provider-telemetry", headers=auth_headers
    )

    assert response.status_code == 200
    summary = response.json()["summaries"][0]
    assert summary["provider"] == "fake-llm"
    assert summary["operation"] == "llm.extract"
    assert summary["call_count"] == 2
    assert summary["failure_count"] == 1
    assert summary["cost_estimate_usd"] == 0.09
    assert summary["average_latency_ms"] >= 0


def test_task_sync_status_exposes_adapter_boundary_without_webhook_secret(
    monkeypatch, auth_headers: dict[str, str]
) -> None:
    monkeypatch.setattr(settings, "task_sync_provider", "webhook", raising=False)
    monkeypatch.setattr(
        settings,
        "task_sync_webhook_url",
        "https://hooks.example.test/secret-path",
        raising=False,
    )

    response = TestClient(app).get("/api/operations/task-sync", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "provider": "webhook",
        "configured": True,
        "supports_push": True,
        "message": "Webhook task sync adapter is configured.",
    }
    assert "secret-path" not in response.text

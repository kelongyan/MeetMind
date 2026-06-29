import logging

import pytest

from app.observability.provider_telemetry import (
    ProviderCallError,
    observe_provider_call,
)


def test_provider_call_telemetry_logs_provider_model_prompt_latency_and_cost(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO, logger="meetmind.provider"):
        result = observe_provider_call(
            operation="llm.extract",
            provider="fake-llm",
            model="fake-model",
            prompt_version="phase8-test",
            estimated_units=2500,
            cost_per_1k_units_usd=0.02,
            call=lambda: "ok",
        )

    assert result == "ok"
    record = caplog.records[0]
    assert record.provider == "fake-llm"
    assert record.model == "fake-model"
    assert record.prompt_version == "phase8-test"
    assert record.latency_ms >= 0
    assert record.cost_estimate_usd == 0.05
    assert record.status == "succeeded"


def test_provider_call_telemetry_logs_failure_and_raises_provider_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    def fail() -> str:
        raise RuntimeError("provider is unavailable")

    with caplog.at_level(logging.INFO, logger="meetmind.provider"):
        with pytest.raises(ProviderCallError) as exc_info:
            observe_provider_call(
                operation="qa.synthesize",
                provider="fake-qa",
                model="fake-answer-model",
                prompt_version=None,
                estimated_units=500,
                cost_per_1k_units_usd=0.01,
                call=fail,
            )

    assert "fake-qa provider call failed" in str(exc_info.value)
    record = caplog.records[0]
    assert record.provider == "fake-qa"
    assert record.model == "fake-answer-model"
    assert record.status == "failed"
    assert record.failure_type == "RuntimeError"
    assert record.failure_message == "provider is unavailable"

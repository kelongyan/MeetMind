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
    message = caplog.records[0].getMessage()
    assert "fake-llm" in message
    assert "fake-model" in message
    assert "phase8-test" in message
    assert "succeeded" in message
    assert "provider_call" in message


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
    message = caplog.records[0].getMessage()
    assert "fake-qa" in message
    assert "fake-answer-model" in message
    assert "failed" in message
    assert "RuntimeError" in message
    assert "provider is unavailable" in message

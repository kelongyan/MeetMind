from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter

logger = logging.getLogger("meetmind.provider")


@dataclass
class ProviderTelemetrySummary:
    provider: str
    operation: str
    model: str | None
    prompt_version: str | None
    call_count: int = 0
    failure_count: int = 0
    total_latency_ms: int = 0
    cost_estimate_usd: float = 0.0

    @property
    def average_latency_ms(self) -> int:
        if self.call_count == 0:
            return 0
        return round(self.total_latency_ms / self.call_count)


_summaries: dict[tuple[str, str, str | None, str | None], ProviderTelemetrySummary] = {}


class ProviderCallError(Exception):
    def __init__(self, provider: str | None, operation: str, original: Exception):
        safe_provider = provider or "unknown"
        self.detail = f"{safe_provider} provider call failed"
        self.provider = safe_provider
        self.operation = operation
        self.original = original
        super().__init__(self.detail)


def observe_provider_call[T](
    *,
    operation: str,
    provider: str | None,
    model: str | None,
    prompt_version: str | None,
    estimated_units: int,
    cost_per_1k_units_usd: float,
    call: Callable[[], T],
    model_from_result: Callable[[T], str | None] | None = None,
) -> T:
    started = perf_counter()
    try:
        result = call()
    except Exception as exc:
        latency_ms = _elapsed_ms(started)
        cost_estimate = _estimate_cost(estimated_units, cost_per_1k_units_usd)
        _record_summary(
            operation=operation,
            provider=provider,
            model=model,
            prompt_version=prompt_version,
            latency_ms=latency_ms,
            cost_estimate_usd=cost_estimate,
            failed=True,
        )
        logger.info(
            "provider_call",
            extra={
                "operation": operation,
                "provider": provider,
                "model": model,
                "prompt_version": prompt_version,
                "latency_ms": latency_ms,
                "estimated_units": estimated_units,
                "cost_estimate_usd": cost_estimate,
                "status": "failed",
                "failure_type": type(exc).__name__,
                "failure_message": str(exc),
            },
        )
        raise ProviderCallError(provider, operation, exc) from exc

    latency_ms = _elapsed_ms(started)
    logged_model = model
    if logged_model is None and model_from_result is not None:
        logged_model = model_from_result(result)
    cost_estimate = _estimate_cost(estimated_units, cost_per_1k_units_usd)
    _record_summary(
        operation=operation,
        provider=provider,
        model=logged_model,
        prompt_version=prompt_version,
        latency_ms=latency_ms,
        cost_estimate_usd=cost_estimate,
        failed=False,
    )
    logger.info(
        "provider_call",
        extra={
            "operation": operation,
            "provider": provider,
            "model": logged_model,
            "prompt_version": prompt_version,
            "latency_ms": latency_ms,
            "estimated_units": estimated_units,
            "cost_estimate_usd": cost_estimate,
            "status": "succeeded",
            "failure_type": None,
            "failure_message": None,
        },
    )
    return result


def _elapsed_ms(started: float) -> int:
    return max(0, round((perf_counter() - started) * 1000))


def _estimate_cost(estimated_units: int, cost_per_1k_units_usd: float) -> float:
    return round(max(0, estimated_units) / 1000 * cost_per_1k_units_usd, 8)


def list_summaries() -> list[ProviderTelemetrySummary]:
    return sorted(
        _summaries.values(),
        key=lambda summary: (summary.provider, summary.operation),
    )


def reset_summary() -> None:
    _summaries.clear()


def _record_summary(
    *,
    operation: str,
    provider: str | None,
    model: str | None,
    prompt_version: str | None,
    latency_ms: int,
    cost_estimate_usd: float,
    failed: bool,
) -> None:
    safe_provider = provider or "unknown"
    key = (safe_provider, operation, model, prompt_version)
    summary = _summaries.setdefault(
        key,
        ProviderTelemetrySummary(
            provider=safe_provider,
            operation=operation,
            model=model,
            prompt_version=prompt_version,
        ),
    )
    summary.call_count += 1
    if failed:
        summary.failure_count += 1
    summary.total_latency_ms += latency_ms
    summary.cost_estimate_usd = round(summary.cost_estimate_usd + cost_estimate_usd, 8)

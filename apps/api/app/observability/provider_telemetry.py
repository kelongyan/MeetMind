from __future__ import annotations

import logging
from collections.abc import Callable
from time import perf_counter

logger = logging.getLogger("meetmind.provider")


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
        logger.info(
            "provider_call",
            extra={
                "operation": operation,
                "provider": provider,
                "model": model,
                "prompt_version": prompt_version,
                "latency_ms": latency_ms,
                "estimated_units": estimated_units,
                "cost_estimate_usd": _estimate_cost(
                    estimated_units, cost_per_1k_units_usd
                ),
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
    logger.info(
        "provider_call",
        extra={
            "operation": operation,
            "provider": provider,
            "model": logged_model,
            "prompt_version": prompt_version,
            "latency_ms": latency_ms,
            "estimated_units": estimated_units,
            "cost_estimate_usd": _estimate_cost(
                estimated_units, cost_per_1k_units_usd
            ),
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

from app.config import Settings, settings
from app.observability.provider_telemetry import list_summaries
from app.operations.schemas import (
    ProviderStatusListRead,
    ProviderStatusRead,
    ProviderTelemetryListRead,
    ProviderTelemetrySummaryRead,
    TaskSyncStatusRead,
)


def get_provider_status(config: Settings = settings) -> ProviderStatusListRead:
    return ProviderStatusListRead(
        providers=[
            _openai_provider_status(
                config=config,
                capability="asr",
                provider=config.asr_provider,
                model=config.openai_transcription_model,
                configured_message="OpenAI ASR is configured.",
                missing_key_message="OpenAI ASR requires OPENAI_API_KEY.",
            ),
            _openai_provider_status(
                config=config,
                capability="llm",
                provider=config.llm_provider,
                model=config.openai_llm_model,
                configured_message="OpenAI LLM is configured.",
                missing_key_message="OpenAI LLM requires OPENAI_API_KEY.",
            ),
            _embedding_status(config),
            ProviderStatusRead(
                capability="qa",
                provider=config.qa_answer_provider,
                model=config.qa_answer_provider,
                configured=config.qa_answer_provider != "disabled",
                message=(
                    "Q&A answer provider is configured."
                    if config.qa_answer_provider != "disabled"
                    else "Q&A answer provider is disabled."
                ),
            ),
        ]
    )


def get_provider_telemetry() -> ProviderTelemetryListRead:
    return ProviderTelemetryListRead(
        summaries=[
            ProviderTelemetrySummaryRead(
                provider=summary.provider,
                operation=summary.operation,
                model=summary.model,
                prompt_version=summary.prompt_version,
                call_count=summary.call_count,
                failure_count=summary.failure_count,
                average_latency_ms=summary.average_latency_ms,
                cost_estimate_usd=summary.cost_estimate_usd,
            )
            for summary in list_summaries()
        ]
    )


def get_task_sync_status(config: Settings = settings) -> TaskSyncStatusRead:
    if config.task_sync_provider == "webhook":
        configured = bool(config.task_sync_webhook_url)
        return TaskSyncStatusRead(
            provider="webhook",
            configured=configured,
            supports_push=configured,
            message=(
                "Webhook task sync adapter is configured."
                if configured
                else "Webhook task sync requires TASK_SYNC_WEBHOOK_URL."
            ),
        )
    return TaskSyncStatusRead(
        provider=config.task_sync_provider,
        configured=False,
        supports_push=False,
        message="Task sync adapter is disabled.",
    )


def _openai_provider_status(
    *,
    config: Settings,
    capability: str,
    provider: str,
    model: str,
    configured_message: str,
    missing_key_message: str,
) -> ProviderStatusRead:
    if provider == "openai":
        configured = bool(config.openai_api_key)
        return ProviderStatusRead(
            capability=capability,
            provider=provider,
            model=model,
            configured=configured,
            message=configured_message if configured else missing_key_message,
        )
    return ProviderStatusRead(
        capability=capability,
        provider=provider,
        model=model if provider != "disabled" else None,
        configured=provider != "disabled",
        message=(
            f"{capability.upper()} provider is configured."
            if provider != "disabled"
            else f"{capability.upper()} provider is disabled."
        ),
    )


def _embedding_status(config: Settings) -> ProviderStatusRead:
    if config.embedding_provider == "openai":
        configured = bool(config.openai_api_key)
        return ProviderStatusRead(
            capability="embedding",
            provider="openai",
            model=config.openai_embedding_model,
            configured=configured,
            message=(
                "OpenAI embedding provider is configured."
                if configured
                else "OpenAI embedding requires OPENAI_API_KEY."
            ),
        )
    return ProviderStatusRead(
        capability="embedding",
        provider=config.embedding_provider,
        model=(
            config.local_embedding_model
            if config.embedding_provider == "local"
            else config.embedding_provider
        ),
        configured=config.embedding_provider != "disabled",
        message=(
            "Embedding provider is configured."
            if config.embedding_provider != "disabled"
            else "Embedding provider is disabled."
        ),
    )

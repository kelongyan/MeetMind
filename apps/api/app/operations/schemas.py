from pydantic import BaseModel, ConfigDict


class ProviderStatusRead(BaseModel):
    capability: str
    provider: str
    model: str | None
    configured: bool
    message: str


class ProviderStatusListRead(BaseModel):
    providers: list[ProviderStatusRead]


class ProviderTelemetrySummaryRead(BaseModel):
    provider: str
    operation: str
    model: str | None
    prompt_version: str | None
    call_count: int
    failure_count: int
    average_latency_ms: int
    cost_estimate_usd: float

    model_config = ConfigDict(from_attributes=True)


class ProviderTelemetryListRead(BaseModel):
    summaries: list[ProviderTelemetrySummaryRead]


class TaskSyncStatusRead(BaseModel):
    provider: str
    configured: bool
    supports_push: bool
    message: str

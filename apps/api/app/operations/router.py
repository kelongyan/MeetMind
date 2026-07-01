from fastapi import APIRouter

from app.operations import service
from app.operations.schemas import (
    ProviderStatusListRead,
    ProviderTelemetryListRead,
    TaskSyncStatusRead,
)

router = APIRouter(prefix="/api/operations", tags=["operations"])


@router.get("/provider-status", response_model=ProviderStatusListRead)
def get_provider_status() -> ProviderStatusListRead:
    return service.get_provider_status()


@router.get("/provider-telemetry", response_model=ProviderTelemetryListRead)
def get_provider_telemetry() -> ProviderTelemetryListRead:
    return service.get_provider_telemetry()


@router.get("/task-sync", response_model=TaskSyncStatusRead)
def get_task_sync_status() -> TaskSyncStatusRead:
    return service.get_task_sync_status()

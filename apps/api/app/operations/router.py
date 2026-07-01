from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.db.models import User
from app.operations import service
from app.operations.schemas import (
    ProviderStatusListRead,
    ProviderTelemetryListRead,
    TaskSyncStatusRead,
)

router = APIRouter(prefix="/api/operations", tags=["operations"])


@router.get("/provider-status", response_model=ProviderStatusListRead)
def get_provider_status(
    current_user: User = Depends(get_current_user),
) -> ProviderStatusListRead:
    return service.get_provider_status()


@router.get("/provider-telemetry", response_model=ProviderTelemetryListRead)
def get_provider_telemetry(
    current_user: User = Depends(get_current_user),
) -> ProviderTelemetryListRead:
    return service.get_provider_telemetry()


@router.get("/task-sync", response_model=TaskSyncStatusRead)
def get_task_sync_status(
    current_user: User = Depends(get_current_user),
) -> TaskSyncStatusRead:
    return service.get_task_sync_status()

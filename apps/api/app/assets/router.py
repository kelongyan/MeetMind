from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.assets import service
from app.assets.schemas import AssetUploadRead, MeetingAssetRead
from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db_session
from app.pagination import PaginatedResponse
from app.pipeline import run_pipeline_sync
from app.providers.llm.dependencies import get_llm_extractor
from app.request_dependencies import resolve_request_dependency

router = APIRouter(tags=["assets"])


@router.post(
    "/api/meetings/{meeting_id}/assets",
    response_model=AssetUploadRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_asset(
    meeting_id: UUID,
    request: Request,
    response: Response,
    auto_process: bool = Query(default=False),
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> AssetUploadRead:
    result = await service.upload_asset(session, meeting_id, file)
    if auto_process and result.job is not None:
        extractor = resolve_request_dependency(request, get_llm_extractor)
        run_pipeline_sync(
            session,
            result.job.id,
            extractor=extractor,
        )
        # Pipeline steps commit in separate SessionLocal sessions,
        # so expire the stale ORM object and reload from the database.
        session.expire(result.job)
        session.refresh(result.job)
    if result.duplicate:
        response.status_code = status.HTTP_200_OK
    return result


@router.get(
    "/api/meetings/{meeting_id}/assets",
    response_model=PaginatedResponse[MeetingAssetRead],
)
def list_assets(
    meeting_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[MeetingAssetRead]:
    items = service.list_assets(session, meeting_id, offset=offset, limit=limit)
    total = service.count_assets(session, meeting_id)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)


@router.delete("/api/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: UUID,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    service.delete_asset(session, asset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from uuid import UUID

from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.assets import service
from app.assets.schemas import AssetUploadRead, MeetingAssetRead
from app.db.session import get_db_session

router = APIRouter(tags=["assets"])


@router.post(
    "/api/meetings/{meeting_id}/assets",
    response_model=AssetUploadRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_asset(
    meeting_id: UUID,
    response: Response,
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
) -> AssetUploadRead:
    result = await service.upload_asset(session, meeting_id, file)
    if result.duplicate:
        response.status_code = status.HTTP_200_OK
    return result


@router.get("/api/meetings/{meeting_id}/assets", response_model=list[MeetingAssetRead])
def list_assets(
    meeting_id: UUID, session: Session = Depends(get_db_session)
) -> list[MeetingAssetRead]:
    return service.list_assets(session, meeting_id)


@router.delete("/api/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: UUID, session: Session = Depends(get_db_session)
) -> Response:
    service.delete_asset(session, asset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

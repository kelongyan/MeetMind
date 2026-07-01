"""Export router – Markdown export endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.assets.schemas import MeetingAssetRead
from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db_session
from app.export.service import export_meeting_markdown

router = APIRouter(tags=["export"])


@router.post(
    "/api/meetings/{meeting_id}/export",
    response_model=MeetingAssetRead,
    status_code=status.HTTP_201_CREATED,
)
def export_meeting(
    meeting_id: UUID,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> MeetingAssetRead:
    """Generate a Markdown export of the meeting and return the EXPORT asset."""
    result = export_meeting_markdown(session, meeting_id)
    session.commit()
    return MeetingAssetRead.model_validate(result.asset)


@router.get(
    "/api/meetings/{meeting_id}/export/download",
    responses={200: {"content": {"text/markdown": {}}}},
)
def download_export(
    meeting_id: UUID,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Download the latest Markdown export as a file."""
    from pathlib import Path

    from sqlalchemy import select

    from app.config import settings
    from app.db.models import AssetType, MeetingAsset
    from app.exceptions import NotFoundError

    asset = session.scalar(
        select(MeetingAsset)
        .where(
            MeetingAsset.meeting_id == meeting_id,
            MeetingAsset.asset_type == AssetType.EXPORT,
            MeetingAsset.deleted_at.is_(None),
        )
        .order_by(MeetingAsset.created_at.desc())
    )
    if asset is None:
        raise NotFoundError("No export found for this meeting")

    # Resolve file path from storage_uri
    storage_uri = asset.storage_uri
    if storage_uri.startswith("local://"):
        relative = storage_uri[len("local://") :]
        file_path = Path(settings.upload_storage_dir) / relative
    else:
        raise NotFoundError("Export file not accessible")

    if not file_path.exists():
        raise NotFoundError("Export file not found on disk")

    content = file_path.read_bytes()
    filename = asset.original_filename or f"meeting-{meeting_id}.md"

    return Response(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )

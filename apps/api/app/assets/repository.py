from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import MeetingAsset


def create_asset(session: Session, asset: MeetingAsset) -> MeetingAsset:
    session.add(asset)
    return asset


def get_asset(session: Session, asset_id: UUID) -> MeetingAsset | None:
    return session.get(MeetingAsset, asset_id)


def list_assets(session: Session, meeting_id: UUID) -> list[MeetingAsset]:
    return list(
        session.scalars(
            select(MeetingAsset)
            .where(
                MeetingAsset.meeting_id == meeting_id,
                MeetingAsset.deleted_at.is_(None),
            )
            .order_by(MeetingAsset.created_at, MeetingAsset.id)
        )
    )


def find_active_asset_by_hash(
    session: Session, meeting_id: UUID, file_hash: str
) -> MeetingAsset | None:
    return session.scalar(
        select(MeetingAsset).where(
            MeetingAsset.meeting_id == meeting_id,
            MeetingAsset.sha256 == file_hash,
            MeetingAsset.deleted_at.is_(None),
        )
    )

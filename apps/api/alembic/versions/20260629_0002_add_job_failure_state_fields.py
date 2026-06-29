"""add job failure state fields

Revision ID: 20260629_0002
Revises: 20260629_0001
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260629_0002"
down_revision: str | None = "20260629_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "processing_jobs",
        sa.Column("retryable", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.add_column(
        "processing_jobs",
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.alter_column("processing_jobs", "retryable", server_default=None)


def downgrade() -> None:
    op.drop_column("processing_jobs", "failed_at")
    op.drop_column("processing_jobs", "retryable")

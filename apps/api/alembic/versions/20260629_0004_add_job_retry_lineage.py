"""add job retry lineage

Revision ID: 20260629_0004
Revises: 20260629_0003
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260629_0004"
down_revision: str | None = "20260629_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "processing_jobs",
        sa.Column("retry_of_job_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "processing_jobs",
        sa.Column(
            "attempt_number",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_processing_jobs_retry_of_job_id",
        "processing_jobs",
        "processing_jobs",
        ["retry_of_job_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column("processing_jobs", "attempt_number", server_default=None)


def downgrade() -> None:
    op.drop_constraint(
        "fk_processing_jobs_retry_of_job_id",
        "processing_jobs",
        type_="foreignkey",
    )
    op.drop_column("processing_jobs", "attempt_number")
    op.drop_column("processing_jobs", "retry_of_job_id")

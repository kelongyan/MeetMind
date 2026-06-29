"""add action item model trace fields

Revision ID: 20260629_0003
Revises: 20260629_0002
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260629_0003"
down_revision: str | None = "20260629_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "action_items", sa.Column("model_name", sa.String(length=128), nullable=True)
    )
    op.add_column(
        "action_items", sa.Column("model_version", sa.String(length=128), nullable=True)
    )
    op.add_column(
        "action_items",
        sa.Column("prompt_version", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("action_items", "prompt_version")
    op.drop_column("action_items", "model_version")
    op.drop_column("action_items", "model_name")

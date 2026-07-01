"""add users and provider_telemetry tables

Revision ID: 20260701_0005
Revises: 20260629_0004
Create Date: 2026-07-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260701_0005"
down_revision: str | None = "20260629_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- users table ---
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "admin",
                "member",
                "viewer",
                name="userrole",
                native_enum=False,
                length=64,
            ),
            server_default="member",
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # --- provider_telemetry table ---
    op.create_table(
        "provider_telemetry",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(128), nullable=False),
        sa.Column("operation", sa.String(128), nullable=False),
        sa.Column("model", sa.String(128), nullable=True),
        sa.Column("prompt_version", sa.String(128), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("estimated_units", sa.Integer(), server_default="0", nullable=False),
        sa.Column("cost_estimate_usd", sa.Float(), server_default="0", nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("failure_type", sa.String(128), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("request_id", sa.String(64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_provider_telemetry_provider", "provider_telemetry", ["provider"]
    )
    op.create_index(
        "ix_provider_telemetry_created_at", "provider_telemetry", ["created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_provider_telemetry_created_at", table_name="provider_telemetry")
    op.drop_index("ix_provider_telemetry_provider", table_name="provider_telemetry")
    op.drop_table("provider_telemetry")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

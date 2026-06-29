from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import text

from alembic import command
from app.db.session import engine

DOMAIN_TABLES = (
    "qa_messages",
    "embeddings",
    "citations",
    "action_items",
    "insight_items",
    "meeting_sections",
    "transcript_segments",
    "speakers",
    "processing_jobs",
    "meeting_assets",
    "meetings",
)


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    api_root = Path(__file__).resolve().parents[1]
    alembic_config = Config(str(api_root / "alembic.ini"))
    command.upgrade(alembic_config, "head")


@pytest.fixture(autouse=True)
def clean_database(migrated_database: None) -> None:
    table_list = ", ".join(DOMAIN_TABLES)
    with engine.begin() as connection:
        connection.execute(
            text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE")
        )
    yield
    with engine.begin() as connection:
        connection.execute(
            text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE")
        )

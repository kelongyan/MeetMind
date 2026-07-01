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
    "users",
    "provider_telemetry",
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


@pytest.fixture
def test_user() -> object:
    """Create and return a test user for authentication."""
    import bcrypt

    from app.db.models import User, UserRole
    from app.db.session import SessionLocal

    with SessionLocal() as session:
        user = User(
            email="test@example.com",
            display_name="Test User",
            password_hash=bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode(),
            role=UserRole.MEMBER,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@pytest.fixture
def auth_headers(test_user: object) -> dict[str, str]:
    """Return auth headers with a valid JWT token for the test user."""
    from app.auth.service import create_access_token

    token, _ = create_access_token(test_user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session", autouse=True)
def _disable_auth_for_tests():
    """Disable auth requirement during tests so endpoints work without tokens."""
    from app.config import settings

    original = settings.auth_required
    settings.auth_required = False
    yield
    settings.auth_required = original

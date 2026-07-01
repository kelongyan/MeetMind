import pytest

from app.config import Settings


def test_settings_have_safe_local_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("APP_NAME", "ENVIRONMENT", "DATABASE_URL", "REDIS_URL"):
        monkeypatch.delenv(key, raising=False)

    settings = Settings(_env_file=None)

    assert settings.app_name == "MeetMind API"
    assert settings.environment == "local"
    assert settings.database_url.startswith("postgresql+psycopg://")
    assert settings.redis_url == "redis://localhost:6379/0"


def test_settings_can_load_root_or_local_env_files() -> None:
    assert Settings.model_config["env_file"] == ("../../.env", ".env")

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MeetMind API"
    environment: str = "local"
    database_url: str = (
        "postgresql+psycopg://meetmind:meetmind@localhost:5432/meetmind"
    )
    redis_url: str = "redis://localhost:6379/0"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_bucket_name: str = "meetmind-local"
    upload_storage_dir: str = "storage/uploads"

    model_config = SettingsConfigDict(
        env_file=("../../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

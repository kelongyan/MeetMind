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
    transcription_work_dir: str = "storage/transcription"
    transcription_chunk_ms: int = 600_000
    ffmpeg_binary: str | None = None
    asr_provider: str = "disabled"
    openai_api_key: str | None = None
    openai_transcription_model: str = "whisper-1"

    model_config = SettingsConfigDict(
        env_file=("../../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MeetMind API"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://meetmind:meetmind@localhost:5432/meetmind"
    # Reserved for future Celery / async task queue integration.
    redis_url: str = "redis://localhost:6379/0"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_bucket_name: str = "meetmind-local"
    upload_storage_dir: str = "storage/uploads"
    transcription_work_dir: str = "storage/transcription"
    transcription_chunk_ms: int = 600_000
    ffmpeg_binary: str | None = None
    asr_provider: str = "disabled"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_transcription_model: str = "whisper-1"
    llm_provider: str = "disabled"
    openai_llm_model: str = "gpt-4.1-mini"
    llm_prompt_version: str = "phase4-structure-v1"
    embedding_provider: str = "local"
    local_embedding_model: str = "local-hash-1536"
    openai_embedding_model: str = "text-embedding-3-small"
    # NOTE: Must match the Vector() dimension in db/models.py EmbeddingRecord.
    embedding_dimensions: int = 1536
    qa_answer_provider: str = "extractive"
    qa_min_retrieval_score: float = 0.1
    llm_cost_per_1k_chars_usd: float = 0.0
    embedding_cost_per_1k_chars_usd: float = 0.0
    qa_cost_per_1k_chars_usd: float = 0.0
    task_sync_provider: str = "disabled"
    task_sync_webhook_url: str | None = None
    cors_allowed_origins: list[str] = [
        "http://localhost:3927",
        "http://127.0.0.1:3927",
    ]
    cors_allow_credentials: bool = True
    # Phase 5: Security
    upload_max_size_bytes: int = 500_000_000  # 500 MB
    rate_limit_default: str = "100/minute"
    rate_limit_login: str = "10/minute"
    rate_limit_enabled: bool = True
    # Phase 5: Auth / JWT
    jwt_secret_key: str = "dev-secret-change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours
    auth_required: bool = True
    # Phase 5: Celery
    celery_enabled: bool = False
    # Phase 5: Health check
    health_check_redis: bool = False
    health_check_s3: bool = False

    model_config = SettingsConfigDict(
        env_file=("../../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

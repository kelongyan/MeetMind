from sqlalchemy import inspect

from app.db.session import engine


def test_core_domain_tables_have_expected_columns() -> None:
    inspector = inspect(engine)

    expected_columns = {
        "meetings": {"id", "workspace_id", "title", "status", "created_at"},
        "meeting_assets": {"meeting_id", "asset_type", "storage_uri", "sha256"},
        "processing_jobs": {
            "job_type",
            "status",
            "progress",
            "failure_code",
            "retryable",
            "failed_at",
        },
        "transcript_segments": {"speaker_id", "start_ms", "end_ms", "text"},
        "speakers": {"display_name", "canonical_user_id", "confidence"},
        "meeting_sections": {"title", "summary", "topic_tags"},
        "insight_items": {"type", "status", "model_name", "prompt_version"},
        "action_items": {
            "owner_text",
            "due_date",
            "status",
            "created_by_ai",
            "model_name",
            "prompt_version",
        },
        "citations": {"target_type", "target_id", "segment_id", "quote"},
        "embeddings": {"source_type", "source_id", "embedding_model", "vector"},
        "qa_messages": {"conversation_id", "role", "content", "citation_ids"},
    }

    for table_name, columns in expected_columns.items():
        assert table_name in inspector.get_table_names()
        actual_columns = {
            column["name"] for column in inspector.get_columns(table_name)
        }
        assert columns <= actual_columns

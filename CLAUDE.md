# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**MeetMind** is a trusted meeting intelligence system that converts meeting audio/video/transcripts into verifiable, retrievable, structured team knowledge assets. It emphasizes evidence-based AI outputs with citations, human-in-the-loop review, and anti-hallucination safeguards.

- All UI text and comments are in Chinese (zh-CN)
- Core principles: Source First, Structured First, Evidence First, Human-in-the-loop
- Priority: Correctness > Readability > Maintainability > Performance > Feature Count

## Build & Development Commands

### Prerequisites
- Windows PowerShell (primary shell)
- Docker Desktop
- Node.js + pnpm 11.7.0
- Python 3.12+ with venv at `apps/api/.venv`

### Infrastructure (PostgreSQL + Redis + MinIO)
```
pnpm infra:up          # Start services (data persisted to F:\MeetMind\storage\docker)
pnpm infra:down        # Stop services
```

### Backend (FastAPI at localhost:8000)
```
cd apps/api
.venv\Scripts\python -m alembic upgrade head    # Run migrations
.venv\Scripts\python -m uvicorn app.main:app --reload  # Start dev server
.venv\Scripts\python -m pytest                   # Run all 70 tests
.venv\Scripts\python -m pytest tests/test_meeting_api.py  # Single file
.venv\Scripts\python -m pytest tests/test_meeting_api.py::test_create_meeting  # Single test
.venv\Scripts\python -m ruff check .             # Lint
.venv\Scripts\python -m ruff format .            # Format
```

### Frontend (Next.js at localhost:3927)
```
pnpm --filter @meetmind/web dev       # Start dev server
pnpm --filter @meetmind/web test      # Run vitest + tsc (38 tests)
pnpm --filter @meetmind/web lint      # ESLint
pnpm --filter @meetmind/web typecheck # TypeScript check
pnpm --filter @meetmind/web build     # Production build
```

### Root workspace commands
```
pnpm lint         # Frontend lint only
pnpm typecheck    # Frontend typecheck only
pnpm test         # Frontend test only
```

## Architecture

### Monorepo Structure (pnpm workspace)
```
MeetMind/
  apps/
    api/          FastAPI backend (Python 3.12+)
    web/          Next.js 16 frontend (React 19, TypeScript)
  packages/       Reserved for shared packages (currently empty)
  infra/          Docker Compose + PostgreSQL init scripts
  doc/            Planning docs (00-07)
  samples/        Sample data (phase8-golden-sample.json)
  storage/        Local runtime data (Docker volumes, uploads)
```

### Backend Layered Architecture
Dependency direction: Route -> Service -> Repository -> Database (strict, no reverse)

Each domain module (`apps/api/app/<domain>/`) typically contains:
- `router.py` - FastAPI endpoints (param validation, service calls, response)
- `service.py` - Business logic
- `repository.py` - Data access
- `schemas.py` - Pydantic DTOs

### Key Backend Modules

| Module | Purpose |
|--------|---------|
| meetings/ | Meeting lifecycle, publish validation |
| assets/ | File upload, storage records |
| jobs/ | Processing jobs, retry lineage |
| transcription/ | Audio/text/subtitle transcription |
| structuring/ | LLM extraction, insight generation |
| insights/ | CRUD, review, lifecycle |
| action_items/ | Global action item tracking |
| citations/ | Citation evidence chain |
| qa/ | Meeting Q&A with retrieval |
| retrieval/ | Embedding + vector search |
| providers/ | Provider adapters (ASR/LLM/Embedding/QA) |
| observability/ | Provider telemetry |
| operations/ | Provider status, call summaries |
| knowledge/ | Workspace search, duplicate detection |

### Provider Adapter Pattern
All external capabilities are isolated behind Protocol interfaces:
- Transcriber - transcribe(audio_path, language) -> list[TranscribedSegment]
- LLMExtractor - extract(LLMExtractionRequest) -> LLMExtractionResponse
- Embedder - embed(texts) -> EmbeddingResponse
- AnswerSynthesizer - synthesize(request) -> AnswerSynthesisResponse

Provider selection via `dependencies.py` factory functions, controlled by `settings.*_provider`. Business code only depends on Protocol interfaces, never directly on SDKs.

### Frontend Structure
```
apps/web/
  app/              App Router pages (layout, page, globals.css)
  features/meetings/
    api.ts          API client (createMeetMindApi)
    types.ts        TypeScript types
    view-model.ts   View model utilities
    meeting-workbench.tsx  Main UI component (~16KB)
    components/     Feature-specific components
  components/       Shared UI (layout, ui)
  hooks/            Data hooks (use-jobs, use-meeting-detail, use-meetings, use-qa, use-review, use-upload)
  lib/              Utils
```

### Database (11 tables, PostgreSQL + pgvector)
All models in `apps/api/app/db/models.py` with enum-typed status fields.

Migrations: 4 Alembic revisions in `apps/api/alembic/versions/`.

### Testing Strategy
- Backend: pytest with session-scoped `migrated_database` fixture (runs alembic) and function-scoped `clean_database` fixture (TRUNCATE all 11 domain tables). External providers are mocked.
- Frontend: Vitest + TypeScript type checking. Tests co-located with source (*.test.ts).
- Current baseline: 70 backend tests, 38 frontend tests.

## Code Style & Conventions

### Python (Backend)
- Line length: 88 (ruff default)
- Lint rules: E, F, I, UP, B (B008 ignored)
- Target: Python 3.12
- All API inputs/outputs use Pydantic schemas (never expose ORM objects directly)
- All status fields use StrEnum with enum_type() helper
- Exceptions: NotFoundError (404), ConflictError (409), InvalidFileTypeError (415), ProviderCallError (502)

### TypeScript (Frontend)
- Strict mode enabled
- Module resolution: bundler
- Path alias: @/* maps to ./*
- ESLint: typescript-eslint + @next/eslint-plugin-next
- No UI component library (custom components only)

## Environment Variables

Copy .env.example to .env. Key variables:
- DATABASE_URL, REDIS_URL, S3_ENDPOINT_URL, S3_BUCKET_NAME
- ASR_PROVIDER (openai/disabled), OPENAI_API_KEY
- LLM_PROVIDER (openai/disabled), OPENAI_LLM_MODEL
- EMBEDDING_PROVIDER (local/openai/disabled)
- QA_ANSWER_PROVIDER (extractive/disabled)
- NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

## Git Conventions
- Default branch: main (no feature branches without explicit permission)
- Commit prefixes: feat:, fix:, docs:, refactor:, test:, chore:
- Never use git add . - stage specific files
- Phase tags: phase-0-foundation through phase-8-hardening-and-deploy

## Security Notes
- Never commit .env, API keys, credentials, recordings, or local DB files
- Provider telemetry only records metadata (no full meeting content in logs)
- Operations UI must never display raw API keys/tokens/webhook URLs
- Meeting data is treated as sensitive by default

## Important Architectural Rules
1. AI outputs must be structured objects (not Markdown)
2. Decisions/risks/action items/Q&A answers MUST have citations
3. AI results default to proposed - require user confirmation to become confirmed
4. Anti-hallucination: when evidence is insufficient, explicitly refuse rather than fabricate
5. Prompt versioning: every AI call records provider/model/prompt_version/latency/cost
6. Long meetings must use chunking (never dump full transcript into single LLM call)

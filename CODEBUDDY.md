# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## 项目概述

MeetMind 是一个**可信会议智能系统**，将会议音频/视频/转写文本转化为可验证、可检索、可执行的结构化工作资产。当前 Phase 0-8 全部完成，具备完整的前后端功能。

**核心原则**：Source First、Structured First、Evidence First、Human-in-the-loop。优先级：正确性 > 可读性 > 可维护性 > 性能优化 > 功能数量。

## 常用命令

### 基础设施

```powershell
pnpm infra:up          # 启动 PostgreSQL/pgvector + Redis + MinIO
pnpm infra:down        # 停止所有基础设施服务
```

基础设施数据持久化在 `F:\MeetMind\storage\docker`，避免占用 C 盘。Compose 文件位于 `infra/docker-compose.yml`。

### 后端 (apps/api)

后端使用 Python FastAPI，虚拟环境在 `apps/api/.venv/`，依赖管理用 uv。

```powershell
cd apps/api

# 数据库迁移
.\.venv\Scripts\python -m alembic upgrade head

# 启动开发服务器 (默认 localhost:8000)
.\.venv\Scripts\python -m uvicorn app.main:app --reload

# 运行全部测试 (pytest 配置在 pyproject.toml [tool.pytest.ini_options])
.\.venv\Scripts\python -m pytest

# 运行单个测试文件
.\.venv\Scripts\python -m pytest tests/test_meeting_api.py

# 运行单个测试函数
.\.venv\Scripts\python -m pytest tests/test_meeting_api.py::test_create_meeting

# Lint/格式化
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m ruff format .
```

**测试配置要点**：`migrated_database` fixture（session 级别）自动运行 alembic upgrade head；`clean_database` fixture（function 级别）在每个测试前后 TRUNCATE 全部 11 张域表。测试中默认 mock 外部 provider（ASR/LLM/Embedding/Object Storage）。

### 前端 (apps/web)

前端使用 Next.js 16 + React 19 + TypeScript + TailwindCSS v4，统一通过 pnpm workspace 管理。

```powershell
# 启动开发服务器 (端口 3927)
pnpm --filter @meetmind/web dev

# 运行测试 (vitest run + tsc --noEmit)
pnpm --filter @meetmind/web test

# 类型检查
pnpm --filter @meetmind/web typecheck

# Lint
pnpm --filter @meetmind/web lint

# 构建
pnpm --filter @meetmind/web build
```

## 架构概览

### 整体结构

```
MeetMind/
  apps/
    api/          -- FastAPI 后端 (Python)
    web/          -- Next.js 前端 (TypeScript)
  packages/       -- 共享包（预留）
  infra/          -- Docker Compose + PostgreSQL 初始化脚本
  doc/            -- 方案书（6 份：总览/路线图/架构/技术栈/开发计划/UI 设计）
  samples/        -- 样例数据 (phase8-golden-sample.json)
  storage/        -- 本地存储（Docker 数据卷、上传文件）
  RULE.md         -- 工程纪律（Git/架构/测试/AI 规范/代码审查清单）
```

### 后端分层架构 (Route -> Service -> Repository)

**依赖方向**：API Layer -> Service Layer -> Repository Layer -> Database。禁止反向依赖。

```
app/
  main.py              -- FastAPI 入口，注册路由/中间件/异常处理
  config.py            -- Pydantic Settings（从 .env 读取）
  db/
    base.py            -- SQLAlchemy DeclarativeBase
    models.py          -- 11 个 ORM 模型（全部枚举化状态字段）
    session.py         -- 数据库会话工厂 + get_db_session 依赖
  meetings/            -- 会议域 (router/service/repository/schemas)
  assets/              -- 资源域（文件上传/存储管理）
  jobs/                -- 处理任务域（创建/状态查询/retry/run）
  transcription/       -- 转写域（音频处理/ASR/文本导入/transcript API）
  structuring/         -- 结构化域（LLM 提取/insight 生成/citation 生成）
  insights/            -- 洞察域（CRUD/确认/生命周期）
  citations/           -- 引用域
  qa/                  -- 问答域（基于检索的问答）
  retrieval/           -- 检索域（embedding/向量搜索）
  providers/           -- Provider Adapter 层
    asr/               -- Transcriber Protocol + OpenAI Whisper 实现
    llm/               -- LLMExtractor Protocol + OpenAI 实现
    embedding/         -- Embedder Protocol + OpenAI/local 实现
    qa/                -- AnswerSynthesizer Protocol + 检索合成实现
  object_storage/      -- 本地文件系统存储实现
  observability/       -- Provider 调用追踪
```

### Provider Adapter 核心接口

所有可替换外部能力（ASR/LLM/Embedding/QA/Storage）都通过 Protocol 隔离，业务代码只依赖接口：

- `Transcriber` — `transcribe(audio_path, language) -> list[TranscribedSegment]`
- `LLMExtractor` — `extract(LLMExtractionRequest) -> LLMExtractionResponse`
- `Embedder` — `embed(texts) -> EmbeddingResponse`
- `AnswerSynthesizer` — `synthesize(AnswerSynthesisRequest) -> AnswerSynthesisResponse`

Provider 调用通过 `provider_telemetry` 自动记录：provider、model、prompt_version、latency_ms、estimated_units、cost_estimate_usd、失败信息。日志统一在 `meetmind.provider` logger。

### 数据模型��11 张表）

定义在 `apps/api/app/db/models.py`：

| 模型 | 用途 | 关键状态枚举 |
|---|---|---|
| Meeting | 会议主记录 | MeetingStatus: uploaded -> transcribing -> structuring -> ready_for_review -> published |
| MeetingAsset | 资源文件 | 类型: audio/video/transcript/subtitle/export |
| ProcessingJob | 异步处理任务 | JobStatus: queued -> running -> succeeded/failed |
| Speaker | 发言人 | display_name, canonical_user_id |
| TranscriptSegment | 转写片段 | start_ms, end_ms, text, confidence |
| MeetingSection | 会议段落 | title, topic_tags (JSON) |
| InsightItem | 洞察项 | InsightStatus: proposed -> confirmed/dismissed |
| ActionItem | 行动项 | ActionItemStatus: proposed -> confirmed -> in_progress -> done/canceled |
| Citation | 引用证据链 | target_type, target_id, segment_id, quote |
| EmbeddingRecord | 向量嵌入 | pgvector, 1536 维 |
| QAMessage | 问答消息 | role: user/assistant, citation_ids |

### 前端结构

框架：Next.js 16 (App Router) + React 19 + TailwindCSS v4，无 UI 组件库。

```
apps/web/
  app/
    layout.tsx          -- 根布局 (zh-CN)
    page.tsx            -- 首页 (直接渲染 MeetingWorkbench)
    globals.css         -- Tailwind 全局样式
  features/
    meetings/
      api.ts            -- API Client (createMeetMindApi)
      api.test.ts       -- API Client 测试
      types.ts          -- TypeScript 类型定义
      view-model.ts     -- 视图模型（状态标签/时间格式化/洞察分组/引用映射）
      view-model.test.ts
      meeting-workbench.tsx -- 主工作台组件 (~1400行，包含所有 UI)
  eslint.config.mjs
  next.config.ts
  tsconfig.json
```

状态管理当前使用 React 内置 hooks，架构推荐后续使用 TanStack Query。

### 数据库迁移 (Alembic)

配置文件：`apps/api/alembic.ini`，环境：`apps/api/alembic/env.py`，迁移文件在 `apps/api/alembic/versions/`。已有 4 个迁移（建表、任务失败字段、行动项追踪字段、retry 血统）。

## Git 规范

- 默认只使用 `main` 分支，未经允许不新建分支
- 提交前缀：`feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`
- 阶段 tag 固定命名：`phase-0-foundation` ~ `phase-8-hardening-and-deploy`
- 禁止 `git add .`，优先 stage 明确文件
- 禁止提交：`.env`、密钥、凭证、私密录音、本地数据库、构建产物
- 阶段完成后推送：`git push -u origin main && git push origin <phase-tag>`

## 阶段开发流程

所有阶段定义在 `doc/04-development-plan.md`。开发前必须阅读方案书（`doc/` 目录下 6 份文档）和 `RULE.md`。

阶段完成标准：功能完成、验收标准满足、测试通过、文档更新、commit + tag + push。

## AI 能力规范要点

- **Structured First**：AI 核心输出必须是结构化对象，不是 Markdown
- **Evidence First**：decision/risk/action item/Q&A 答案必须有 citation
- **Human-in-the-loop**：AI 结果默认 proposed，进入 confirmed 必须经用户确认
- **反幻觉**：证据不足时必须明确说明"未在会议记录中找到足够证据"，不允许凭空补 owner/due_date/decision
- **Prompt 版本化**：每次 AI 调用记录 provider/model/prompt_version/input_size/output_size/latency/cost/schema validation

## 环境变量

从 `.env.example` 复制为 `.env` 后使用。关键配置：
- 数据库连接：`DATABASE_URL`
- AI Provider：`OPENAI_API_KEY`、`OPENAI_BASE_URL`
- 对象存储：MinIO access/secret key、endpoint、bucket
- 成本估算：`LLM_COST_PER_1K_CHARS_USD`、`EMBEDDING_COST_PER_1K_CHARS_USD`、`QA_COST_PER_1K_CHARS_USD`
- 模型路由模式：`MODEL_ROUTING_MODE`（local_only / hybrid / cloud_first）

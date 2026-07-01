<div align="center">

# MeetMind

**Trusted meeting intelligence for verifiable team knowledge.**

[![Status](https://img.shields.io/badge/status-product--ready-111827?style=flat-square)](#status)
[![Frontend](https://img.shields.io/badge/frontend-Next.js_16-000000?style=flat-square)](#tech-stack)
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688?style=flat-square)](#tech-stack)
[![Database](https://img.shields.io/badge/database-PostgreSQL_%2B_pgvector-336791?style=flat-square)](#tech-stack)
[![Tests](https://img.shields.io/badge/tests-70_backend_%7C_38_frontend-2563eb?style=flat-square)](#testing)

**English** · [简体中文](#简体中文)

</div>

---

## ✦ Overview

MeetMind is a trusted meeting intelligence workspace that turns meeting audio, video, transcripts, and notes into structured, searchable, and verifiable team assets.

It is not just a meeting summarizer. MeetMind helps teams preserve facts, review AI-generated outputs, trace important decisions back to source evidence, and keep follow-up work visible after the meeting ends.

## ✦ What It Does

### Meeting Workspace

- Create meetings and upload audio, video, transcript, or subtitle files.
- Review timestamped transcript segments.
- Navigate long meetings with generated sections.
- Track processing jobs and retry failed steps.
- Publish reviewed meeting results after quality checks.

### Insights and Action Items

- Extract discussion points, decisions, risks, and open questions.
- Extract action items with owner text, due text, status, and confidence.
- Confirm, dismiss, start, complete, or cancel action items.
- Review action items across meetings with status filters.
- Jump from an action item back to its source meeting.

### Evidence and Q&A

- Store citations for structured outputs and answers.
- Jump from citations back to transcript segments.
- Ask questions against meeting evidence.
- Preserve Q&A history.
- Refuse to invent answers when evidence is insufficient.

### Knowledge Views

- Search transcripts, insights, and action items by workspace.
- Review historical decisions.
- Detect possible duplicate action items.
- Keep cross-meeting results tied to their source meetings.

### Operations Readiness

- View ASR, LLM, Embedding, and Q&A provider status.
- Track provider call count, failure count, average latency, and cost estimate.
- Keep task-sync adapter boundaries explicit.
- Avoid exposing API keys, tokens, or webhook URLs in the UI.

## ✦ Product Principles

| Principle | Meaning |
| --- | --- |
| Source First | Original meeting material remains the source of truth. |
| Structured First | Important outputs are stored as structured data. |
| Evidence First | Decisions, action items, and answers should point back to evidence. |
| Human-in-the-loop | AI output is reviewed before it becomes official. |

## ✦ Tech Stack

| Area | Technology |
| --- | --- |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic |
| Database | PostgreSQL with pgvector |
| Queue / Cache | Redis |
| Object Storage | MinIO / S3-compatible storage |
| AI Providers | Adapter-based ASR, LLM, Embedding, and Q&A providers |
| Quality | pytest, ruff, Vitest, TypeScript, ESLint |
| Package Manager | pnpm |

## ✦ Repository Structure

```text
MeetMind/
  apps/
    api/          FastAPI backend
    web/          Next.js frontend
  infra/          Docker Compose services and database init scripts
  doc/            Project notes, architecture, and progress records
  samples/        Sample meeting data
  storage/        Local runtime storage
  package.json    Workspace scripts
```

Backend modules:

```text
apps/api/app/
  action_items/   Global action-item API
  assets/         Uploads, asset records, and file handling
  db/             SQLAlchemy models and database sessions
  insights/       Insights, action items, citations, and review state
  jobs/           Processing jobs and retry lineage
  knowledge/      Workspace search, decisions, duplicate action candidates
  meetings/       Meeting lifecycle and publish validation
  observability/  Provider telemetry
  operations/     Provider status, telemetry summary, task-sync status
  providers/      ASR, LLM, Embedding, and Q&A adapters
  qa/             Meeting Q&A
  retrieval/      Embedding and evidence retrieval
  structuring/    LLM-based structured extraction
  transcription/  Audio, text, and subtitle transcript processing
```

Frontend modules:

```text
apps/web/features/meetings/
  api.ts                         API client
  types.ts                       Frontend domain types
  meeting-workbench.tsx          Main workspace shell
  components/action-items/       Global action-item view
  components/knowledge/          Knowledge view
  components/meeting-detail/     Meeting detail panels
  components/operations/         Operations readiness view
  components/qa/                 Meeting Q&A UI
  components/transcript/         Transcript and section navigation
```

## ✦ Requirements

- Windows PowerShell
- Docker Desktop
- Node.js with pnpm
- Python 3.12+
- Backend virtual environment at `apps/api/.venv`

## ✦ Configuration

Create a local environment file:

```powershell
Copy-Item .env.example .env
```

Key settings:

```env
DATABASE_URL=postgresql+psycopg://meetmind:meetmind@localhost:5432/meetmind
REDIS_URL=redis://localhost:6379/0
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET_NAME=meetmind-local

ASR_PROVIDER=disabled
OPENAI_API_KEY=
OPENAI_TRANSCRIPTION_MODEL=whisper-1

LLM_PROVIDER=disabled
OPENAI_LLM_MODEL=gpt-4.1-mini
LLM_PROMPT_VERSION=phase4-structure-v1

EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=local-hash-1536
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

QA_ANSWER_PROVIDER=extractive

TASK_SYNC_PROVIDER=disabled
TASK_SYNC_WEBHOOK_URL=
```

By default, ASR and LLM providers are disabled. Local embedding and extractive Q&A are available for development.

## ✦ Development

Install dependencies:

```powershell
pnpm install
```

Start infrastructure:

```powershell
pnpm infra:up
```

Run database migrations:

```powershell
cd apps/api
.\.venv\Scripts\python -m alembic upgrade head
```

Start the API:

```powershell
cd apps/api
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

API:

```text
http://localhost:8000
```

Start the web app:

```powershell
pnpm --filter @meetmind/web dev
```

Web:

```text
http://localhost:3927
```

Stop infrastructure:

```powershell
pnpm infra:down
```

## ✦ Commands

Root workspace:

```powershell
pnpm infra:up
pnpm infra:down
pnpm lint
pnpm typecheck
pnpm test
```

Backend:

```powershell
cd apps/api
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m alembic upgrade head
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

Frontend:

```powershell
pnpm --filter @meetmind/web dev
pnpm --filter @meetmind/web test
pnpm --filter @meetmind/web lint
pnpm --filter @meetmind/web typecheck
pnpm --filter @meetmind/web build
```

## ✦ Testing

Recommended verification:

```powershell
cd apps/api
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .
cd ..\..
pnpm --filter @meetmind/web test
pnpm --filter @meetmind/web lint
pnpm --filter @meetmind/web typecheck
pnpm --filter @meetmind/web build
```

Current baseline:

```text
Backend: 70 tests passing
Frontend: 38 tests passing
```

## ✦ Operations

- Provider telemetry is emitted through the `meetmind.provider` logger.
- Telemetry records provider, model, prompt version, latency, estimated units, cost estimate, and failure metadata.
- The operations view displays provider readiness and aggregated telemetry.
- Task sync currently exposes adapter readiness; deep third-party integrations are disabled by default.
- Docker Compose data is stored under `storage/docker`.

## ✦ Security

- Do not commit `.env`, API keys, credentials, private recordings, local database files, or runtime logs.
- The operations UI must not expose raw API keys, tokens, or webhook URLs.
- Provider telemetry should record metadata, not full meeting text or sensitive prompts.
- AI outputs should remain tied to source evidence whenever possible.

## ✦ Status

MeetMind is currently a local product-ready workspace for trusted meeting processing, review, action tracking, knowledge search, and operations visibility.

Known boundaries:

- Real ASR and LLM quality depends on configured providers and real meeting samples.
- Full enterprise auth, SSO, audit, and multi-tenant governance are not included yet.
- External task systems such as Jira, Linear, Feishu, or Slack are not deeply integrated yet.
- Production deployment hardening remains a future step.

---

## 简体中文

<div align="center">

# MeetMind

**可信会议智能工作台，把会议转化为可验证的团队知识。**

[English](#meetmind) · **简体中文**

</div>

---

## ✦ 产品概览

MeetMind 用于把会议音频、视频、转写文本和人工记录整理成结构化、可检索、可追踪的团队知识资产。

它不只是生成一段会议摘要，而是帮助团队保留会议事实、审阅 AI 输出、把关键结论追溯到原始证据，并让会议后的行动持续可见。

MeetMind 面向会议后的真实协作场景：

- 快速整理 transcript、决策、风险、开放问题和行动项。
- 为关键结论保留原始发言引用，降低 AI 幻觉和误读风险。
- 用户审阅 AI 结果后，再进入正式状态。
- 支持会议内问答，并保留带引用的回答历史。
- 支持跨会议行动项追踪和知识搜索。
- 提供 provider 状态、调用质量和成本估算的运维可见性。

## ✦ 功能特性

### 会议工作台

- 创建会议并上传音频、视频、转写文本或字幕文件。
- 查看带时间戳的 transcript。
- 使用章节导航定位长会议内容。
- 查看处理任务状态并执行 retry。
- 在质量校验通过后发布会议。

### 洞察与行动项

- 提取讨论点、决策、风险和开放问题。
- 提取行动项，包括负责人文本、截止时间文本、状态和置信度。
- 支持确认、驳回、开始、完成或取消行动项。
- 支持跨会议查看行动项，并按状态筛选。
- 可从行动项跳回来源会议。

### 引用与问答

- 为结构化结果和问答答案保存 citation。
- 点击 citation 回到 transcript 对应片段。
- 支持围绕单场会议提问。
- 保存 Q&A 历史。
- 证据不足时拒绝编造答案。

### 知识库

- 按 workspace 搜索 transcript、insight 和 action item。
- 查看历史决策。
- 提示可能重复的行动项。
- 跨会议结果保留来源会议和上下文线索。

### 运维视图

- 查看 ASR、LLM、Embedding、Q&A provider 配置状态。
- 查看 provider 调用次数、失败次数、平均耗时和成本估算。
- 预留任务同步 adapter 边界。
- 不在界面展示 API key、token 或 webhook URL。

## ✦ 产品原则

| 原则 | 说明 |
| --- | --- |
| Source First | 原始会议资料是事实来源 |
| Structured First | 关键输出以结构化数据保存 |
| Evidence First | 决策、行动项和回答尽量带证据 |
| Human-in-the-loop | AI 结果先审阅，再发布 |

## ✦ 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端 | Next.js 16、React 19、TypeScript、Tailwind CSS |
| 后端 | FastAPI、SQLAlchemy、Alembic、Pydantic |
| 数据库 | PostgreSQL、pgvector |
| 队列与缓存 | Redis |
| 对象存储 | MinIO / S3-compatible storage |
| AI 能力 | ASR、LLM、Embedding、Q&A provider adapter |
| 测试与质量 | pytest、ruff、Vitest、TypeScript、ESLint |
| 包管理 | pnpm |

## ✦ 仓库结构

```text
MeetMind/
  apps/
    api/          FastAPI 后端服务
    web/          Next.js 前端应用
  infra/          Docker Compose 和数据库初始化脚本
  doc/            项目资料、架构资料和阶段记录
  samples/        样例会议数据
  storage/        本地运行时存储目录
  package.json    工作区脚本
```

后端主要模块：

```text
apps/api/app/
  action_items/   全局行动项接口
  assets/         上传、资源记录和文件处理
  db/             SQLAlchemy 模型和数据库会话
  insights/       洞察、行动项、引用和审阅状态
  jobs/           处理任务和 retry 血统
  knowledge/      工作区搜索、历史决策、重复行动项提示
  meetings/       会议生命周期和发布校验
  observability/  provider telemetry
  operations/     provider 状态、调用汇总、任务同步状态
  providers/      ASR、LLM、Embedding、Q&A adapter
  qa/             会议问答
  retrieval/      embedding 和证据检索
  structuring/    LLM 结构化提取
  transcription/  音频、文本和字幕转写处理
```

前端主要模块：

```text
apps/web/features/meetings/
  api.ts                         API client
  types.ts                       前端类型定义
  meeting-workbench.tsx          主工作台
  components/action-items/       行动项总览
  components/knowledge/          知识库视图
  components/meeting-detail/     会议详情
  components/operations/         运维视图
  components/qa/                 会议问答
  components/transcript/         transcript 和章节导航
```

## ✦ 环境要求

- Windows PowerShell
- Docker Desktop
- Node.js 与 pnpm
- Python 3.12+
- 后端虚拟环境：`apps/api/.venv`

## ✦ 配置

复制环境变量示例：

```powershell
Copy-Item .env.example .env
```

关键配置：

```env
DATABASE_URL=postgresql+psycopg://meetmind:meetmind@localhost:5432/meetmind
REDIS_URL=redis://localhost:6379/0
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET_NAME=meetmind-local

ASR_PROVIDER=disabled
OPENAI_API_KEY=
OPENAI_TRANSCRIPTION_MODEL=whisper-1

LLM_PROVIDER=disabled
OPENAI_LLM_MODEL=gpt-4.1-mini
LLM_PROMPT_VERSION=phase4-structure-v1

EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=local-hash-1536
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

QA_ANSWER_PROVIDER=extractive

TASK_SYNC_PROVIDER=disabled
TASK_SYNC_WEBHOOK_URL=
```

默认情况下，ASR 和 LLM provider 关闭；本地 embedding 和 extractive Q&A 可用于开发验证。

## ✦ 本地开发

安装依赖：

```powershell
pnpm install
```

启动基础设施：

```powershell
pnpm infra:up
```

执行数据库迁移：

```powershell
cd apps/api
.\.venv\Scripts\python -m alembic upgrade head
```

启动后端：

```powershell
cd apps/api
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

后端默认地址：

```text
http://localhost:8000
```

启动前端：

```powershell
pnpm --filter @meetmind/web dev
```

前端默认地址：

```text
http://localhost:3927
```

停止基础设施：

```powershell
pnpm infra:down
```

## ✦ 常用命令

根目录：

```powershell
pnpm infra:up
pnpm infra:down
pnpm lint
pnpm typecheck
pnpm test
```

后端：

```powershell
cd apps/api
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m alembic upgrade head
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

前端：

```powershell
pnpm --filter @meetmind/web dev
pnpm --filter @meetmind/web test
pnpm --filter @meetmind/web lint
pnpm --filter @meetmind/web typecheck
pnpm --filter @meetmind/web build
```

## ✦ 测试

推荐验证流程：

```powershell
cd apps/api
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .
cd ..\..
pnpm --filter @meetmind/web test
pnpm --filter @meetmind/web lint
pnpm --filter @meetmind/web typecheck
pnpm --filter @meetmind/web build
```

当前基线：

```text
Backend: 70 tests passing
Frontend: 38 tests passing
```

## ✦ 运维说明

- Provider telemetry 使用 `meetmind.provider` logger。
- Telemetry 记录 provider、model、prompt version、latency、estimated units、cost estimate 和失败信息。
- 运维视图展示 provider readiness 和调用汇总。
- 任务同步当前只暴露 adapter readiness，第三方系统深度集成默认未启用。
- Docker Compose 数据默认保存在 `storage/docker` 下。

## ✦ 安全说明

- 不提交 `.env`、API key、凭证、私密录音、本地数据库或运行日志。
- 运维界面不得展示原始 API key、token 或 webhook URL。
- Provider telemetry 只记录元数据，不记录完整会议正文或敏感 prompt。
- AI 输出应尽量绑定来源证据。

## ✦ 当前状态

MeetMind 当前已经具备本地产品可用形态，覆盖会议处理、审阅、行动项追踪、知识搜索和运维可见性。

已知边界：

- 真实 ASR 和 LLM 质量取决于 provider 配置和真实会议样例。
- 企业级权限、SSO、审计和多租户治理尚未完整实现。
- Jira、Linear、飞书、Slack 等外部任务系统尚未深度接入。
- 生产级部署加固仍属于后续工作。

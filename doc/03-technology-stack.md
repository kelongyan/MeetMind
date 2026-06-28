# MeetMind 技术栈方案书

> 版本：2026-06-28  
> 目标：确定 MeetMind 当前阶段的主技术栈、备选方案、取舍理由和禁止过早引入的复杂度。  
> 适用范围：Phase 0 到 Phase 8 的浏览器服务主线开发。

---

## 1. 结论

MeetMind 当前阶段采用：

```text
Next.js Web 前端
  + FastAPI AI 后端
  + PostgreSQL / pgvector
  + Redis / Celery
  + S3-compatible Object Storage
  + FFmpeg
  + ASR / LLM / Embedding Provider Adapter
```

这套技术栈的核心判断是：

- 产品形态优先做浏览器服务。
- AI pipeline 放在 Python 后端。
- 长耗时任务必须异步化。
- 业务数据和向量数据优先统一放在 PostgreSQL。
- 外部模型能力必须通过 adapter 接入，不能绑定单一供应商。
- 第一版先跑通可信会议闭环，不追求实时会议和桌面软件。

---

## 2. 技术选型原则

### 2.1 稳定优先

优先选择成熟、文档完整、社区活跃、容易招聘/协作的技术。MeetMind 的复杂度已经在 AI pipeline、证据链和任务状态流转上，不应该再让基础框架增加额外不确定性。

### 2.2 AI 后端优先 Python

语音识别、音频处理、LLM 编排、embedding、数据评测这些能力在 Python 生态里更顺。后端采用 FastAPI，可以同时获得：

- 类型化 API；
- OpenAPI 文档；
- Pydantic schema；
- Python AI 生态；
- 异步任务和测试工具链。

### 2.3 前端专注工作台体验

前端不承担核心 AI pipeline。Next.js 负责：

- 页面路由；
- 会议工作台；
- 文件上传；
- job 状态展示；
- transcript viewer；
- citations 联动；
- Q&A 交互。

核心业务逻辑放后端，避免 Next.js 和 FastAPI 两边都写一套业务规则。

### 2.4 先单体，后拆分

当前阶段使用模块化单体。不要一开始拆微服务。系统内部通过清晰模块边界组织：

```text
meetings
assets
jobs
transcription
structuring
citations
retrieval
qa
action_items
providers
```

等真实瓶颈出现后，再拆独立 worker、ASR 服务或检索服务。

### 2.5 Provider 可替换

以下能力必须通过 adapter：

- ASR provider
- LLM provider
- Embedding provider
- Object storage provider
- Queue provider

业务代码不直接依赖供应商 SDK。

---

## 3. 推荐技术栈总览

| 层级 | 推荐技术 | 作用 |
| --- | --- | --- |
| 前端框架 | Next.js + React + TypeScript | 浏览器服务主界面 |
| UI | TailwindCSS + shadcn/ui | 快速构建工作台 UI |
| 前端数据 | TanStack Query | 处理请求、缓存、轮询、失败重试 |
| 后端框架 | FastAPI | API、业务服务、AI pipeline 入口 |
| Schema | Pydantic v2 | API schema、AI structured output 校验 |
| ORM | SQLAlchemy 2.x | 数据访问 |
| Migration | Alembic | 数据库迁移 |
| 主数据库 | PostgreSQL | 业务数据 |
| 向量检索 | pgvector | transcript / insight embedding 检索 |
| 队列 | Celery + Redis | 异步任务处理 |
| 文件存储 | S3-compatible storage | 音视频、导出文件、派生文件 |
| 本地对象存储 | MinIO | 本地模拟 S3 |
| 音视频 | FFmpeg | 抽音轨、转码、切片 |
| ASR | OpenAI speech-to-text / faster-whisper adapter | 语音转写 |
| LLM | OpenAI Responses API / 其他 LLM adapter | 结构化理解与问答 |
| Embedding | OpenAI embeddings / 其他 embedding adapter | 语义检索 |
| 后端测试 | pytest | 后端单元和集成测试 |
| 前端测试 | Vitest + Testing Library | 前端组件与逻辑测试 |
| E2E | Playwright | 浏览器端到端流程 |
| Python 工具 | uv + Ruff | 依赖、格式化、lint |
| JS 工具 | pnpm workspace | monorepo 依赖管理 |
| 本地环境 | Docker Compose | PostgreSQL、Redis、MinIO 等依赖 |
| 观测 | OpenTelemetry / Sentry / Langfuse | 日志、错误、LLM 调用追踪 |

---

## 4. 前端技术栈

### 4.1 Next.js + React + TypeScript

推荐理由：

- 适合浏览器服务；
- 路由、构建、开发体验成熟；
- TypeScript 能减少接口对接错误；
- 后续可以支持服务端渲染、静态页面和客户端工作台混合。

使用边界：

- Next.js 负责 UI 和轻量页面逻辑；
- 不把核心 AI pipeline 写进 Next.js；
- 不把数据库访问散落到前端项目；
- 不用 Server Actions 承担核心业务状态流转。

### 4.2 TailwindCSS + shadcn/ui

推荐理由：

- 适合快速构建稳定的后台工作台；
- 组件可复制、可控，不被黑盒设计系统绑死；
- Tailwind 适合维护统一视觉 token；
- shadcn/ui 与 Radix 生态适合无障碍交互。

使用边界：

- 不堆花哨 landing page；
- 重点做信息密度高、可扫描、可操作的工作台；
- transcript、citation、action item 等区域必须支持长内容。

### 4.3 TanStack Query

推荐理由：

- 非常适合处理 job 状态轮询；
- 支持缓存、失败重试、后台刷新；
- 前端不用手写大量请求状态样板代码。

主要用途：

- 会议列表；
- 会议详情；
- 文件上传结果；
- job 状态轮询；
- transcript 加载；
- insight/action item 更新；
- Q&A 请求。

---

## 5. 后端技术栈

### 5.1 FastAPI

推荐理由：

- 与 Python AI 生态自然结合；
- OpenAPI 自动文档方便前后端协作；
- 类型提示和 Pydantic 集成好；
- 对异步接口和文件上传支持成熟。

使用边界：

- Route 层不写复杂业务逻辑；
- Route 调 service；
- service 调 repository 和 provider interface；
- provider implementation 封装具体外部服务。

### 5.2 Pydantic v2

推荐理由：

- API 输入输出校验；
- AI structured output 校验；
- 明确类型边界；
- 避免 LLM 输出直接污染数据库。

主要用途：

- API request / response schema；
- LLM JSON Schema；
- provider result schema；
- job payload schema；
- citation validation schema。

### 5.3 SQLAlchemy 2.x + Alembic

推荐理由：

- SQLAlchemy 成熟稳定；
- Alembic migration 清晰；
- 适合复杂关系数据；
- 后续性能优化空间大。

使用边界：

- ORM model 不直接作为 API response；
- 数据模型变更必须有 migration；
- migration 必须能从空库跑通。

---

## 6. 数据层技术栈

### 6.1 PostgreSQL

推荐理由：

- 适合关系复杂的会议领域模型；
- 支持事务；
- 支持 JSONB；
- 与 pgvector 搭配能同时处理结构化数据和向量检索。

核心表：

- meetings
- meeting_assets
- processing_jobs
- transcript_segments
- meeting_sections
- insight_items
- action_items
- citations
- embeddings
- qa_messages

### 6.2 pgvector

推荐理由：

- MVP 阶段不需要独立向量数据库；
- embedding 可以和 meeting_id、section_id、source_type 等业务字段一起查询；
- 降低部署复杂度；
- 适合单会议和早期多会议知识库检索。

使用边界：

- 第一阶段只做单会议 RAG；
- 多会议规模变大后再评估 Qdrant、Milvus、Pinecone 等独立向量库；
- 不提前引入复杂检索基础设施。

### 6.3 Redis

推荐理由：

- 作为 Celery broker；
- 存储短期任务状态和锁；
- 支持 job 状态轮询辅助；
- 本地部署简单。

使用边界：

- 真实业务状态仍以 PostgreSQL 的 processing_jobs 表为准；
- Redis 不作为唯一真实状态源。

---

## 7. 异步任务技术栈

### 7.1 Celery + Redis

推荐理由：

- 适合长耗时后台任务；
- 支持 retry；
- Python 生态成熟；
- 可以拆独立 worker；
- 适合 ASR、LLM、embedding、导出等任务。

主要任务：

```text
media_normalize
transcribe_meeting
segment_transcript
extract_insights
generate_citations
embed_meeting
answer_question
export_meeting
```

### 7.2 为什么不用纯 FastAPI BackgroundTasks

FastAPI BackgroundTasks 适合轻量任务，不适合：

- 长音频转写；
- 多步骤 pipeline；
- retry；
- 任务监控；
- worker 横向扩展；
- 任务失败恢复。

MeetMind 的处理链路天然需要真正的队列系统。

### 7.3 RQ 作为备选

RQ 更轻，学习成本低，但复杂 pipeline、重试策略和任务编排能力不如 Celery 成熟。可以作为小规模 MVP 备选，但默认推荐 Celery。

---

## 8. 文件与媒体处理

### 8.1 S3-compatible Object Storage

推荐理由：

- 音视频文件不适合放数据库；
- 本地可用 MinIO；
- 云端可切 S3、Cloudflare R2 或其他 S3 兼容服务；
- 方便后续做预签名上传和生命周期策略。

存储对象：

- 原始音频；
- 原始视频；
- 标准化音频；
- 音频切片；
- 导出文件；
- 临时处理产物。

### 8.2 FFmpeg

推荐理由：

- 音视频处理事实标准；
- 支持抽音轨、转码、采样率转换、切片；
- 可通过命令行或 Python wrapper 调用。

使用策略：

- 后端保存原始 asset；
- worker 处理媒体标准化；
- chunk 必须记录原始时间轴偏移；
- 不破坏 transcript 时间戳。

---

## 9. AI 技术栈

### 9.1 ASR

推荐阶段策略：

```text
v0.1:
  优先使用云端 speech-to-text 跑通链路

v0.2:
  接入 faster-whisper 作为本地/低成本转写选项

v0.3:
  接入 WhisperX / pyannote 做发言人识别增强
```

原因：

- 第一阶段最重要的是验证完整链路；
- 本地 ASR 的 CUDA、模型下载、性能差异会拖慢开发；
- provider adapter 能保证后续替换成本低。

必须定义：

```text
Transcriber
  transcribe(audio_asset) -> TranscriptResult
```

### 9.2 LLM

推荐策略：

- 使用支持 structured output 的模型作为主路径；
- 所有关键输出都走 JSON Schema；
- provider 通过 LLMExtractor interface 隔离；
- prompt 必须版本化。

必须定义：

```text
LLMExtractor
  extract_meeting_insights(transcript, schema) -> StructuredInsights
```

### 9.3 Embedding

推荐策略：

- 第一阶段使用一种 embedding provider；
- 向量存储在 pgvector；
- source_type 区分 transcript_segment、meeting_section、insight_item；
- 后续可切换本地 embedding 或其他云端 embedding。

必须定义：

```text
Embedder
  embed(texts) -> vectors
```

### 9.4 不建议第一阶段重度使用 LangChain / LlamaIndex

原因：

- MeetMind pipeline 边界清晰；
- 自己写轻量编排更可控；
- 引用、状态、审阅、版本记录都需要领域定制；
- 重框架可能让调试复杂化。

后续如果进入复杂 agent workflow，再评估 LangGraph 等工具。

---

## 10. 测试与质量工具

### 10.1 后端

推荐：

- pytest
- pytest-asyncio
- httpx test client
- factory-boy 或等价 fixture 工具
- Ruff

重点测试：

- Pydantic schema；
- Job 状态流转；
- Citation 校验；
- Action Item 生命周期；
- Provider adapter mock；
- Q&A 证据不足拒答。

### 10.2 前端

推荐：

- Vitest
- Testing Library
- Playwright
- ESLint
- TypeScript typecheck

重点测试：

- 上传流程；
- job 状态展示；
- transcript viewer；
- citation 点击跳转；
- action item 编辑确认；
- Q&A 引用展示。

### 10.3 Golden Samples

必须准备固定样例：

- 短会议；
- 项目周会；
- 需求评审；
- 技术讨论；
- 噪音或多人发言样例。

样例音频如果包含敏感内容，不进入 Git。

---

## 11. 工具链与仓库管理

### 11.1 pnpm workspace

推荐用于前端和未来 shared package 管理。

JS 依赖管理和脚本执行统一使用 `pnpm`，禁止在项目常规流程中使用 `npm` 或 `yarn`。文档和阶段验收命令必须写成 `pnpm install`、`pnpm lint`、`pnpm typecheck`、`pnpm test` 等形式。

### 11.2 uv

推荐用于 Python 依赖管理和虚拟环境管理。

### 11.3 Docker Compose

推荐用于本地依赖：

```text
PostgreSQL
Redis
MinIO
worker
api
web
```

第一阶段可以先只编排基础依赖，应用服务后续再加入。

---

## 12. 可观测性

### 12.1 第一阶段

先做结构化日志：

- job_id
- meeting_id
- provider
- model
- prompt_version
- latency
- retry_count
- failure_code

### 12.2 后续增强

可接入：

- OpenTelemetry；
- Sentry；
- Langfuse；
- Prometheus / Grafana。

LLM 调用必须保留必要追踪信息，但不能把完整敏感会议内容写入普通日志。

---

## 13. 暂不推荐的技术路线

| 技术/路线 | 当前不推荐原因 |
| --- | --- |
| Electron / Tauri 主产品 | 会被安装、权限、更新、本地环境拖慢 |
| Kubernetes | 太早，Docker Compose 足够 |
| 微服务 | 领域边界还在变化，先模块化单体 |
| 独立向量数据库 | 初期 pgvector 足够 |
| Next.js 全栈承担核心业务 | AI pipeline 更适合 Python 后端 |
| 重度 LangChain / LlamaIndex | 当前 pipeline 清晰，自研轻量编排更可控 |
| 实时会议优先 | 先做好会后可信处理 |
| Supabase 全家桶锁定 | 快但会削弱对 job、pipeline、citation 的控制 |

---

## 14. 最终推荐栈

```text
Web:
  Next.js
  React
  TypeScript
  TailwindCSS
  shadcn/ui
  TanStack Query

API:
  FastAPI
  Pydantic v2
  SQLAlchemy 2.x
  Alembic

Data:
  PostgreSQL
  pgvector
  Redis
  S3-compatible object storage

AI Pipeline:
  FFmpeg
  OpenAI speech-to-text / faster-whisper adapter
  OpenAI Responses API / LLM provider adapter
  Embedding provider adapter
  pgvector retrieval

Async:
  Celery
  Redis
  processing_jobs table as source of truth

Quality:
  pytest
  Vitest
  Playwright
  Ruff
  Docker Compose
```

---

## 15. 技术决策记录

当前已确定：

- 产品主形态优先浏览器服务。
- 后端使用 FastAPI。
- 数据库使用 PostgreSQL。
- 向量检索优先 pgvector。
- 异步任务优先 Celery + Redis。
- 文件存储使用 S3-compatible adapter。
- AI 能力通过 provider adapter 接入。

待开发前最终确认：

- v0.1 ASR 首个 provider 选择云端 speech-to-text 还是本地 faster-whisper。
- v0.1 是否从一开始引入 MinIO，还是先用本地文件系统 adapter。
- 前端组件库是否固定 shadcn/ui。
- 初始 auth 是否暂缓。

# MeetMind 开发进展跟踪

> 更新日期：2026-06-29  
> 用途：记录已完成工作、未完成工作、当前风险和下一步推进重点。  
> 维护规则：每完成一个阶段、一次重要提交或一次验证，都应同步更新本文档。

---

## 1. 总体进度

当前项目已完成 Phase 0-8 的基础建设、核心闭环和稳定性准备，进入 v0.1 手动验证和真实 provider 配置准备阶段。

| 维度 | 当前状态 | 说明 |
| --- | --- | --- |
| 阶段进度 | Phase 0-8 已完成 | 阶段 tag 已推进到 `phase-8-hardening-and-deploy` |
| 后端能力 | 核心闭环已打通 | Meeting、Asset、Job、Transcript、Insight、Citation、Q&A、Review |
| 前端能力 | 会议工作台已具备 | 会议列表、上传、详情、Transcript、洞察、Q&A、审阅动作 |
| 本地依赖 | 可一条命令启动 | `pnpm infra:up` 启动 PostgreSQL/pgvector、Redis、MinIO |
| 测试基线 | 已建立 | 后端 pytest、ruff；前端 lint、typecheck、test、build |
| 部署准备 | 本地部署基线已完成 | README 已补本地启动、备份、重建和 provider telemetry 说明 |

---

## 2. 阶段完成情况

| 阶段 | 状态 | 已完成重点 | 阶段 tag |
| --- | --- | --- | --- |
| Phase 0 工程基线 | Done | pnpm workspace、FastAPI、Next.js、Docker Compose、基础测试 | `phase-0-foundation` |
| Phase 1 后端核心领域 | Done | 核心数据模型、Alembic、Meeting/Job/Transcript/Insight/Citation API | `phase-1-backend-core` |
| Phase 2 上传与异步任务 | Done | 文件上传、hash 去重、Asset 入库、ProcessingJob、失败信息和 retry API | `phase-2-upload-and-jobs` |
| Phase 3 语音转写链路 | Done | FFmpeg 标准化、切片、ASR adapter、Transcript segments 入库 | `phase-3-transcription` |
| Phase 4 结构化理解与引用 | Done | LLM adapter、JSON schema 校验、洞察/行动项/引用落库、prompt/model trace | `phase-4-structuring-and-citations` |
| Phase 5 会议工作台前端 | Done | 会议列表、上传、详情页、Transcript 与洞察联动、基础状态处理 | `phase-5-meeting-workbench` |
| Phase 6 单会议 Q&A | Done | embedding、pgvector 检索、单会议问答、拒答、回答引用 | `phase-6-single-meeting-qa` |
| Phase 7 审阅与行动闭环 | Done | Insight/Action 审阅接口、Action 状态流转、前端审阅操作 | `phase-7-review-and-actions` |
| Phase 8 稳定性与部署准备 | Done | golden sample、provider telemetry、job retry lineage、文件清理、Compose F 盘数据目录 | `phase-8-hardening-and-deploy` |

---

## 3. 已完成工作清单

### 3.1 工程与基础设施

- 使用 `pnpm` 作为统一前端包管理工具。
- 建立 `apps/api`、`apps/web`、`infra`、`samples`、`doc` 的项目结构。
- 建立 Docker Compose 本地依赖：PostgreSQL/pgvector、Redis、MinIO。
- Compose 数据默认写入 `F:\MeetMind\storage\docker`，降低 C 盘占用。
- 建立 `.env.example`，覆盖数据库、Redis、S3、本地存储、provider 和成本估算配置。
- README 已补本地启动、备份、重建、golden sample 和 provider telemetry 说明。

### 3.2 后端能力

- Meeting、Asset、ProcessingJob、TranscriptSegment、InsightItem、ActionItem、Citation、EmbeddingRecord、QAMessage 等核心模型已落库。
- Alembic migration 已覆盖核心表、job 失败状态、Action trace 字段、job retry lineage。
- 上传接口支持音频、视频、文本、字幕文件，并按 hash 识别重复上传。
- 转写链路具备 FFmpeg 标准化、音频切片和 ASR provider adapter。
- 结构化链路具备 LLM provider adapter、JSON schema 校验、citation 校验和失败回滚。
- 单会议 Q&A 支持 embedding 重建、pgvector 检索、证据不足拒答和回答 citation。
- Insight 与 Action Item 支持用户审阅、确认、取消、完成等状态流转。
- Job retry 支持来源追踪、attempt 计数，并拒绝 non-retryable job。
- 删除会议时会同步清理本地上传文件，保持业务数据和文件引用一致。
- Provider telemetry 统一记录 `provider`、`model`、`prompt_version`、`latency_ms`、`estimated_units`、`cost_estimate_usd` 和失败信息。

### 3.3 前端能力

- 建立 Next.js 会议工作台页面。
- 支持会议创建、会议列表、会议选择和详情展示。
- 支持文件上传与处理状态展示。
- 支持 Transcript、洞察、行动项、引用和 Q&A 展示。
- 支持 Insight 与 Action Item 的确认、取消、完成等审阅动作。
- 前端具备 API client、view model 测试和基础状态处理。

### 3.4 测试与验证

- 后端全量测试覆盖健康检查、配置、迁移、Meeting、Asset、Job、Transcription、Structuring、Citation、Retrieval、Q&A、Review、Phase 8 smoke sample。
- 前端覆盖 API client 与 meeting view model 测试。
- Phase 8 golden sample 已加入 `samples\meetings\phase8-golden-sample.json`。
- 当前验证基线：
  - `docker compose -f infra\docker-compose.yml ps`
  - `cd apps/api; .\.venv\Scripts\python -m alembic upgrade head`
  - `cd apps/api; .\.venv\Scripts\python -m pytest`
  - `cd apps/api; .\.venv\Scripts\python -m ruff check .`
  - `pnpm lint`
  - `pnpm typecheck`
  - `pnpm test`
  - `pnpm --filter @meetmind/web build`

---

## 4. 未完成工作与下一步

| 优先级 | 工作项 | 当前状态 | 说明 |
| --- | --- | --- | --- |
| P0 | 手动验证会议工作台主流程 | 未完成 | 用户需在浏览器中手动验证创建会议、上传、查看、审阅、Q&A |
| P0 | 真实 provider 配置验证 | 未完成 | 需要配置真实 OpenAI API key 或其他 provider key，验证 ASR/LLM/Embedding 真实调用 |
| P0 | 真实会议样例验证 | 未完成 | 需要使用一段真实音频或会议材料验证端到端质量 |
| P1 | 后台 worker/队列执行模式 | 未完成 | 当前以 API 触发和本地流程为主，后续可补 Celery worker 编排 |
| P1 | 跨会议知识库 | 未开始 | 当前 Q&A 限定单会议，跨会议检索属于后续路线 |
| P1 | 外部任务系统集成 | 未开始 | Jira、Linear、飞书、Slack 等集成暂未实现 |
| P1 | 用户权限与多租户 | 未开始 | 当前未做企业级权限、组织、角色和审计 |
| P2 | 生产级部署方案 | 未开始 | 当前仅完成本地 Docker Compose 基线，未做云原生编排和自动扩缩容 |
| P2 | 观察性增强 | 未完成 | 后续可加入 request id、结构化 JSON 日志、metrics dashboard 和 tracing |
| P2 | UI 细节打磨 | 未完成 | 需要真实使用后继续补空状态、错误提示、可访问性和移动端细节 |

---

## 5. 当前风险与注意事项

- 真实 provider 的成本、延迟和失败率还没有经过真实会议样例验证。
- 当前 transcription、structuring、embedding 的完整异步 worker 编排还不是生产形态。
- Docker Compose 已把服务数据 bind 到 `F:\MeetMind\storage\docker`，但 Docker Desktop 自身镜像和缓存位置仍需在 Docker Desktop 设置中单独迁移。
- README 中的数据库重建命令会删除 `storage\docker\postgres`，执行前必须先确认备份文件已生成。
- 前端已通过命令验证，但本阶段没有做浏览器人工验证。
- `apps/web/next-env.d.ts` 会被 Next build 自动切换 routes 引用，提交前需要确认没有把生成漂移带入提交。

---

## 6. 进度更新规则

后续推进时按下面规则维护本文档：

1. 完成一个阶段或重要功能后，更新“总体进度”和“阶段完成情况”。
2. 新增能力时，补到“已完成工作清单”的对应分组。
3. 发现未完成事项、风险或技术债时，补到“未完成工作与下一步”或“当前风险与注意事项”。
4. 每次阶段收尾前，确认本文档、`doc/04-development-plan.md` 和 README 状态一致。
5. 提交前运行对应验证命令，并把关键验证结果写入阶段方案书或本文档。

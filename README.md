# MeetMind

MeetMind 是一个面向会议场景的可信会议智能系统，目标是把会议音频、视频、转写文本和人工记录转化为可验证、可检索、可执行的结构化工作资产。

它不是只生成一段会议摘要的工具。MeetMind 更关注会议内容后续能不能被团队真正使用：每个关键结论能否回到原始发言，每个行动项是否有负责人和状态，每次问答是否有证据支撑，会议知识是否能在后续项目推进中继续复用。

---

## 核心闭环

```text
上传会议资料
  -> 生成带时间戳的转写
  -> 结构化提取总结、决策、风险、行动项
  -> 每个关键结论绑定原始发言证据
  -> 用户审阅、修正、确认
  -> 支持基于会议内容的问答
  -> 沉淀为会议知识库
```

---

## 当前方向

- 产品形态：先做浏览器服务，后续扩展桌面助手、本地处理和混合部署。
- 系统架构：模块化单体 + 异步任务队列。
- 主技术栈：Next.js + FastAPI + PostgreSQL/pgvector + Redis/Celery + S3-compatible storage。
- AI 策略：ASR、LLM、Embedding 全部通过 provider adapter 接入。
- 核心原则：Source First、Structured First、Evidence First、Human-in-the-loop。

---

## 文档入口

建议按以下顺序阅读：

| 顺序 | 文档 | 内容 |
| --- | --- | --- |
| 1 | [项目总览](./doc/00-overview.md) | 定位、趋势、核心问题、产品原则、v0.1 成功标准 |
| 2 | [产品路线](./doc/01-product-roadmap.md) | 先浏览器服务，后续桌面/本地/混合部署 |
| 3 | [系统架构](./doc/02-system-architecture.md) | 模块、数据流、数据模型、API、RAG、治理 |
| 4 | [技术栈](./doc/03-technology-stack.md) | 技术选型、备选方案、暂不推荐路线 |
| 5 | [开发计划](./doc/04-development-plan.md) | Phase 0-8、验收标准、阶段 tag |
| 6 | [UI 设计](./doc/05-ui-design.md) | 正式工作台风格、白蓝灰视觉、页面与组件规范 |
| 7 | [开发进展跟踪](./doc/06-progress-tracking.md) | 已完成、未完成、当前风险、整体进度 |
| 8 | [开发规则](./RULE.md) | Git、代码规范、低耦合、测试、安全、阶段交付纪律 |

---

## 本地启动

本项目统一使用 pnpm，不使用 npm/yarn。

```powershell
Copy-Item .env.example .env
pnpm install
pnpm infra:up
cd apps/api
.\.venv\Scripts\python -m alembic upgrade head
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

另开一个 PowerShell 启动前端：

```powershell
pnpm --filter @meetmind/web dev
```

浏览器服务默认运行在 `http://localhost:3927`。核心依赖通过 `pnpm infra:up` 一条命令启动：PostgreSQL/pgvector、Redis、MinIO。Compose 数据默认落在 `F:\MeetMind\storage\docker`，避免占用 C 盘 Docker 默认数据区；如需彻底迁移 Docker Desktop 自身镜像/缓存，仍要在 Docker Desktop 设置里把数据目录迁到 F 盘。

常用维护命令：

```powershell
pnpm infra:down
New-Item -ItemType Directory -Force storage\backups | Out-Null
docker compose -f infra\docker-compose.yml exec -T postgres pg_dump -U meetmind meetmind | Set-Content -Encoding utf8 storage\backups\meetmind.sql
docker compose -f infra\docker-compose.yml down
Remove-Item -Recurse -Force storage\docker\postgres
pnpm infra:up
cd apps/api
.\.venv\Scripts\python -m alembic upgrade head
```

Phase 8 的 golden sample 位于 `samples\meetings\phase8-golden-sample.json`，后端集成测试会用它验证“上传 -> transcript/action/citation -> Q&A”的本地闭环。Provider 日志统一落在 `meetmind.provider` logger，包含 `provider`、`model`、`prompt_version`、`latency_ms`、`estimated_units`、`cost_estimate_usd` 和失败信息。成本估算可通过 `.env` 中的 `LLM_COST_PER_1K_CHARS_USD`、`EMBEDDING_COST_PER_1K_CHARS_USD`、`QA_COST_PER_1K_CHARS_USD` 配置。

---

## 当前仓库状态

当前仓库已完成 Phase 0-8，具备本地核心依赖启动、后端稳定性测试、provider telemetry 和基础部署说明。

已完成：

- 前后端基础工程与 Docker Compose 核心依赖；
- 后端领域模型、上传、转写、结构化、引用、Q&A；
- 前端会议工作台、审阅流与行动项生命周期；
- 本地测试、类型检查和阶段 tag 交付纪律。

下一步：

1. 手动验证会议工作台主要流程。
2. 准备 v0.1 真实会议样例与外部 provider 配置。
3. 按产品路线进入下一轮功能规划。

---

## 最小成功标准

v0.1 只有达到下面标准，才算真正跑通：

- 上传一段真实会议音频后，系统能完成异步处理；
- 用户能看到带时间戳的 transcript；
- 系统能生成结构化 summary、decisions、risks、action items；
- 每个 action item 和 decision 至少有一个 citation；
- 点击 citation 能跳到 transcript 对应位置；
- 用户能修改并确认 action item；
- 用户能向当前会议提问，并得到带引用的回答；
- 当证据不足时，Q&A 会拒绝编造。

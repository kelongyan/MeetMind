# MeetMind 分阶段开发方案书

> 版本：2026-06-28  
> 目标：把 MeetMind 从架构方案推进到可持续开发的工程路线。  
> 原则：每个阶段都必须能独立验收、能回滚、能打标记、能推送。

---

## 1. 开发总目标

MeetMind 的第一条主线是完成一个可信会议智能闭环：

```text
会议创建
  -> 文件上传
  -> 媒体处理
  -> 语音转写
  -> 结构化理解
  -> 引用追溯
  -> 用户审阅
  -> 单会议问答
  -> 行动项状态流转
```

系统不以“功能堆叠”为目标，而以“稳定、可信、可扩展”为目标。每个阶段只解决当前阶段必须解决的问题，避免提前引入复杂度。

---

## 2. 阶段标记规则

每个阶段完成后必须做四件事：

1. 更新本文档的阶段状态。
2. 运行该阶段规定的验证命令。
3. 创建清晰的 Git 提交。
4. 推送 `main` 分支，并创建/推送阶段 tag。

阶段状态统一使用：

```text
Not Started
In Progress
Blocked
Done
```

阶段 tag 统一使用：

```text
phase-0-foundation
phase-1-backend-core
phase-2-upload-and-jobs
phase-3-transcription
phase-4-structuring-and-citations
phase-5-meeting-workbench
phase-6-single-meeting-qa
phase-7-review-and-actions
phase-8-hardening-and-deploy
```

阶段完成提交示例：

```powershell
git add doc/04-development-plan.md RULE.md
git commit -m "docs: add development phases and project rules"
git push -u origin main
```

阶段 tag 示例：

```powershell
git tag phase-0-foundation
git push origin phase-0-foundation
```

---

## 3. 总体里程碑

| 阶段 | 名称 | 状态 | 核心结果 |
| --- | --- | --- | --- |
| Phase 0 | 工程基线 | Done | 项目结构、依赖管理、配置、数据库、测试框架 |
| Phase 1 | 后端核心领域 | Done | Meeting、Asset、Job、Transcript、Insight、Citation 数据模型 |
| Phase 2 | 上传与异步任务 | Done | 文件上传、媒体元数据、任务队列、处理状态 |
| Phase 3 | 语音转写链路 | Done | 音频标准化、ASR adapter、Transcript 入库与展示接口 |
| Phase 4 | 结构化理解与引用 | Done | LLM JSON 输出、Action Items、Decisions、Risks、Citations |
| Phase 5 | 会议工作台前端 | Done | 上传页、会议列表、会议详情、Transcript 与洞察联动 |
| Phase 6 | 单会议 Q&A | Not Started | Embedding、检索、基于引用的回答 |
| Phase 7 | 审阅与行动闭环 | Not Started | AI 结果编辑、确认、Action Item 状态流转 |
| Phase 8 | 稳定性与部署准备 | Not Started | 测试样例、日志、错误恢复、Docker、本地部署说明 |

---

## 4. 工程基线

### 4.1 技术栈来源

技术栈以 `doc/03-technology-stack.md` 为准。本文只记录开发阶段和验收标准，不重复维护完整技术选型，避免后续方案漂移。

当前主栈摘要：

```text
Next.js Web 前端
  + FastAPI AI 后端
  + PostgreSQL / pgvector
  + Redis / Celery
  + S3-compatible Object Storage
  + FFmpeg
  + ASR / LLM / Embedding Provider Adapter
```

### 4.2 代码组织建议

```text
MeetMind/
  apps/
    api/
      app/
        main.py
        config.py
        db/
        meetings/
        assets/
        jobs/
        transcription/
        structuring/
        citations/
        retrieval/
        qa/
        action_items/
        providers/
          asr/
          llm/
          embedding/
      tests/
    web/
      app/
      components/
      features/
      lib/
      tests/
  doc/
    00-overview.md
    01-product-roadmap.md
    02-system-architecture.md
    03-technology-stack.md
    04-development-plan.md
  infra/
    docker-compose.yml
  samples/
    meetings/
  RULE.md
```

---

## 5. Phase 0：工程基线

### 5.1 目标

建立可以长期开发的基础工程结构，确保后续不是在散乱脚本上堆功能。

### 5.2 开发范围

- 初始化 Git 仓库。
- 创建前后端目录结构。
- 建立后端 FastAPI 最小应用。
- 建立前端 Next.js 最小应用。
- 建立 Docker Compose 基础环境。
- 配置 PostgreSQL、pgvector、Redis。
- 配置 `.env.example`。
- 建立后端测试框架。
- 建立前端基础检查命令。
- 建立统一格式化和 lint 规则。

### 5.3 不做范围

- 不实现 ASR。
- 不实现 LLM。
- 不实现完整 UI。
- 不接任何外部系统。

### 5.4 交付物

- `apps/api/` 可启动。
- `apps/web/` 可启动。
- `infra/docker-compose.yml` 可启动数据库和 Redis。
- `RULE.md` 已被项目采用。
- 基础健康检查接口可用。

### 5.5 验收标准

- 后端健康检查返回成功。
- 前端首页能打开。
- PostgreSQL 可连接。
- Redis 可连接。
- 后端测试命令通过。
- 前端 lint 或 typecheck 通过。

### 5.6 建议验证命令

```powershell
docker compose -f infra/docker-compose.yml up -d
cd apps/api
python -m pytest
cd ../web
pnpm lint
pnpm typecheck
```

### 5.7 阶段标记

```powershell
git add apps infra doc RULE.md
git commit -m "chore: establish project foundation"
git tag phase-0-foundation
git push -u origin main
git push origin phase-0-foundation
```

---

## 6. Phase 1：后端核心领域

### 6.1 目标

先把核心领域模型定下来，让后续功能围绕稳定的数据结构生长。

### 6.2 开发范围

- Meeting 模型。
- MeetingAsset 模型。
- ProcessingJob 模型。
- TranscriptSegment 模型。
- Speaker 模型。
- MeetingSection 模型。
- InsightItem 模型。
- ActionItem 模型。
- Citation 模型。
- EmbeddingRecord 模型。
- QAMessage 模型。
- Alembic migration。
- 基础 CRUD service。
- 基础 API 路由。

### 6.3 不做范围

- 不调用真实 ASR。
- 不调用真实 LLM。
- 不实现复杂权限。
- 不做前端复杂页面。

### 6.4 交付物

- 数据表可创建。
- 基础 Meeting API 可用。
- Job 状态可以创建和查询。
- Transcript segment 可以写入和读取。
- Insight、ActionItem、Citation 可以写入和读取。

### 6.5 验收标准

- migration 能从空数据库跑通。
- 所有模型字段与 `doc/02-system-architecture.md` 一致。
- 核心 API 有测试覆盖。
- 服务层不直接依赖具体 AI provider。

### 6.6 建议验证命令

```powershell
cd apps/api
alembic upgrade head
python -m pytest tests/meetings tests/jobs tests/transcripts tests/insights
```

### 6.7 阶段标记

```powershell
git add apps/api
git commit -m "feat: add backend domain models and core APIs"
git tag phase-1-backend-core
git push -u origin main
git push origin phase-1-backend-core
```

---

## 7. Phase 2：上传与异步任务

### 7.1 目标

让系统能够接收会议资料，并用异步任务状态管理后续处理。

### 7.2 开发范围

- 文件上传 API。
- 文件类型校验。
- 文件 hash 计算。
- 原始文件保存。
- Asset 元数据入库。
- ProcessingJob 创建。
- Job 状态流转。
- 失败状态记录。
- Retry 接口。

### 7.3 不做范围

- 不做真实语音识别。
- 不做复杂对象存储权限。
- 不做大规模并发上传优化。

### 7.4 交付物

- 用户可以创建会议并上传音频、视频、文本或字幕。
- 上传成功后能看到 asset 记录。
- 后端能创建处理任务。
- job 可以进入 queued、running、succeeded、failed 状态。

### 7.5 验收标准

- 非法文件类型被拒绝。
- 文件 hash 可用于识别重复上传。
- 上传 API 不阻塞长时间处理。
- Job 失败时有 failure_code 和 failure_message。
- Retry 不产生重复 asset。

### 7.6 建议验证命令

```powershell
cd apps/api
python -m pytest tests/assets tests/jobs
```

### 7.7 阶段标记

```powershell
git add apps/api
git commit -m "feat: add asset upload and processing jobs"
git tag phase-2-upload-and-jobs
git push -u origin main
git push origin phase-2-upload-and-jobs
```

---

## 8. Phase 3：语音转写链路

### 8.1 目标

完成从音频文件到带时间戳 transcript segments 的最小可用链路。

### 8.2 开发范围

- FFmpeg 音频标准化。
- 音频时长读取。
- 长音频切片。
- 切片偏移记录。
- `Transcriber` provider interface。
- 一个真实 ASR provider 实现。
- transcript segments 入库。
- Transcript API。

### 8.3 不做范围

- 不强依赖真实发言人身份。
- 不做实时转写。
- 不做音频降噪高级算法。

### 8.4 交付物

- 上传音频后可以触发转写。
- 转写结果包含 start_ms、end_ms、text、confidence。
- 前端或 API 可以按时间顺序读取 transcript。

### 8.5 验收标准

- 5 分钟样例音频可完整转写。
- 长音频切片后时间戳仍然连续。
- ASR provider 可被 mock 替换。
- 转写失败不影响 meeting 和 asset 数据。

### 8.6 建议验证命令

```powershell
cd apps/api
python -m pytest tests/transcription
python -m pytest tests/integration/test_transcription_pipeline.py
```

### 8.7 阶段标记

```powershell
git add apps/api samples
git commit -m "feat: add transcription pipeline"
git tag phase-3-transcription
git push -u origin main
git push origin phase-3-transcription
```

---

## 9. Phase 4：结构化理解与引用

### 9.1 目标

让系统从 transcript 中生成结构化洞察，并把关键结论绑定到原始发言证据。

### 9.2 开发范围

- `LLMExtractor` provider interface。
- 结构化输出 JSON Schema。
- Pydantic 校验。
- Meeting summary 生成。
- Decisions 提取。
- Risks 提取。
- Open questions 提取。
- Action Items 提取。
- Citation 生成。
- Citation 校验。
- Prompt version 记录。

### 9.3 不做范围

- 不自动创建外部任务。
- 不把 AI 输出直接视为已确认结果。
- 不做跨会议知识库。

### 9.4 交付物

- 对已有 transcript 可触发结构化理解。
- 可通过 `POST /api/jobs/{job_id}/structure` 运行 `structure` job。
- insight_items、action_items、citations 正常入库。
- 每个 action item 和 decision 至少绑定一个 citation。
- 结构化结果状态默认为 proposed。

### 9.5 验收标准

- LLM 返回非法 JSON 时，系统能记录错误并重试一次。
- 缺少 citation 的关键对象不能进入 ready 状态。
- 同一 transcript 重复运行不会产生无法区分的重复结果。
- Prompt 版本和 model 信息可追踪。

### 9.6 建议验证命令

```powershell
cd apps/api
python -m pytest tests/structuring tests/citations
python -m pytest tests/integration/test_structuring_pipeline.py
```

### 9.7 阶段标记

```powershell
git add apps/api
git commit -m "feat: add structured insights and citations"
git tag phase-4-structuring-and-citations
git push -u origin main
git push origin phase-4-structuring-and-citations
```

---

## 10. Phase 5：会议工作台前端

### 10.1 目标

建立用户可实际操作的会议工作台，让后端能力可见、可用、可检查。

### 10.2 开发范围

- 会议列表页。
- 会议创建入口。
- 文件上传入口。
- Job 状态展示。
- 会议详情页。
- Transcript viewer。
- Summary / Decisions / Risks / Action Items 面板。
- Citation 点击跳转。
- 加载、空状态、错误状态。

### 10.3 不做范围

- 不做复杂权限。
- 不做移动端深度优化。
- 不做复杂图表。

### 10.4 交付物

- 用户可以从浏览器创建会议并上传文件。
- 用户可以看到处理状态。
- 用户可以查看 transcript 和结构化洞察。
- 点击 citation 可以定位到对应 transcript segment。

### 10.5 验收标准

- 页面布局在桌面宽度下稳定。
- 主要按钮可通过键盘访问。
- 错误状态有清楚提示。
- 前端不直接拼接后端内部字段含义，尽量使用 typed API client。

### 10.6 建议验证命令

```powershell
cd apps/web
pnpm lint
pnpm typecheck
pnpm test
```

### 10.7 阶段标记

```powershell
git add apps/web
git commit -m "feat: add meeting workbench UI"
git tag phase-5-meeting-workbench
git push -u origin main
git push origin phase-5-meeting-workbench
```

---

## 11. Phase 6：单会议 Q&A

### 11.1 目标

支持用户围绕当前会议提问，并返回有引用依据的回答。

### 11.2 开发范围

- `Embedder` provider interface。
- transcript embedding。
- section embedding。
- insight embedding。
- pgvector 检索。
- metadata filter。
- 单会议 Q&A API。
- answer synthesis。
- 回答 citations。
- 证据不足时拒答。

### 11.3 不做范围

- 不做跨会议问答。
- 不做复杂权限搜索。
- 不做自动总结所有历史会议。

### 11.4 交付物

- 当前会议可提问。
- 回答基于检索结果生成。
- 回答包含引用。
- 引用可跳转到 transcript。

### 11.5 验收标准

- 问“谁负责某个任务”时能基于 action item 和 transcript 回答。
- 问不存在的信息时能明确表示证据不足。
- 检索结果必须限制在当前 meeting_id。
- Q&A provider 可被 mock 替换。

### 11.6 建议验证命令

```powershell
cd apps/api
python -m pytest tests/retrieval tests/qa
cd ../web
pnpm test
```

### 11.7 阶段标记

```powershell
git add apps/api apps/web
git commit -m "feat: add single meeting question answering"
git tag phase-6-single-meeting-qa
git push -u origin main
git push origin phase-6-single-meeting-qa
```

---

## 12. Phase 7：审阅与行动闭环

### 12.1 目标

让 AI 结果从 proposed 进入可管理状态，形成真正的行动闭环。

### 12.2 开发范围

- Insight 编辑。
- Insight dismiss。
- Action Item 编辑。
- Action Item confirm。
- Action Item 状态流转。
- owner_text 与 owner_user_id 兼容。
- due_text 与 due_date 兼容。
- 修改记录。
- 前端审阅界面。

### 12.3 不做范围

- 不接 Jira、Linear、飞书、Slack。
- 不做复杂多人协作冲突处理。
- 不做通知系统。

### 12.4 交付物

- 用户可以编辑 AI 生成的 action item。
- 用户可以确认、完成、取消 action item。
- 系统能区分 AI proposed 和用户 confirmed。
- 修改后 citation 保持可见。

### 12.5 验收标准

- 状态流转符合规则。
- confirmed 状态必须有用户确认记录。
- canceled 不会被 Q&A 当作待办事项。
- done 后仍保留原始 citation。

### 12.6 建议验证命令

```powershell
cd apps/api
python -m pytest tests/action_items tests/insights
cd ../web
pnpm test
```

### 12.7 阶段标记

```powershell
git add apps/api apps/web
git commit -m "feat: add review workflow and action lifecycle"
git tag phase-7-review-and-actions
git push -u origin main
git push origin phase-7-review-and-actions
```

---

## 13. Phase 8：稳定性与部署准备

### 13.1 目标

让项目从“能跑”进入“可持续使用、可排查、可部署”的状态。

### 13.2 开发范围

- Golden sample 管理。
- 集成测试样例。
- 日志规范。
- Job retry 和失败恢复。
- 处理成本统计。
- Provider latency 统计。
- Docker Compose 完整本地启动。
- 数据库备份和重建流程。
- 文件删除流程。
- 基础部署说明。

### 13.3 不做范围

- 不做复杂云原生编排。
- 不做多租户企业权限。
- 不做自动扩缩容。

### 13.4 交付物

- 本地一条命令可启动核心依赖。
- 样例会议可从上传跑到 Q&A。
- 失败 job 可重试。
- 日志能定位 provider、model、prompt_version、latency、cost estimate。

### 13.5 验收标准

- 端到端样例通过。
- 删除会议后，业务数据和文件引用一致。
- 外部 provider 失败时系统不会崩溃。
- 所有阶段文档状态更新。

### 13.6 建议验证命令

```powershell
docker compose -f infra/docker-compose.yml up -d
cd apps/api
python -m pytest
cd ../web
pnpm lint
pnpm typecheck
pnpm test
```

### 13.7 阶段标记

```powershell
git add apps web infra samples doc
git commit -m "chore: harden local workflow and deployment baseline"
git tag phase-8-hardening-and-deploy
git push -u origin main
git push origin phase-8-hardening-and-deploy
```

---

## 14. 阶段推进纪律

### 14.1 每阶段开始前

- 阅读 `RULE.md`。
- 确认上一阶段 tag 已推送。
- 确认当前阶段范围。
- 不把下一阶段功能提前塞进当前阶段。

### 14.2 每阶段开发中

- 每个 PR 或提交只解决一类问题。
- 外部 provider 必须通过 adapter 接入。
- 核心业务逻辑必须有测试。
- 数据模型变更必须有 migration。
- 前端状态必须覆盖 loading、empty、error。

### 14.3 每阶段结束前

- 更新阶段状态为 `Done`。
- 补齐验收记录。
- 删除无用代码、无用导入、临时日志。
- 运行完整验证命令。
- 创建阶段 tag。
- 推送 `main` 和 tag。

---

## 15. 近期执行建议

当前最合理的下一步是：

1. 将本目录初始化为 Git 仓库。
2. 推送当前文档基线到 GitHub。
3. 开始 Phase 0。

初始文档提交建议：

```powershell
git init -b main
git add README.md RULE.md doc/00-overview.md doc/01-product-roadmap.md doc/02-system-architecture.md doc/03-technology-stack.md doc/04-development-plan.md
git commit -m "docs: establish project architecture and development rules"
git remote add origin <github-repo-url>
git push -u origin main
```

如果远端仓库已经存在，使用已有仓库地址替换 `<github-repo-url>`。

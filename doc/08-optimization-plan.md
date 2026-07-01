# 08 - MeetMind 优化方案书

> 编写日期：2026-07-01
> 基于：Phase 0-8 代码审计 + 文档交叉对照 + 前后端逐文件审查
> 状态：待执行

---

## 一、现状评估

MeetMind 已完成 9 个开发阶段（Phase 0-8），代码质量扎实：分层架构严格（Route → Service → Repository）、Provider 适配器模式规范、零 TODO/FIXME 标记、70+ 后端测试覆盖。引用链设计和发布前质量门禁体现了"可信"这一产品核心定位。

但审计发现，项目当前处于**"本地可运行的开发原型"**阶段，与文档中描述的 v0.1 产品闭环目标存在显著差距。核心矛盾在于：**产品的关键体验链路——上传音频后自动产出结构化结果——尚未打通**，用户需要手动逐步触发 API 才能推进处理流程。

### 1.1 功能完成度总览

| 类别 | 数量 | 说明 |
|------|------|------|
| 已完成 | 13 项 | CRUD、转录管道（手动触发）、结构化提取（手动触发）、引用生成、单会议 QA、审核流程、发布门禁、章节导航、全局待办视图、Provider 状态与遥测面板、Q&A 历史恢复 |
| 部分完成 | 4 项 | 自动处理流水线（仅覆盖文本/字幕路径）、知识库搜索（子串匹配而非语义检索）、任务同步适配器（仅状态上报无推送）、章节生成（按固定 5 段分组而非主题切分） |
| 未实现 | 9 项 | 后台任务执行、真实 Provider 验证、导出功能、用户/认证模型、通知/Webhook、多会议向量检索、Dockerfile、CI/CD、持久化遥测 |

### 1.2 关键风险

1. **核心链路断裂**：音频上传后不会自动触发转录，转录完成后不会自动触发结构化，结构化完成后不会自动构建向量索引。
2. **零真实验证**：所有 Provider 仅用 mock 测试，从未配置真实 OpenAI API Key 运行。
3. **前端盲区**：MeetingWorkbench（501 行主组件 + 数十个子组件）从未在浏览器中进行人工验证。
4. **同步阻塞**：所有长时操作（转录、结构化）在 HTTP 线程同步执行，30 分钟音频将导致请求阻塞数分钟。

---

## 二、优化分阶段规划

本方案分为 **5 个阶段**，按依赖关系和风险优先级排序。每个阶段有独立主题和验收标准，完成后可独立交付价值。

---

### Phase 1：核心链路贯通

**主题**：让"上传音频 → 自动产出结果"这条产品核心体验跑通。

**预计工作量**：3-5 天

#### 1.1 串联自动处理流水线

**问题**：当前 `assets/router.py` 的 `auto_process` 参数仅覆盖"文本/字幕 → 结构化"路径。音频/视频上传后创建的 TRANSCRIBE Job 不会自动执行，各步骤之间没有链式触发。

**方案**：

- 在每个 Job 成功完成后，自动创建并触发下一阶段 Job：
  - TRANSCRIBE 成功 → 创建 STRUCTURE Job → 自动执行
  - STRUCTURE 成功 → 调用 `ensure_meeting_embeddings()` 构建向量索引
- 使用 FastAPI 的 `BackgroundTasks` 实现进程内异步执行（不引入 Celery 依赖，降低初期复杂度）
- 为 Job 执行提取独立的 `run_job(job_id)` 函数，解耦 HTTP 层与业务逻辑，供背景和手动两种调用路径复用
- 在 Meeting 状态机上正确推进状态（`transcribing → segmenting → structuring → embedding → ready_for_review`）

**验收标准**：
- 上传一段音频文件后，无需手动干预，会议状态自动推进至 `ready_for_review`
- 上传文本/字幕文件后，自动完成结构化和向量索引构建
- Job 失败时 Meeting 进入对应的 `failed_*` 状态，不影响已完成的步骤

**涉及文件**：
- `apps/api/app/jobs/service.py` — 提取 Job 执行函数
- `apps/api/app/assets/router.py` — 上传后触发链式处理
- `apps/api/app/transcription/service.py` — 转录完成回调
- `apps/api/app/structuring/service.py` — 结构化完成回调
- `apps/api/app/meetings/service.py` — 状态机推进逻辑

#### 1.2 接入真实 Provider 并完成端到端验证

**问题**：所有 Provider（ASR/LLM/Embedding）仅通过 mock 测试。`config.py` 中 Provider 默认值为 `disabled`，从未配置真实 OpenAI API Key。

**方案**：

- 准备一份真实会议音频样本（3-5 分钟，含多发言人）
- 配置 `.env` 使用真实 OpenAI API Key
- 配置 `ASR_PROVIDER=openai`、`LLM_PROVIDER=openai`、`EMBEDDING_PROVIDER=openai`
- 运行端到端流程：上传 → 转录 → 结构化 → 向量索引 → QA 提问
- 记录每个 Provider 的实际延迟、Token 消耗、错误率
- 根据实测结果调整 `config.py` 中的成本估算参数

**验收标准**：
- 真实音频从上传到 `ready_for_review` 全流程可走通
- QA 提问能基于向量检索返回带引用的回答
- Provider 遥测面板显示真实的延迟和成本数据

#### 1.3 修复阻塞性问题

**问题**：若干代码层面的问题会在真实运行时暴露。

**修复清单**：

| 问题 | 位置 | 修复方式 |
|------|------|----------|
| `embedding_dimensions` 配置与 DB 模型硬编码不一致 | `config.py:26` vs `db/models.py:418` | 统一为配置驱动或固定值 |
| `MeetingUpdate` 允许通过 PATCH 绕过状态转换校验 | `meetings/schemas.py:20` | 从 Update schema 中排除 `status` 字段 |
| `qa/router.py` 返回类型标注为 `list[object]` | `qa/router.py:41` | 改为 `list[QAMessageRead]` |
| `count_embeddings_for_meeting` 全量加载 ID 再计数 | `retrieval/repository.py:33` | 改用 `func.count()` |
| `redis_url` 配置声明但未使用 | `config.py:10` | 添加注释说明预留用途，或暂时移除 |
| Health check 不验证下游依赖 | `main.py:63` | 添加 DB 连通性检查 |

---

### Phase 2：前端验证与稳定性

**主题**：在浏览器中完整验证前端交互，修复代码质量问题，增强健壮性。

**预计工作量**：2-3 天

#### 2.1 浏览器端到端验证

**问题**：前端 38 个测试全部是单元测试/设计验证，MeetingWorkbench 从未在浏览器中进行过完整的人工操作验证。

**验证清单**：

1. 创建会议 → 上传音频 → 观察处理流程（依赖 Phase 1 完成的自动流水线）
2. 查看转录文本 → 点击章节导航 → 跳转到对应位置
3. 浏览 Insight 卡片 → 使用审核控件确认/驳回
4. 浏览 Action Item → 完整生命周期操作（确认 → 开始 → 完成）
5. 在 QA 面板提问 → 查看带引用的回答
6. 切换到知识库视图 → 搜索 → 查看决策和重复产出
7. 发布会议 → 验证发布前门禁
8. 切换会议 → 验证状态清理和数据刷新

#### 2.2 修复前端代码质量问题

| 问题 | 位置 | 修复方式 |
|------|------|----------|
| `useEffect` 闭包陷阱：视图切换时闭包捕获过期值 | `meeting-workbench.tsx:323-333` | 将 `actionStatusFilter`、`knowledgeQuery` 等加入依赖数组，或改用 `useRef` |
| 多数 Hook 无请求取消机制 | `use-meetings.ts`、`use-meeting-detail.ts` | 添加 `AbortController`，在 cleanup 函数中取消 |
| 无 React ErrorBoundary | 全局 | 在 `app/` 下创建 `error.tsx`，捕获并优雅展示运行时错误 |
| 搜索无防抖 | `meeting-search.tsx`、`knowledge-overview.tsx` | 添加 300ms 防抖 |
| 侧边栏 3 个导航项为死链 | `app-sidebar.tsx:73-81` | 移除或连接到正确的视图切换逻辑 |
| `REVIEWER_USER_ID` 硬编码 | `action-review-controls.tsx:17` | 提取为配置常量，添加注释说明 |
| 发言人名称未解析 | `transcript-segment.tsx:35` | 利用 Speaker 模型做名称映射 |
| 部分视图缺少 Loading 骨架屏 | `action-items-overview.tsx`、`knowledge-overview.tsx` | 补充加载态组件 |

#### 2.3 增强前端基础设施

**暗色模式接通**：`next-themes` 已安装，shadcn 组件已包含 `dark:` 变体，但无 `ThemeProvider`。在 `layout.tsx` 中添加 `ThemeProvider` 包裹，并在侧边栏或顶栏添加主题切换按钮。

**响应式增强**：当前移动端体验较差——侧边栏在 `<md` 时垂直堆叠占据整个视口高度。添加移动端侧边栏折叠/汉堡菜单机制。

**无障碍补强**：
- 视图切换按钮使用 `role="tablist"` / `role="tab"` 语义
- 面板状态变化添加 `aria-live` 区域
- 添加 skip-to-content 链接
- 添加 `prefers-reduced-motion` 媒体查询，避免对前庭障碍用户触发平滑滚动和动画

---

### Phase 3：工程化与部署

**主题**：让项目可容器化构建、可自动化测试、可一键部署。

**预计工作量**：3-4 天

#### 3.1 Dockerfile 与生产镜像

为 `apps/api` 和 `apps/web` 分别创建 Dockerfile：

**API Dockerfile**：
- 基础镜像：`python:3.12-slim`
- 多阶段构建：builder 阶段安装依赖，runtime 阶段仅复制已安装包
- 安装 FFmpeg（`apt-get install ffmpeg`）
- 非 root 用户运行
- 暴露 8000 端口

**Web Dockerfile**：
- 基础镜像：`node:22-alpine`
- `output: 'standalone'` 模式（需在 `next.config.ts` 中启用）
- 多阶段构建：deps → build → runtime
- 暴露 3000 端口

**docker-compose.yml 扩展**：
- 添加 `api` 和 `web` 服务定义
- 添加 `worker` 服务（若 Phase 1 选择了独立 worker 模式）
- 服务间依赖与健康检查
- 环境变量通过 `.env` 文件注入，不再硬编码

#### 3.2 CI/CD 管线

创建 `.github/workflows/ci.yml`，包含以下 Job：

**后端 Job**：
1. `ruff check` — Python lint
2. `ruff format --check` — Python 格式检查
3. `pytest` — 后端测试（需要 PostgreSQL 服务容器）

**前端 Job**：
1. `pnpm typecheck` — TypeScript 类型检查
2. `pnpm lint` — ESLint
3. `pnpm test` — Vitest
4. `pnpm build` — 构建验证

**可选 Job**：
- Docker 镜像构建验证（push 到 GHCR）
- `pytest-cov` 覆盖率报告

#### 3.3 统一开发脚本

在根 `package.json` 中补充：

```json
{
  "scripts": {
    "dev": "concurrently \"pnpm --filter @meetmind/web dev\" \"cd apps/api && uv run uvicorn app.main:app --reload\"",
    "build": "pnpm --filter @meetmind/web build",
    "test": "pnpm --filter @meetmind/web test && cd apps/api && uv run pytest",
    "lint": "pnpm --filter @meetmind/web lint && cd apps/api && uv run ruff check .",
    "typecheck": "pnpm --filter @meetmind/web typecheck",
    "db:migrate": "cd apps/api && uv run alembic upgrade head",
    "db:rollback": "cd apps/api && uv run alembic downgrade -1"
  }
}
```

添加 `concurrently` 作为根 devDependency。

#### 3.4 环境配置完善

- 补充 `FFMPEG_BINARY` 安装说明到 README
- 创建 `.env.test` 供测试隔离使用（独立数据库）
- `next.config.ts` 添加 `output: 'standalone'` 和 API 代理 rewrite 规则
- 补充 `@testing-library/react` 依赖（技术栈文档已选定但未安装）

---

### Phase 4：功能补全与质量提升

**主题**：补齐规划中但尚未实现的功能模块，提升已有功能的质量。

**预计工作量**：5-7 天

#### 4.1 Markdown 导出

**问题**：`AssetType.EXPORT` 和 `JobType.EXPORT` 已定义但无实现。

**方案**：

- 在 `structuring/` 或新建 `export/` 模块中实现导出服务
- 导出内容：会议摘要、决策列表、风险列表、待办项（含引用信息）
- 输出格式：Markdown 文件，存储为 EXPORT 类型的 MeetingAsset
- 前端在会议详情页添加"导出"按钮，点击后下载 Markdown 文件

**验收标准**：
- 发布的会议可导出为格式规范的 Markdown 文件
- 导出内容包含所有结构化产出（决策、风险、待办）及引用来源

#### 4.2 知识搜索升级为语义检索

**问题**：`knowledge/service.py` 的跨会议搜索使用子串匹配，而单会议 QA 已具备完整的向量检索能力。两者能力倒挂。

**方案**：

- 复用 `retrieval/` 已有的 pgvector 余弦距离搜索能力
- 将知识搜索从子串匹配改为基于 Embedding 的语义检索
- 支持跨会议过滤（按 workspace、时间范围、会议状态）
- 保留关键词搜索作为 fallback（当 embedding provider 不可用时降级）

**验收标准**：
- 输入自然语言问题，能跨会议检索到语义相关的转录段落、Insight 和 Action Item
- 搜索结果按相关度排序，包含来源会议链接

#### 4.3 QA 回答合成器增强

**问题**：`ExtractiveAnswerSynthesizer` 仅取第一条证据用硬编码模板拼接，不支持跨证据综合。

**方案**：

- 改进 extractive 实现：取 top-K 证据，按相关度组织回答
- 新增 LLM 生成式回答 Provider（`LLMAnswerSynthesizer`）：将证据上下文和原始问题发送给 LLM，生成综合回答
- 通过 `QA_ANSWER_PROVIDER` 环境变量切换

**验收标准**：
- QA 回答能综合多条证据
- 回答中每个关键断言附带引用标记

#### 4.4 分页支持

**问题**：所有列表端点无分页，数据增长后会有性能问题。

**方案**：

- 后端：为所有 list 端点添加 `offset` + `limit` 参数，返回 `{ items, total, has_more }` 结构
- 前端：会议列表添加无限滚动，其他列表添加分页控件或"加载更多"按钮
- 涉及端点：`list_meetings`、`list_processing_jobs`、`list_transcript_segments`、`list_global_action_items`、`search_knowledge`、`list_qa_messages`

#### 4.5 章节生成优化

**问题**：`_build_basic_sections` 按固定每 5 段分组，标题取首段前 48 字符，不具备语义意义。

**方案**：

- 利用已有的 LLM Provider，在结构化提取阶段让 LLM 识别章节边界
- LLM 输出章节标题和时间范围
- 保留固定分组作为 fallback（当 LLM provider 不可用时）

---

### Phase 5：生产加固

**主题**：为多用户和生产环境部署做准备。

**预计工作量**：5-7 天

#### 5.1 认证与授权（最小可用）

**方案**：

- 新建 `User` 模型（id, email, display_name, role）
- 实现 JWT 认证中间件
- 添加登录/注册端点
- 为所有现有端点注入 `current_user` 依赖
- Meeting 和 ActionItem 添加 `workspace_id` 过滤
- 移除 `REVIEWER_USER_ID = "local-user"` 硬编码

**验收标准**：
- 用户需登录才能访问 API
- 用户只能访问自己 workspace 的数据
- Action Item 审核操作记录真实的用户 ID

#### 5.2 可观测性升级

**持久化遥测**：将 Provider 遥测从内存 dict 迁移到数据库表或日志文件，进程重启后不丢失。

**结构化日志**：
- 引入 `structlog` 替代 stdlib logging
- 添加 Request ID 中间件，贯穿整个请求生命周期
- 所有 Service 层错误记录结构化日志（含 request_id、meeting_id、job_id）

**深度健康检查**：`/health` 端点验证 DB 连通性，可选验证 Redis 和 S3 可达性。

#### 5.3 安全加固

- CORS 配置按环境区分：开发环境允许 localhost，生产环境严格限制 `allow_origins`
- 添加安全响应头中间件：`X-Content-Type-Options`、`X-Frame-Options`、`Content-Security-Policy`
- 添加请求速率限制（`slowapi` 或 Redis-based limiter）
- `docker-compose.yml` 中的数据库密码改为 `.env` 注入
- 文件上传大小限制显式配置

#### 5.4 后台任务队列（Celery）

**问题**：Phase 1 使用 FastAPI BackgroundTasks 解决了紧急需求，但生产环境需要更可靠的方案。

**方案**：

- 安装 Celery + Redis 依赖
- 将 Job 执行迁移到 Celery worker
- 实现任务重试策略（指数退避）
- 添加 Celery Flower 监控面板（可选）

**验收标准**：
- 长时操作（转录、结构化）在独立 worker 进程中执行，不阻塞 HTTP
- Worker 崩溃后任务可自动重试
- Job 进度可实时查询

---

## 三、执行依赖关系

```
Phase 1（核心链路）
  ├── 1.1 自动流水线 ──┐
  ├── 1.2 真实验证    ──┤──→ Phase 2（前端验证，依赖 1.1 的自动流水线）
  └── 1.3 阻塞修复    ──┘           │
                                    ↓
                            Phase 3（工程化，与 Phase 2 可并行）
                                    │
                                    ↓
                            Phase 4（功能补全，依赖 Phase 1-2 的稳定基础）
                                    │
                                    ↓
                            Phase 5（生产加固，依赖 Phase 3-4 的功能完整性）
```

Phase 2 和 Phase 3 可以并行执行。Phase 4 和 Phase 5 内的各子任务之间相对独立，可按需调整优先级。

---

## 四、验收总标准

所有阶段完成后，MeetMind 应达到以下状态：

1. **核心体验闭环**：用户上传一段会议录音，系统自动完成转录、结构化提取、向量索引构建，用户在浏览器中直接查看结果、审核产出、提问并获得带引用的回答。
2. **工程化就绪**：`docker-compose up` 一条命令启动完整应用（API + Web + Worker + 基础设施），CI 管线在每次 push 时自动运行测试和构建。
3. **质量可观测**：Provider 调用延迟、成本、失败率持久化记录并可通过面板查看，请求链路可通过 Request ID 追踪。
4. **功能完整度**：导出、语义搜索、分页、增强 QA 等规划功能已实现，文档与代码同步。
5. **安全基线**：用户认证、workspace 隔离、CORS 收紧、安全响应头已就位。

---

## 五、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 真实 Provider 延迟/成本超出预期 | Phase 1.2 验收受阻 | 先用短音频（< 1 分钟）验证，逐步加长；准备降级方案（local embedder + 简单结构化） |
| BackgroundTasks 在生产负载下不够可靠 | Phase 1 临时方案有局限 | Phase 1 明确标注为过渡方案，Phase 5.4 的 Celery 迁移是最终方案 |
| 前端验证暴露大量 UI 问题 | Phase 2 工作量膨胀 | 先做核心路径验证，非核心问题记录为 backlog 后续处理 |
| 分页改动涉及所有端点 | Phase 4.4 改动面大 | 优先对数据量最大的端点（transcript_segments、meetings）加分页，其余按需 |

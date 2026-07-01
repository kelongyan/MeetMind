<div align="center">

<!-- ═══════════════════════════════════════════ -->

# 🧠 MeetMind

### 可信会议智能工作台

<p><i>把会议音频、视频、转写文本和人工记录整理成<br><b>可验证 · 可检索 · 可追踪</b> 的团队知识资产</i></p>

<!-- Badges -->
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](/)
[![Frontend](https://img.shields.io/badge/frontend-Next.js_16-000000?style=flat-square&logo=nextdotjs&logoColor=white)](/)
[![Python](https://img.shields.io/badge/python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](/)
[![TypeScript](https://img.shields.io/badge/typescript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white)](/)
[![Tests](https://img.shields.io/badge/tests-108_passing-brightgreen?style=flat-square&logo=checkmarx&logoColor=white)](/)
[![License](https://img.shields.io/badge/status-product--ready-6366F1?style=flat-square&logoColor=white)](/)

</div>

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## ✨ 项目简介

> MeetMind 面向会议后的真实协作场景 —— 它不只是生成一段会议摘要，而是帮助团队<b>保留会议事实、结构化关键结论、追踪后续行动</b>，并在需要时回到原始证据。

### 💎 核心价值

|  |  |  |
|:---:|:---:|:---:|
| 🎯 **快速整理** transcript、决策、风险、开放问题和行动项 | 📎 **证据链** 为关键结论保留原始发言引用，降低 AI 幻觉和误读风险 | 👁️ **人工审阅** AI 结果先审阅，再进入正式状态 |
| 💬 **会议问答** 支持会议内问答，保留带引用的回答历史 | 🔍 **跨会议追踪** 行动项追踪和知识搜索 | 📊 **运维可见** provider 状态、调用质量和成本估算 |

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## 🚀 功能特性

<div align="center">

### ━━━ 🧭 会议工作台 ━━━

</div>

- 创建会议并上传音频、视频、转写文本或字幕文件
- 查看带时间戳的 transcript
- 使用章节导航定位长会议内容
- 查看处理任务状态并执行 retry
- 在质量校验通过后发布会议

<div align="center">

### ━━━ 📝 洞察与行动项 ━━━

</div>

- 提取讨论点、决策、风险和开放问题
- 提取行动项（负责人、截止时间、状态、置信度）
- 支持确认、驳回、开始、完成或取消行动项
- 跨会议查看行动项，按状态筛选
- 从行动项跳回来源会议

<div align="center">

### ━━━ 🔗 引用与问答 ━━━

</div>

- 为结构化结果和问答答案保存 citation
- 点击 citation 回到 transcript 对应片段
- 围绕单场会议提问并保存 Q&A 历史
- 证据不足时拒绝编造答案

<div align="center">

### ━━━ 📚 知识库 ━━━

</div>

- 按 workspace 搜索 transcript、insight 和 action item
- 查看历史决策
- 提示可能重复的行动项
- 跨会议结果保留来源会议和上下文线索

<div align="center">

### ━━━ 📊 运维视图 ━━━

</div>

- 查看 ASR、LLM、Embedding、Q&A provider 配置状态
- 查看调用次数、失败次数、平均耗时和成本估算
- 预留任务同步 adapter 边界
- 不在界面展示 API key、token 或 webhook URL

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## 🧩 产品原则

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   📂 Source First     原始会议资料是事实来源            │
│   📐 Structured First  关键输出以结构化数据保存         │
│   📎 Evidence First    决策、行动项和回答尽量带证据     │
│   🤝 Human-in-the-loop  AI 结果先审阅，再发布           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## 🛠️ 技术栈

| 模块 | 技术 |
|:---|:---|
| 🎨 **前端** | Next.js 16 · React 19 · TypeScript · Tailwind CSS |
| ⚙️ **后端** | FastAPI · SQLAlchemy · Alembic · Pydantic |
| 🗄️ **数据库** | PostgreSQL · pgvector |
| ⚡ **队列与缓存** | Redis |
| 📦 **对象存储** | MinIO / S3-compatible |
| 🤖 **AI 能力** | ASR · LLM · Embedding · Q&A provider adapter |
| ✅ **测试与质量** | pytest · ruff · Vitest · TypeScript · ESLint |
| 📋 **包管理** | pnpm |

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## 📁 仓库结构

```text
MeetMind/
├── apps/
│   ├── api/          ⚙️  FastAPI 后端服务
│   └── web/          🎨  Next.js 前端应用
├── infra/            🗄️  Docker Compose 和数据库初始化脚本
├── doc/              📖  项目资料、架构资料和阶段记录
├── samples/          🧪  样例会议数据
├── storage/          💾  本地运行时存储目录
└── package.json      📋  工作区脚本
```

### 后端模块

```text
apps/api/app/
├── action_items/    📋  全局行动项接口
├── assets/          📤  上传、资源记录和文件处理
├── db/              🗃️  SQLAlchemy 模型和数据库会话
├── insights/        💡  洞察、行动项、引用和审阅状态
├── jobs/            🔄  处理任务和 retry 血统
├── knowledge/       🔍  工作区搜索、历史决策、重复行动项提示
├── meetings/        🎯  会议生命周期和发布校验
├── observability/   📊  provider telemetry
├── operations/      🔧  provider 状态、调用汇总、任务同步状态
├── providers/       🤖  ASR、LLM、Embedding、Q&A adapter
├── qa/              💬  会议问答
├── retrieval/       🔎  embedding 和证据检索
├── structuring/     📐  LLM 结构化提取
└── transcription/   🎙️  音频、文本和字幕转写处理
```

### 前端模块

```text
apps/web/features/meetings/
├── api.ts                         🌐  API client
├── types.ts                       📝  前端类型定义
├── meeting-workbench.tsx          🖥️  主工作台
└── components/
    ├── action-items/              📋  行动项总览
    ├── knowledge/                 📚  知识库视图
    ├── meeting-detail/            🎯  会议详情
    ├── operations/                📊  运维视图
    ├── qa/                        💬  会议问答
    └── transcript/                📄  transcript 和章节导航
```

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## ⚙️ 环境要求

- 🪟 Windows PowerShell
- 🐳 Docker Desktop
- 🟢 Node.js + pnpm
- 🐍 Python 3.12+
- 📦 后端虚拟环境：`apps/api/.venv`

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## 🔐 配置

复制环境变量示例：

```powershell
Copy-Item .env.example .env
```

关键配置：

```env
# ─── 基础设施 ───
DATABASE_URL=postgresql+psycopg://meetmind:meetmind@localhost:5432/meetmind
REDIS_URL=redis://localhost:6379/0
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET_NAME=meetmind-local

# ─── AI Providers ───
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

# ─── 任务同步 ───
TASK_SYNC_PROVIDER=disabled
TASK_SYNC_WEBHOOK_URL=
```

> 💡 默认情况下，ASR 和 LLM provider 关闭；本地 embedding 和 extractive Q&A 可用于开发验证。

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## 💻 本地开发

**安装依赖：**

```powershell
pnpm install
```

**启动基础设施：**

```powershell
pnpm infra:up
```

**执行数据库迁移：**

```powershell
cd apps/api
.\.venv\Scripts\python -m alembic upgrade head
```

**启动后端：**

```powershell
cd apps/api
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

> 🌐 后端默认地址：`http://localhost:8000`

**启动前端：**

```powershell
pnpm --filter @meetmind/web dev
```

> 🌐 前端默认地址：`http://localhost:3927`

**停止基础设施：**

```powershell
pnpm infra:down
```

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## ⌨️ 常用命令

<details>
<summary><b>📦 根目录命令</b></summary>

```powershell
pnpm infra:up      # 启动基础设施
pnpm infra:down    # 停止基础设施
pnpm lint          # 前端 lint
pnpm typecheck     # 前端类型检查
pnpm test          # 前端测试
```

</details>

<details>
<summary><b>⚙️ 后端命令</b></summary>

```powershell
cd apps/api
.\.venv\Scripts\python -m pytest                                    # 运行全部测试
.\.venv\Scripts\python -m pytest tests/test_meeting_api.py          # 单个文件
.\.venv\Scripts\python -m pytest tests/test_meeting_api.py::test_x  # 单个测试
.\.venv\Scripts\python -m ruff check .                              # Lint
.\.venv\Scripts\python -m ruff format .                             # Format
.\.venv\Scripts\python -m alembic upgrade head                      # 数据库迁移
.\.venv\Scripts\python -m uvicorn app.main:app --reload             # 启动后端
```

</details>

<details>
<summary><b>🎨 前端命令</b></summary>

```powershell
pnpm --filter @meetmind/web dev        # 启动开发服务器
pnpm --filter @meetmind/web test       # 运行测试
pnpm --filter @meetmind/web lint       # Lint
pnpm --filter @meetmind/web typecheck  # 类型检查
pnpm --filter @meetmind/web build      # 生产构建
```

</details>

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## ✅ 测试

**推荐验证流程：**

```powershell
# 后端
cd apps/api
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .

# 前端
cd ..\..
pnpm --filter @meetmind/web test
pnpm --filter @meetmind/web lint
pnpm --filter @meetmind/web typecheck
pnpm --filter @meetmind/web build
```

<div align="center">

| 🎯 Backend | 🎨 Frontend |
|:---:|:---:|
| ✅ 70 tests passing | ✅ 38 tests passing |

</div>

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## 📈 运维说明

- 📊 Provider telemetry 使用 `meetmind.provider` logger
- 📝 记录 provider、model、prompt version、latency、estimated units、cost estimate 和失败信息
- 👁️ 运维视图展示 provider readiness 和调用汇总
- 🔌 任务同步当前只暴露 adapter readiness，第三方系统深度集成默认未启用
- 💾 Docker Compose 数据默认保存在 `storage/docker` 下

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## 🛡️ 安全说明

- 🚫 不提交 `.env`、API key、凭证、私密录音、本地数据库或运行日志
- 🔒 运维界面不得展示原始 API key、token 或 webhook URL
- 📋 Provider telemetry 只记录元数据，不记录完整会议正文或敏感 prompt
- 📎 AI 输出应尽量绑定来源证据

---

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## 📌 当前状态

> ✅ MeetMind 当前已经具备本地产品可用形态，覆盖会议处理、审阅、行动项追踪、知识搜索和运维可见性。

### 🚧 已知边界

- 真实 ASR 和 LLM 质量取决于 provider 配置和真实会议样例
- 企业级权限、SSO、审计和多租户治理尚未完整实现
- Jira、Linear、飞书、Slack 等外部任务系统尚未深度接入
- 生产级部署加固仍属于后续工作

---

<!-- ═══════════════════════════════════════════ -->

<div align="center">

<sub>Built with ❤️ by the MeetMind team</sub>

</div>

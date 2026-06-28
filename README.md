# MeetMind

MeetMind 是一个面向会议场景的可信会议智能系统，目标是把会议音频、视频、转写文本和人工记录转化为可验证、可检索、可执行的结构化工作资产。

它不是只生成一段会议摘要的工具。MeetMind 更关注会议内容后续能不能被团队真正使用：每个关键结论能否回到原始发言，每个行动项是否有负责人和状态，每次问答是否有证据支撑，会议知识是否能在后续项目推进中继续复用。

---

## 核心定位

会议结束后，团队真正需要的不只是“看起来完整的纪要”，而是：

- 能确认谁在什么时候说了什么；
- 能知道哪些事项已经决策，哪些只是讨论；
- 能把行动项从一句话变成可跟踪的任务对象；
- 能快速回到原始发言，验证 AI 总结是否可靠；
- 能围绕会议内容继续提问，并得到带引用的回答；
- 能把单次会议沉淀为后续可搜索、可复用的知识。

MeetMind 的核心目标是完成这个闭环：

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

## 核心能力

### 1. 会议资料摄取

支持会议音频、视频、转写文本、字幕文件等输入。系统会保存原始资产信息，创建异步处理任务，并为后续转写、结构化理解和检索做准备。

### 2. 语音转写

通过 ASR provider 将音频转换为带时间戳的 transcript segments。后续可以接入 `faster-whisper`、OpenAI speech-to-text、WhisperX 或其他语音识别服务。

### 3. 结构化会议理解

使用 LLM 将会议内容提取为结构化对象，包括：

- Meeting Summary
- Discussion Points
- Decisions
- Risks
- Open Questions
- Action Items

核心结果不直接依赖 Markdown，而是通过 JSON Schema / Pydantic 校验后进入系统。

### 4. 引用追溯

每个关键结论都需要绑定原始 transcript segment。用户点击 action item、decision 或 Q&A 回答时，可以回到对应原始发言。

### 5. 行动项生命周期

Action Item 不是静态文本，而是有状态的任务对象：

```text
proposed -> confirmed -> in_progress -> done / canceled
```

AI 只负责提出候选结果，用户负责确认和修正。

### 6. 单会议问答

用户可以围绕当前会议提问。系统通过检索 transcript、section 和 insight，生成带引用的回答；证据不足时必须明确拒答。

---

## 架构方向

当前阶段采用 **模块化单体 + 异步任务队列**。

```text
Frontend
  Next.js / React / TypeScript

Backend API
  FastAPI / Pydantic / SQLAlchemy

Domain Services
  Meeting / Asset / Job / Transcription / Structuring / Citation / Retrieval / QA

Infrastructure
  PostgreSQL / pgvector / Redis / Object Storage / FFmpeg / AI Providers
```

设计原则：

- Source First：转写片段是事实源头。
- Structured First：核心 AI 输出必须结构化。
- Evidence First：关键结论必须有引用证据。
- Human-in-the-loop：AI 结果默认是 proposed，需要用户确认。
- Model-agnostic：ASR、LLM、Embedding 都通过 adapter 接入。
- Privacy by Design：会议内容默认敏感，架构上保留删除、审计、模型路由和权限空间。

---

## 技术栈规划

前端：

- Next.js
- React
- TypeScript
- TailwindCSS
- shadcn/ui
- TanStack Query

后端：

- FastAPI
- Pydantic
- SQLAlchemy 或 SQLModel
- Alembic
- PostgreSQL
- pgvector
- Redis Queue / RQ / Celery

AI 与媒体：

- FFmpeg
- faster-whisper 或云端 speech-to-text
- WhisperX / pyannote 作为后续发言人识别候选
- LLM provider adapter
- Embedding provider adapter

---

## 开发阶段

项目按阶段推进，每个阶段都必须可验收、可提交、可打 tag、可推送。

| 阶段 | 名称 | 当前状态 | 核心结果 |
| --- | --- | --- | --- |
| Phase 0 | 工程基线 | Not Started | 项目结构、依赖管理、配置、数据库、测试框架 |
| Phase 1 | 后端核心领域 | Not Started | Meeting、Asset、Job、Transcript、Insight、Citation 数据模型 |
| Phase 2 | 上传与异步任务 | Not Started | 文件上传、媒体元数据、任务队列、处理状态 |
| Phase 3 | 语音转写链路 | Not Started | 音频标准化、ASR adapter、Transcript 入库与展示接口 |
| Phase 4 | 结构化理解与引用 | Not Started | LLM JSON 输出、Action Items、Decisions、Risks、Citations |
| Phase 5 | 会议工作台前端 | Not Started | 上传页、会议列表、会议详情、Transcript 与洞察联动 |
| Phase 6 | 单会议 Q&A | Not Started | Embedding、检索、基于引用的回答 |
| Phase 7 | 审阅与行动闭环 | Not Started | AI 结果编辑、确认、Action Item 状态流转 |
| Phase 8 | 稳定性与部署准备 | Not Started | 测试样例、日志、错误恢复、Docker、本地部署说明 |

---

## 当前仓库状态

当前仓库处于架构与开发规划阶段，尚未进入应用代码实现。

已完成：

- 项目总体架构方案
- 分阶段开发方案
- 工程规则与协作规范
- GitHub 仓库初始化

下一步：

1. 开始 Phase 0，搭建前后端基础工程。
2. 建立 Docker Compose、本地数据库和 Redis。
3. 建立后端测试框架和前端基础检查命令。
4. 推送 `phase-0-foundation` 阶段 tag。

---

## 文档入口

- [项目总体架构方案](./meetmind-meeting-intelligence.md)
- [分阶段开发方案](./doc/phased-development-plan.md)
- [开发规则](./RULE.md)

---

## 阶段推进规则

每完成一个阶段，必须：

1. 更新 `doc/phased-development-plan.md` 中的阶段状态。
2. 运行该阶段要求的验证命令。
3. 创建清晰的 Git commit。
4. 创建阶段 tag。
5. 推送 `main` 分支和阶段 tag 到 GitHub。

示例：

```powershell
git add <changed-files>
git commit -m "feat: complete phase 0 foundation"
git tag phase-0-foundation
git push -u origin main
git push origin phase-0-foundation
```

---

## 最小成功标准

v0.1 只有达到下面标准，才算真正跑通：

- 上传一段真实会议音频后，系统能完成异步处理。
- 用户能看到带时间戳的 transcript。
- 系统能生成结构化 summary、decisions、risks、action items。
- 每个 action item 和 decision 至少有一个 citation。
- 点击 citation 能跳到 transcript 对应位置。
- 用户能修改并确认 action item。
- 用户能向当前会议提问，并得到带引用的回答。
- 当证据不足时，Q&A 会拒绝编造。

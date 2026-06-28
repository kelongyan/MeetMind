# MeetMind - 可信会议智能与行动闭环系统

> 当前版本：2026-06-28  
> 当前目标：先把产品定位、系统架构、核心数据流和后续开发路径想清楚。暂不做对外包装，暂不追求大而全。

---

## 0. 现阶段趋势判断

### 0.1 会议 AI 已经从“新功能”变成“办公基础能力”

截至 2026 年，主流办公平台已经把 AI 会议能力内置到自己的产品里：

- Microsoft Teams Intelligent Recap 已支持 AI notes、recommended tasks、speaker markers、topic chapters 等能力。
- Google Meet 的 Gemini note taking 已经覆盖实时记录、action items、Google Docs/Calendar 联动。
- Zoom AI Companion 已支持基于 speech-to-text 的 meeting summary，并能通过邮件或聊天分享。

这说明一个现实问题：**单纯做“会议总结”已经不够有差异化**。如果 MeetMind 只是“上传音频，然后生成一段纪要”，它会很快变成大厂功能的弱化版。

### 0.2 真正的机会在“可信、可追溯、可执行”

会议智能下一阶段不是把会议变成一篇漂亮文章，而是把会议变成可使用的工作资产：

- **可信**：每条总结、决策、行动项都能回到原始发言。
- **可追溯**：知道“谁在什么时候说了什么”，而不是只有 AI 的二手转述。
- **可执行**：Action Items 有负责人、截止时间、状态、证据和变更记录。
- **可检索**：一次会议不是孤岛，后续可以在会议知识库里找历史决策和上下文。
- **可治理**：会议内容敏感，必须有权限、保留策略、删除策略和模型路由策略。

### 0.3 Agentic AI 对项目架构的启发

Microsoft 2026 Work Trend Index 提到，很多员工已经准备好使用 AI，但组织层面的流程、治理和支持还没跟上。这对 MeetMind 的启发是：

MeetMind 不应该只做一个“帮我总结”的助手，而应该做一个 **Meeting Intelligence Layer**：

- 先理解会议内容；
- 再抽取结构化事实；
- 再把事实连接到任务、知识库和后续工作流；
- 最后允许人审阅、修正和确认。

也就是说，系统核心不是聊天框，而是 **会议证据、结构化知识和行动闭环**。

---

## 1. 项目定位

### 1.1 一句话定位

**MeetMind 是一个将会议音视频、转写文本和人工记录转化为可信知识与可执行任务的会议智能系统。**

### 1.2 我们不做什么

当前阶段先明确边界，避免一上来就做成“大杂烩”：

- 不优先做实时会议机器人。
- 不优先做日历、邮箱、飞书、Slack、Jira 等完整集成。
- 不承诺 100% 准确的发言人识别。
- 不把 LLM 输出当作事实本身。
- 不让 AI 自动执行外部任务，先做人审确认。

### 1.3 我们重点做什么

第一阶段重点做一个闭环：

```text
上传会议资料
  -> 生成带时间戳的转写
  -> 结构化提取总结、决策、风险、行动项
  -> 每个关键结论绑定原始发言证据
  -> 用户审阅、修正、确认
  -> 支持基于会议内容的问答
```

这个闭环跑通以后，再扩展到多会议知识库、团队协作、外部系统集成和实时能力。

---

## 2. 核心问题

### 2.1 会议后的真实痛点

会议结束后，团队常见问题不是“没有纪要”，而是：

- 纪要只记录结论，不知道结论从哪里来。
- Action Items 写得模糊，没有负责人、截止时间或上下文。
- 决策散落在聊天、录音、文档里，后面没人找得到。
- 参会者对同一件事理解不一致。
- AI 总结看起来流畅，但无法判断有没有漏掉、编造或误解。
- 长会议回看成本太高，想找某一句话很痛苦。

### 2.2 MeetMind 要解决的核心问题

MeetMind 的核心问题定义为：

> 如何把一场会议转化为“可验证、可检索、可执行”的结构化工作资产？

这句话里有三个关键词：

- **可验证**：所有关键输出都要有证据链。
- **可检索**：会议内容要能被搜索、问答和复用。
- **可执行**：行动项不是文案，而是有生命周期的任务对象。

---

## 3. 产品原则

### 3.1 Source First

转写片段是事实源头。总结、决策、风险、行动项都只是从事实源头派生出来的结构化视图。

### 3.2 Structured First

LLM 输出必须尽量结构化。核心内容不直接依赖 Markdown，而是通过 JSON Schema / Pydantic 模型进入系统，再由前端渲染。

### 3.3 Human-in-the-loop

AI 负责初步理解和提取，人负责确认。任何任务、决策、风险进入“已确认”状态前，都应该允许用户审阅和修改。

### 3.4 Evidence-backed AI

没有证据的结论不应被展示为事实。对于 Action Items、Decisions、Risks 这类关键对象，必须绑定 transcript segment 或时间戳引用。

### 3.5 Async First

MVP 以会后异步处理为主。实时转写和实时问答是后续增强，不作为第一阶段主路径。

### 3.6 Model-agnostic

系统不绑定单一模型供应商。ASR、LLM、Embedding 都通过 adapter 隔离，方便在本地模型、OpenAI、Qwen、Claude 等方案之间切换。

### 3.7 Privacy by Design

会议内容默认敏感。架构上要预留权限、数据保留、删除、模型路由、审计日志和脱敏能力。

---

## 4. 用户与场景

### 4.1 核心用户

- **会议组织者**：希望快速产出可信纪要和行动项。
- **项目负责人**：关心决策、风险、任务推进和跨会议上下文。
- **普通参会者**：想快速回看自己错过的内容、确认自己负责什么。
- **团队管理员**：关心数据权限、历史会议沉淀和知识复用。

### 4.2 优先支持的会议类型

- 项目周会
- 产品需求评审
- 技术方案评审
- 客户访谈
- 事故复盘
- 头脑风暴后的行动整理

### 4.3 第一阶段最重要的用户路径

```text
用户上传会议音频或转写文本
  -> 系统显示处理进度
  -> 用户进入会议详情页
  -> 左侧查看 transcript
  -> 右侧查看 AI 提取的 summary / decisions / risks / action items
  -> 点击任意结论跳转到对应原始发言
  -> 用户修正并确认行动项
  -> 用户在 Q&A 中追问会议内容
```

---

## 5. 系统总体架构

### 5.1 架构选择

当前阶段建议采用 **模块化单体 + 异步任务队列**。

原因：

- 项目初期业务边界还在变化，微服务会增加部署和调试成本。
- 音频处理和 LLM 处理天然耗时，必须异步化。
- 模块化单体可以先把领域边界设计清楚，后续需要时再拆服务。

### 5.2 总体架构图

```text
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│              Next.js / React / TailwindCSS                   │
│  Upload / Job Status / Meeting Detail / Transcript / Q&A     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         Backend API                          │
│                           FastAPI                            │
│  Meeting API / Asset API / Job API / Insight API / Q&A API   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Domain Services                         │
│                                                             │
│  Media Service          - 文件校验、转码、切片               │
│  Transcription Service  - ASR 转写、时间戳、可选说话人       │
│  Segmentation Service   - 语义分段、主题识别                 │
│  Structuring Service    - 总结、决策、风险、行动项提取       │
│  Citation Service       - 结论到原文片段的证据映射           │
│  Retrieval Service      - Embedding、搜索、RAG 问答          │
│  Task Service           - Action Item 生命周期               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
│                                                             │
│  PostgreSQL + pgvector    - 业务数据与向量检索               │
│  Object Storage           - 原始音视频、转码文件、导出文件   │
│  Redis + Queue            - 异步任务、重试、状态             │
│  LLM / ASR Providers      - OpenAI / Qwen / Claude / Local   │
│  Observability            - 日志、指标、错误追踪             │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 为什么不是一开始做实时系统

实时系统需要同时处理音频流、WebSocket、低延迟 ASR、增量上下文、会中权限和 UI 状态同步。它很酷，但不是最小闭环。

MeetMind 的第一阶段应该先把“会后理解质量”做好：

- 转写准不准；
- 结构化结果稳不稳；
- 引用是否能对上；
- 用户能不能审阅和修正；
- 问答是否基于证据。

这些做好以后，再做实时能力才不会变成空中楼阁。

---

## 6. 数据处理流水线

### 6.1 主流程

```text
1. Upload
   接收音频、视频、转写文本或字幕文件。

2. Normalize
   使用 FFmpeg 转码、抽音轨、统一采样率，必要时切片。

3. Transcribe
   调用 ASR 服务生成 transcript segments。

4. Segment
   基于时间、话题变化和语义相似度划分会议段落。

5. Structure
   使用 LLM 按 JSON Schema 生成 summary、decisions、risks、action items。

6. Cite
   为每个关键 insight 绑定 transcript segment IDs 和时间戳。

7. Embed
   为 transcript segments、sections、insights 生成向量索引。

8. Review
   用户审阅 AI 结果，修正 owner、due date、内容和引用。

9. Ask
   用户基于当前会议或未来的会议知识库进行问答。
```

### 6.2 处理状态

每场会议应该有明确的处理状态，方便前端展示和失败恢复：

```text
uploaded
  -> media_processing
  -> transcribing
  -> segmenting
  -> structuring
  -> citing
  -> embedding
  -> ready_for_review
  -> published
```

失败状态：

```text
failed_media_processing
failed_transcription
failed_structuring
failed_embedding
```

每个失败状态都要记录：

- failure_code
- failure_message
- retryable
- failed_at
- provider
- input_asset_id

---

## 7. 核心模块设计

### 7.1 文件摄取模块

职责：

- 接收 `mp3`、`wav`、`mp4`、`m4a`、`webm`、`txt`、`srt`、`vtt`。
- 计算文件 hash，避免重复上传和重复处理。
- 保存原始文件元数据。
- 创建 processing job。

关键设计：

- 原始文件和派生文件分开存储。
- 上传成功不等于处理成功。
- 大文件必须异步处理。
- 后续要支持删除原始音视频，仅保留 transcript 和结构化结果。

### 7.2 音频处理模块

职责：

- 从视频中抽取音频。
- 转成统一格式，例如 mono wav / 16kHz。
- 对长音频做切片。
- 记录切片与原始时间轴的偏移关系。

关键设计：

- 切片不能破坏时间戳。
- 每个 chunk 都要保存 `offset_start_ms`。
- 后续合并 transcript 时要把局部时间还原成全局时间。

### 7.3 语音转写模块

职责：

- 将音频转换为带时间戳的 transcript segments。
- 支持中英文会议。
- 支持后续插拔不同 ASR provider。

建议 provider 策略：

- MVP：优先支持 `faster-whisper` 或云端 ASR 中的一种，先跑通。
- 增强：增加 OpenAI speech-to-text adapter。
- 增强：增加 WhisperX / pyannote / diarized transcription adapter。

输出结构示例：

```json
{
  "segments": [
    {
      "id": "seg_001",
      "speaker_id": "speaker_unknown",
      "start_ms": 1200,
      "end_ms": 5600,
      "text": "我们今天先确认一下数据库优化的进度。",
      "confidence": 0.91
    }
  ]
}
```

### 7.4 发言人识别模块

当前阶段策略：

- Phase 1：允许全部标记为 `speaker_unknown`，或者按 ASR 输出的粗粒度 speaker。
- Phase 2：接入 WhisperX / pyannote / 云端 diarization。
- Phase 3：支持用户手动把 `Speaker A` 改成真实姓名，并回写到全局 speaker map。

原因：

- 发言人分离在真实会议里不稳定，尤其是多人重叠、远场麦克风、噪音环境。
- 如果第一版强依赖 diarization，会拖慢核心闭环。
- Action Items 和 citations 的价值不完全依赖真实姓名，先保证时间戳和原文证据更重要。

### 7.5 语义分段模块

职责：

- 把连续 transcript 划分为有主题的 sections。
- 每个 section 绑定一组 transcript segments。
- 为后续 summary、Q&A 和导航提供结构。

section 示例：

```json
{
  "id": "sec_001",
  "meeting_id": "mtg_001",
  "title": "数据库性能优化进展",
  "start_ms": 1000,
  "end_ms": 182000,
  "segment_ids": ["seg_001", "seg_002", "seg_003"],
  "topic_tags": ["backend", "database", "performance"]
}
```

第一阶段可以用简单规则：

- 每 3-5 分钟作为基础窗口；
- 根据关键词和 embedding 相似度合并相邻窗口；
- 再让 LLM 为 section 生成标题。

### 7.6 AI 结构化理解模块

职责：

- 从 transcript / sections 中提取结构化会议结果。
- 输出必须能被程序验证。
- 每个关键对象必须包含引用信息。

核心输出：

- meeting_brief
- discussion_points
- decisions
- risks
- action_items
- open_questions

示例结构：

```json
{
  "meeting_brief": {
    "goal": "确认项目进度与数据库优化方案",
    "summary": "本次会议主要讨论后端接口进展、数据库查询性能和前端 dashboard 排期。"
  },
  "decisions": [
    {
      "id": "decision_001",
      "title": "优先优化数据库查询性能",
      "rationale": "当前查询性能影响接口响应时间，是后续 dashboard 展示的前置条件。",
      "citation_segment_ids": ["seg_004", "seg_005"],
      "confidence": 0.86
    }
  ],
  "action_items": [
    {
      "id": "action_001",
      "description": "优化数据库查询并提交性能对比结果",
      "owner_text": "后端负责人",
      "due_text": "Friday",
      "status": "proposed",
      "citation_segment_ids": ["seg_006"],
      "confidence": 0.82
    }
  ]
}
```

关键规则：

- LLM 不直接创建数据库最终状态，只产生 proposed insight。
- 后端验证 JSON Schema，不合法则重试或标记失败。
- 缺少 citation 的关键对象不得进入 ready 状态。
- `confidence` 只是辅助排序，不代表事实正确。

### 7.7 引用与证据链模块

职责：

- 把 AI 输出的每个关键 insight 映射回 transcript。
- 支持点击 insight 跳转到对应原始发言。
- 支持一个 insight 绑定多个引用片段。

citation 结构：

```json
{
  "id": "cite_001",
  "target_type": "action_item",
  "target_id": "action_001",
  "segment_id": "seg_006",
  "start_ms": 203000,
  "end_ms": 218000,
  "quote": "数据库查询性能需要优化，这周五前给一个对比结果。",
  "confidence": 0.88
}
```

实现策略：

- 第一阶段：要求 LLM 输出 `segment_ids`，后端校验 segment 是否存在。
- 第二阶段：用 embedding / lexical matching 二次验证引用是否真的支持结论。
- 第三阶段：加入 citation verifier，对“引用不支持结论”的结果打回重试。

### 7.8 会议问答模块

职责：

- 用户可以对单场会议提问。
- 回答必须基于 transcript / insights / sections。
- 回答要附引用，不足以回答时明确说证据不足。

第一阶段 Q&A 范围：

- 当前会议内问答。
- 支持按 speaker、时间范围、section、insight 类型过滤。

后续扩展：

- 多会议知识库问答。
- 跨会议决策追踪。
- “这个问题上次怎么决定的？”这类历史上下文查询。

回答规则：

```text
如果检索结果不足，不编造答案。
如果答案来自多个片段，合并时保留多个引用。
如果用户问未来计划，只能基于已记录 action items / decisions 回答。
```

### 7.9 Action Item 生命周期模块

Action Item 不应只是一行文字，而是一个有状态对象。

状态设计：

```text
proposed
  -> confirmed
  -> in_progress
  -> done
  -> canceled
```

字段设计：

- description
- owner_text
- owner_user_id
- due_text
- due_date
- source_meeting_id
- citation_ids
- status
- created_by_ai
- confirmed_by_user_id
- confirmed_at
- updated_at

第一阶段不需要接 Jira / Linear / 飞书任务，但数据模型要为这些集成留好位置。

### 7.10 前端体验模块

MVP 页面建议：

```text
/meetings
  会议列表、上传入口、处理状态

/meetings/:id
  左侧 transcript
  右侧 summary / decisions / risks / action items
  底部或右侧 Q&A

/meetings/:id/review
  AI 结果审阅、编辑、确认、发布
```

会议详情页核心交互：

- 点击 transcript segment，高亮对应时间段。
- 点击 action item / decision，滚动到引用片段。
- 用户可以编辑 AI 提取结果。
- 用户可以把 proposed action item 确认为正式任务。
- Q&A 回答展示引用来源。

---

## 8. 核心数据模型

### 8.1 meetings

```text
id
workspace_id
title
description
language
status
started_at
ended_at
duration_ms
created_by
created_at
updated_at
```

### 8.2 meeting_assets

```text
id
meeting_id
asset_type           # audio / video / transcript / subtitle / export
storage_uri
original_filename
mime_type
size_bytes
sha256
duration_ms
created_at
deleted_at
```

### 8.3 processing_jobs

```text
id
meeting_id
job_type             # transcribe / structure / embed / export
status
progress
provider
input_asset_id
failure_code
failure_message
started_at
finished_at
created_at
```

### 8.4 transcript_segments

```text
id
meeting_id
speaker_id
start_ms
end_ms
text
confidence
source_asset_id
chunk_index
created_at
```

### 8.5 speakers

```text
id
meeting_id
display_name         # Speaker A / Alice / Unknown
canonical_user_id
confidence
created_at
updated_at
```

### 8.6 meeting_sections

```text
id
meeting_id
title
summary
start_ms
end_ms
topic_tags
created_at
```

### 8.7 insight_items

统一存储 summary 之外的结构化洞察：

```text
id
meeting_id
section_id
type                 # discussion_point / decision / risk / open_question
title
body
status               # proposed / confirmed / dismissed
confidence
model_name
model_version
prompt_version
created_at
updated_at
```

### 8.8 action_items

```text
id
meeting_id
section_id
description
owner_text
owner_user_id
due_text
due_date
status               # proposed / confirmed / in_progress / done / canceled
confidence
created_by_ai
confirmed_by_user_id
confirmed_at
created_at
updated_at
```

### 8.9 citations

```text
id
meeting_id
target_type          # insight_item / action_item / answer
target_id
segment_id
start_ms
end_ms
quote
confidence
created_at
```

### 8.10 embeddings

```text
id
meeting_id
source_type          # transcript_segment / meeting_section / insight_item
source_id
embedding_model
vector
metadata
created_at
```

### 8.11 qa_messages

```text
id
meeting_id
conversation_id
role                 # user / assistant
content
citation_ids
model_name
created_at
```

---

## 9. API 设计草案

### 9.1 Meeting API

```text
POST /api/meetings
GET  /api/meetings
GET  /api/meetings/{meeting_id}
PATCH /api/meetings/{meeting_id}
DELETE /api/meetings/{meeting_id}
```

### 9.2 Asset API

```text
POST /api/meetings/{meeting_id}/assets
GET  /api/meetings/{meeting_id}/assets
DELETE /api/assets/{asset_id}
```

### 9.3 Processing API

```text
POST /api/meetings/{meeting_id}/process
GET  /api/jobs/{job_id}
POST /api/jobs/{job_id}/retry
```

### 9.4 Transcript API

```text
GET /api/meetings/{meeting_id}/transcript
GET /api/meetings/{meeting_id}/sections
```

### 9.5 Insight API

```text
GET   /api/meetings/{meeting_id}/insights
PATCH /api/insights/{insight_id}
PATCH /api/action-items/{action_item_id}
POST  /api/action-items/{action_item_id}/confirm
POST  /api/action-items/{action_item_id}/complete
```

### 9.6 Q&A API

```text
POST /api/meetings/{meeting_id}/qa
GET  /api/meetings/{meeting_id}/qa/{conversation_id}
```

Q&A 请求示例：

```json
{
  "question": "这次会议决定了哪些数据库优化事项？",
  "filters": {
    "speaker_ids": [],
    "section_ids": [],
    "time_range": null
  }
}
```

Q&A 响应示例：

```json
{
  "answer": "会议中确认优先优化数据库查询性能，并要求在周五前提交性能对比结果。",
  "citations": [
    {
      "segment_id": "seg_006",
      "start_ms": 203000,
      "end_ms": 218000,
      "quote": "数据库查询性能需要优化，这周五前给一个对比结果。"
    }
  ]
}
```

---

## 10. 技术栈建议

### 10.1 前端

- Next.js
- React
- TypeScript
- TailwindCSS
- shadcn/ui 或同类组件库
- TanStack Query

### 10.2 后端

- FastAPI
- Pydantic
- SQLAlchemy 或 SQLModel
- Alembic
- Redis Queue / RQ / Celery

### 10.3 数据层

建议直接使用：

- PostgreSQL
- pgvector
- 本地文件系统或 MinIO/S3 兼容对象存储

不建议 MVP 长期依赖 SQLite，原因是：

- 后续要做向量检索；
- Job、asset、transcript、citation 数据关系较多；
- PostgreSQL 更接近真实部署环境。

### 10.4 AI 与音频

- FFmpeg：音视频处理。
- faster-whisper：本地 ASR 候选。
- WhisperX / pyannote：后续 diarization 候选。
- OpenAI speech-to-text：云端 ASR 候选。
- OpenAI / Qwen / Claude：结构化理解候选。
- Embedding model：先通过 adapter 隔离，后续可切换。

### 10.5 推荐的 adapter 抽象

```text
Transcriber
  transcribe(audio_asset) -> TranscriptResult

Diarizer
  diarize(audio_asset, transcript) -> SpeakerTimeline

LLMExtractor
  extract_meeting_insights(transcript, schema) -> StructuredInsights

Embedder
  embed(texts) -> vectors

Retriever
  search(query, filters) -> ranked_chunks
```

---

## 11. LLM 设计策略

### 11.1 结构化输出

LLM 输出必须通过 JSON Schema 约束，后端使用 Pydantic 校验。校验失败时：

1. 记录原始输出；
2. 触发一次修复重试；
3. 仍失败则标记 `failed_structuring`；
4. 前端提示用户可以稍后重试。

### 11.2 分阶段 Prompt

不要让一个 prompt 做完所有事情。建议拆成：

```text
Prompt 1: 会议主题与结构识别
Prompt 2: 决策、风险、开放问题提取
Prompt 3: Action Items 提取
Prompt 4: 引用校验或补全
Prompt 5: 面向用户的简洁 summary 生成
```

这样做的好处：

- 输出更稳定；
- 出错时更容易定位；
- 可以单独评估 action items 或 citations；
- 后续可替换某个步骤的模型。

### 11.3 Chunking 策略

长会议不能直接塞给模型。建议：

```text
transcript segments
  -> time/topic chunks
  -> chunk-level extraction
  -> meeting-level aggregation
  -> citation verification
```

聚合时必须保留：

- 原始 segment_id；
- section_id；
- chunk_id；
- 时间范围；
- speaker 信息。

### 11.4 反幻觉规则

系统级规则：

- 不允许凭空补 owner。
- 不允许凭空补 due date。
- 不允许把讨论中的可能方案写成已决策。
- 不允许回答没有证据的问题。
- 不允许隐藏不确定性。

当信息不足时，输出：

```text
未在会议记录中找到足够证据。
```

---

## 12. RAG 与会议知识库

### 12.1 MVP：单会议 RAG

第一阶段只做单场会议内问答：

- transcript segment embedding；
- section embedding；
- insight embedding；
- 根据 `meeting_id` 强过滤；
- 回答必须返回 citations。

### 12.2 后续：多会议知识库

第二阶段再扩展到 workspace 级：

- 按项目、标签、参与人、时间范围搜索；
- 查询历史决策；
- 对比不同会议中同一主题的变化；
- 自动发现重复 action items；
- 生成项目级 timeline。

### 12.3 检索策略

优先级：

```text
用户问题
  -> query rewrite
  -> metadata filter
  -> hybrid search: keyword + vector
  -> rerank
  -> answer synthesis
  -> citation check
```

---

## 13. 隐私、安全与治理

### 13.1 数据敏感性

会议内容可能包含：

- 客户信息；
- 商业决策；
- 账号、合同、报价；
- 内部路线图；
- 个人信息。

所以系统必须从一开始保留治理空间。

### 13.2 第一阶段必须具备的能力

- 用户可以删除会议。
- 用户可以删除原始音视频。
- 原始文件与结构化结果分离。
- 每次 AI 处理记录 provider、model、时间和状态。
- 前端明确展示 AI 结果是 proposed，未经确认不等于事实。

### 13.3 后续增强能力

- 工作区权限。
- 数据保留策略。
- PII 自动检测与脱敏。
- 本地模型优先处理敏感会议。
- 审计日志。
- 导出前水印或权限提醒。

### 13.4 模型路由策略

后续可以支持三种模式：

```text
local_only
  所有 ASR / LLM / Embedding 都走本地或私有部署。

hybrid
  普通会议走云端模型，敏感会议走本地模型。

cloud_first
  追求速度和效果，优先走云端模型。
```

---

## 14. 可靠性与异常处理

### 14.1 Job 可恢复

每个处理步骤都应该幂等：

- 已完成的步骤不重复跑；
- 失败步骤可以单独 retry；
- retry 不应产生重复 transcript / insights；
- 每次重新生成 insight 要记录版本。

### 14.2 长会议处理

长会议风险：

- 文件大；
- 转写慢；
- token 超限；
- 结构化结果重复或遗漏；
- 引用容易错位。

应对策略：

- 音频切片；
- transcript 分 chunk；
- chunk-level extraction；
- meeting-level merge；
- insight 去重；
- citation verification。

### 14.3 Partial Result

如果 ASR 成功但 LLM 失败，用户仍然应该能查看 transcript。

如果 structure 成功但 embedding 失败，用户仍然应该能查看 summary/action items，只是 Q&A 暂不可用。

---

## 15. 质量评估指标

### 15.1 ASR 指标

- Word Error Rate / Character Error Rate。
- 时间戳偏移误差。
- 长音频处理成功率。

### 15.2 结构化提取指标

- Action Item precision。
- Action Item recall。
- Decision precision。
- Risk precision。
- Owner / due date extraction accuracy。

### 15.3 引用质量指标

- Citation support rate：引用是否真的支持结论。
- Citation click success：点击后是否跳到正确片段。
- Unsupported insight rate：没有证据支撑的 insight 占比。

### 15.4 Q&A 指标

- Answer groundedness。
- Retrieval hit rate。
- Refusal correctness：证据不足时是否拒答。
- Citation usefulness。

### 15.5 产品指标

- 从上传到 ready_for_review 的耗时。
- 用户确认 action item 的比例。
- 用户手动修改 AI 输出的比例。
- 用户点击 citation 的比例。
- 单场会议处理成本。

---

## 16. 开发路线图

### 16.1 MVP v0.1：单会议可信闭环

目标：跑通“上传 -> 转写 -> 结构化 -> 引用 -> 审阅 -> 问答”。

范围：

- 会议创建与文件上传。
- 异步处理 job。
- 音频转写。
- transcript 展示。
- summary / decisions / risks / action items 提取。
- citations 点击跳转。
- 单会议 Q&A。
- action item 确认与状态更新。

不做：

- 实时会议。
- 多工作区权限。
- 外部任务系统集成。
- 完整发言人身份识别。
- 多会议知识库。

### 16.2 MVP 建议开发顺序

```text
Step 1: 后端基础
  FastAPI 项目结构、数据库、migration、配置系统。

Step 2: 会议与文件
  meetings / assets / jobs 数据模型和 API。

Step 3: 音频处理
  FFmpeg normalize、音频时长、切片策略。

Step 4: ASR
  Transcriber adapter、transcript_segments 入库。

Step 5: 前端 transcript
  上传、job 状态、会议详情、transcript viewer。

Step 6: 结构化提取
  LLMExtractor、JSON Schema、insights/action_items 入库。

Step 7: 引用系统
  citation 表、点击 insight 跳转 transcript。

Step 8: 单会议 Q&A
  embedding、检索、answer synthesis、citation 展示。

Step 9: 审阅与确认
  编辑 insight、确认 action item、状态流转。

Step 10: 质量与稳定性
  golden sample、日志、失败重试、成本统计。
```

### 16.3 v0.2：发言人与体验增强

- Speaker diarization。
- 用户手动绑定 speaker 真实姓名。
- 更好的 section 导航。
- 会议导出 Markdown / PDF。
- Prompt 版本管理。
- Citation verifier。

### 16.4 v0.3：会议知识库

- workspace 级搜索。
- 多会议 Q&A。
- 历史决策追踪。
- 项目 timeline。
- 相似会议 / 相似议题推荐。

### 16.5 v0.4：协作与集成

- 用户与权限。
- Action Items 分配给用户。
- Slack / 飞书 / Jira / Linear / Notion 集成。
- 周报生成。
- 会议后自动发送 digest。

### 16.6 v1.0：实时能力

- WebSocket 实时转写。
- 实时摘要。
- 会中提问。
- 实时 action item detection。
- 会中提醒和决策确认。

---

## 17. 当前优先级判断

### 17.1 最高优先级

- 稳定上传和处理。
- 可靠 transcript。
- 结构化 action items。
- citations。
- 用户审阅和确认。

这些是系统骨架，不能跳过。

### 17.2 中优先级

- 发言人识别。
- Q&A。
- section 导航。
- 导出。
- Prompt 版本管理。

这些能明显增强体验，但不应该拖慢第一条主链路。

### 17.3 低优先级

- 实时会议。
- 多平台机器人。
- 复杂权限系统。
- 自动创建外部任务。
- 会议效率分析大屏。

这些后续可以做，但现在先别被它们带偏。

---

## 18. 关键技术风险与应对

### 18.1 ASR 不准

风险：

- 噪音、口音、多人重叠会影响转写质量。

应对：

- 支持用户编辑 transcript。
- 保存 ASR confidence。
- 对低 confidence 片段做 UI 标记。
- 后续支持更换 provider。

### 18.2 发言人识别不稳定

风险：

- diarization 错误会导致 owner 误判。

应对：

- Phase 1 不强依赖真实 speaker。
- Action owner 用 `owner_text` 和人工确认。
- 后续支持用户手动修正 speaker map。

### 18.3 LLM 幻觉

风险：

- 模型可能把讨论中的可能性写成已确认决策。

应对：

- 强制 structured output。
- 强制 citation。
- proposed 状态必须经用户确认。
- 对 decision/action item 做引用校验。

### 18.4 长会议成本高

风险：

- 长音频转写慢，LLM token 成本高。

应对：

- 分片转写。
- 分 chunk 提取。
- 只对必要片段做深度 LLM。
- 支持本地模型和云模型切换。

### 18.5 大厂功能竞争

风险：

- Teams / Google / Zoom 自带会议总结。

应对：

- MeetMind 不拼“谁也能总结”。
- 差异化放在跨平台、证据链、结构化任务、可治理知识库。

---

## 19. 开发验证策略

### 19.1 Golden Samples

准备 3-5 份固定样例：

- 5 分钟短会议。
- 20 分钟项目周会。
- 带明确 action items 的需求评审。
- 有多个争议点的技术讨论。
- 噪音较多或发言人混杂的会议。

每次改 ASR、prompt、chunking、citation 逻辑，都用这些样例做回归。

### 19.2 测试层级

- Unit tests：数据模型、schema validation、citation 校验、状态流转。
- Integration tests：上传、job、ASR mock、LLM mock、insight 入库。
- E2E tests：上传样例文件，等待 ready，检查 transcript 和 action items。
- Manual review：人工检查 citations 是否真正支持结论。

### 19.3 必须记录的调试信息

- provider
- model
- prompt_version
- input token / output token
- latency
- cost estimate
- raw model output
- schema validation error
- retry count

---

## 20. 项目结构建议

后续实际开发时，可以按下面方式组织：

```text
meetmind/
  apps/
    web/                     # Next.js frontend
    api/                     # FastAPI backend
  packages/
    shared/                  # shared types / schemas if needed
  infra/
    docker-compose.yml
    postgres/
  samples/
    meetings/                # golden samples metadata, not sensitive audio
```

后端内部建议：

```text
apps/api/
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
```

---

## 21. 近期决策清单

开发前需要尽快确认这些问题：

1. ASR 第一版用本地 `faster-whisper`，还是先用云端 speech-to-text 加快开发？
2. 第一版是否直接上 PostgreSQL + pgvector？
3. 前端是否使用 Next.js + TailwindCSS + shadcn/ui？
4. Q&A 是否进入 v0.1，还是放到 v0.2？
5. 是否需要第一版就支持用户登录？
6. 原始音视频默认保留多久？
7. 是否允许把会议内容发给云端模型？

当前推荐：

- ASR：先选一个最快能跑通的 provider，但必须通过 adapter 包起来。
- 数据库：直接 PostgreSQL + pgvector。
- Q&A：保留在 v0.1，但只做单会议范围。
- 登录：本地开发阶段可先不做完整权限，接口保留 `workspace_id` 和 `created_by`。
- 原始文件：默认保留，提供删除入口。
- 云端模型：开发期允许，架构上保留 local/hybrid/cloud 三种模式。

---

## 22. 最小成功标准

v0.1 只有达到下面标准，才算真的跑通：

- 上传一段真实会议音频后，系统能完成异步处理。
- 用户能看到带时间戳的 transcript。
- 系统能生成结构化 summary、decisions、risks、action items。
- 每个 action item 和 decision 至少有一个 citation。
- 点击 citation 能跳到 transcript 对应位置。
- 用户能修改并确认 action item。
- 用户能向当前会议提问，并得到带引用的回答。
- 当证据不足时，Q&A 会拒绝编造。

---

## 23. 参考资料

- [Microsoft 2026 Work Trend Index: Agents, human agency, and opportunity](https://www.microsoft.com/en-us/worklab/work-trend-index/agents-human-agency-and-the-opportunity-for-every-organization)
- [Microsoft Teams Intelligent Recap](https://learn.microsoft.com/en-us/microsoftteams/intelligent-recap-calls-meetings)
- [Google Workspace: AI note taking and Take notes for me](https://workspace.google.com/solutions/ai/ai-note-taking/)
- [Zoom AI Companion Meeting Summary](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0058013)
- [OpenAI Speech to Text Guide](https://developers.openai.com/api/docs/guides/speech-to-text)
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI File Search and Vector Stores](https://developers.openai.com/api/docs/guides/tools-file-search)

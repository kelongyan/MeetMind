# MeetMind 系统架构方案

> 版本：2026-06-28  
> 目标：定义 MeetMind 的系统边界、数据流、核心模块、数据模型、API 草案、可靠性和治理要求。  
> 适用范围：后端领域建模、前后端协作、AI pipeline、RAG、引用追溯和行动闭环。

---

## 1. 架构选择

当前阶段采用 **模块化单体 + 异步任务队列**。

原因：

- 业务边界仍在快速变化，微服务会过早增加部署和调试成本；
- 音频处理、ASR、LLM、embedding 都是长耗时任务，必须异步化；
- 模块化单体可以先把领域边界设计清楚，后续需要时再拆独立服务。

---

## 2. 总体架构

```text
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│              Next.js / React / TypeScript                    │
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
│  Redis + Celery           - 异步任务、重试、状态             │
│  LLM / ASR Providers      - OpenAI / Qwen / Claude / Local   │
│  Observability            - 日志、指标、错误追踪             │
└─────────────────────────────────────────────────────────────┘
```

详细技术选型见 `doc/03-technology-stack.md`。

---

## 3. 数据处理流水线

### 3.1 主流程

```text
1. Upload
   接收音频、视频、转写文本或字幕文件。

2. Normalize
   使用 FFmpeg 转码、抽音轨、统一采样率，必要时切片。

3. Transcribe
   调用 ASR provider 生成 transcript segments。

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

### 3.2 处理状态

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

每个失败状态必须记录：

- failure_code；
- failure_message；
- retryable；
- failed_at；
- provider；
- input_asset_id。

---

## 4. 核心模块

### 4.1 文件摄取模块

职责：

- 接收 `mp3`、`wav`、`mp4`、`m4a`、`webm`、`txt`、`srt`、`vtt`；
- 计算文件 hash，避免重复上传和重复处理；
- 保存原始文件元数据；
- 创建 processing job。

关键设计：

- 原始文件和派生文件分开存储；
- 上传成功不等于处理成功；
- 大文件必须异步处理；
- 后续要支持删除原始音视频，仅保留 transcript 和结构化结果。

### 4.2 音频处理模块

职责：

- 从视频中抽取音频；
- 转成统一格式，例如 mono wav / 16kHz；
- 对长音频做切片；
- 记录切片与原始时间轴的偏移关系。

关键设计：

- 切片不能破坏时间戳；
- 每个 chunk 都要保存 `offset_start_ms`；
- 合并 transcript 时要把局部时间还原成全局时间。

### 4.3 语音转写模块

职责：

- 将音频转换为带时间戳的 transcript segments；
- 支持中英文会议；
- 支持后续插拔不同 ASR provider。

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

### 4.4 发言人识别模块

当前策略：

- v0.1：允许全部标记为 `speaker_unknown`；
- v0.2：接入 WhisperX / pyannote / 云端 diarization；
- v0.3：支持用户手动把 `Speaker A` 改成真实姓名，并回写 speaker map。

发言人分离在多人重叠、远场麦克风、噪音环境下不稳定，第一版不应强依赖它。

### 4.5 语义分段模块

职责：

- 把连续 transcript 划分为有主题的 sections；
- 每个 section 绑定一组 transcript segments；
- 为 summary、Q&A 和导航提供结构。

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

### 4.6 AI 结构化理解模块

职责：

- 从 transcript / sections 中提取结构化会议结果；
- 输出必须能被程序验证；
- 每个关键对象必须包含引用信息。

核心输出：

- meeting_brief；
- discussion_points；
- decisions；
- risks；
- action_items；
- open_questions。

关键规则：

- LLM 不直接创建数据库最终状态，只产生 proposed insight；
- 后端验证 JSON Schema，不合法则重试或标记失败；
- 缺少 citation 的关键对象不得进入 ready 状态；
- confidence 只用于辅助排序，不代表事实正确。

### 4.7 引用与证据链模块

职责：

- 把 AI 输出的关键 insight 映射回 transcript；
- 支持点击 insight 跳转到原始发言；
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

### 4.8 会议问答模块

职责：

- 用户可以对单场会议提问；
- 回答必须基于 transcript / insights / sections；
- 回答要附引用；
- 证据不足时明确拒答。

回答规则：

```text
如果检索结果不足，不编造答案。
如果答案来自多个片段，合并时保留多个引用。
如果用户问未来计划，只能基于已记录 action items / decisions 回答。
```

### 4.9 Action Item 生命周期模块

状态设计：

```text
proposed
  -> confirmed
  -> in_progress
  -> done
  -> canceled
```

核心字段：

- description；
- owner_text；
- owner_user_id；
- due_text；
- due_date；
- source_meeting_id；
- citation_ids；
- status；
- created_by_ai；
- confirmed_by_user_id；
- confirmed_at；
- updated_at。

---

## 5. 前端工作台

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

- 点击 transcript segment，高亮对应时间段；
- 点击 action item / decision，滚动到引用片段；
- 用户可以编辑 AI 提取结果；
- 用户可以把 proposed action item 确认为正式任务；
- Q&A 回答展示引用来源。

---

## 6. 核心数据模型

### 6.1 meetings

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

### 6.2 meeting_assets

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

### 6.3 processing_jobs

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
retryable
failed_at
started_at
finished_at
created_at
```

### 6.4 transcript_segments

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

### 6.5 speakers

```text
id
meeting_id
display_name         # Speaker A / Alice / Unknown
canonical_user_id
confidence
created_at
updated_at
```

### 6.6 meeting_sections

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

### 6.7 insight_items

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

### 6.8 action_items

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
model_name
model_version
prompt_version
created_by_ai
confirmed_by_user_id
confirmed_at
created_at
updated_at
```

### 6.9 citations

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

### 6.10 embeddings

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

### 6.11 qa_messages

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

## 7. API 草案

### 7.1 Meeting API

```text
POST   /api/meetings
GET    /api/meetings
GET    /api/meetings/{meeting_id}
PATCH  /api/meetings/{meeting_id}
DELETE /api/meetings/{meeting_id}
```

### 7.2 Asset API

```text
POST   /api/meetings/{meeting_id}/assets
GET    /api/meetings/{meeting_id}/assets
DELETE /api/assets/{asset_id}
```

### 7.3 Processing API

```text
POST /api/meetings/{meeting_id}/process
GET  /api/jobs/{job_id}
PATCH /api/jobs/{job_id}
POST /api/jobs/{job_id}/retry
POST /api/jobs/{job_id}/run
POST /api/jobs/{job_id}/structure
```

### 7.4 Transcript API

```text
POST /api/meetings/{meeting_id}/transcript
GET /api/meetings/{meeting_id}/transcript
GET /api/meetings/{meeting_id}/sections
```

### 7.5 Insight API

```text
POST  /api/meetings/{meeting_id}/insights
GET   /api/meetings/{meeting_id}/insights
POST  /api/meetings/{meeting_id}/action-items
GET   /api/meetings/{meeting_id}/action-items
POST  /api/meetings/{meeting_id}/citations
GET   /api/meetings/{meeting_id}/citations
PATCH /api/insights/{insight_id}
PATCH /api/action-items/{action_item_id}
POST  /api/action-items/{action_item_id}/confirm
POST  /api/action-items/{action_item_id}/complete
```

### 7.6 Q&A API

```text
POST /api/meetings/{meeting_id}/qa
GET  /api/meetings/{meeting_id}/qa/{conversation_id}
```

---

## 8. LLM 策略

### 8.1 结构化输出

LLM 输出必须通过 JSON Schema 约束，后端使用 Pydantic 校验。校验失败时：

1. 记录原始输出；
2. 触发一次修复重试；
3. 仍失败则标记 `failed_structuring`；
4. 前端提示用户可以稍后重试。

### 8.2 分阶段 Prompt

建议拆成：

```text
Prompt 1: 会议主题与结构识别
Prompt 2: 决策、风险、开放问题提取
Prompt 3: Action Items 提取
Prompt 4: 引用校验或补全
Prompt 5: 面向用户的简洁 summary 生成
```

### 8.3 Chunking 策略

```text
transcript segments
  -> time/topic chunks
  -> chunk-level extraction
  -> meeting-level aggregation
  -> citation verification
```

聚合时必须保留：

- segment_id；
- section_id；
- chunk_id；
- 时间范围；
- speaker 信息。

### 8.4 反幻觉规则

系统级规则：

- 不允许凭空补 owner；
- 不允许凭空补 due date；
- 不允许把讨论中的可能方案写成已决策；
- 不允许回答没有证据的问题；
- 不允许隐藏不确定性。

当信息不足时，输出：

```text
未在会议记录中找到足够证据。
```

---

## 9. RAG 与会议知识库

### 9.1 v0.1：单会议 RAG

- transcript segment embedding；
- section embedding；
- insight embedding；
- 根据 `meeting_id` 强过滤；
- 回答必须返回 citations。

### 9.2 后续：多会议知识库

- 按项目、标签、参与人、时间范围搜索；
- 查询历史决策；
- 对比不同会议中同一主题的变化；
- 自动发现重复 action items；
- 生成项目级 timeline。

### 9.3 检索策略

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

## 10. 隐私、安全与治理

### 10.1 第一阶段必须具备

- 用户可以删除会议；
- 用户可以删除原始音视频；
- 原始文件与结构化结果分离；
- 每次 AI 处理记录 provider、model、时间和状态；
- 前端明确展示 AI 结果是 proposed，未经确认不等于事实。

### 10.2 后续增强

- 工作区权限；
- 数据保留策略；
- PII 自动检测与脱敏；
- 本地模型优先处理敏感会议；
- 审计日志；
- 导出前水印或权限提醒。

### 10.3 模型路由

```text
local_only
  所有 ASR / LLM / Embedding 都走本地或私有部署。

hybrid
  普通会议走云端模型，敏感会议走本地模型。

cloud_first
  追求速度和效果，优先走云端模型。
```

---

## 11. 可靠性与异常处理

### 11.1 Job 可恢复

每个处理步骤都应该幂等：

- 已完成的步骤不重复跑；
- 失败步骤可以单独 retry；
- retry 不应产生重复 transcript / insights；
- 每次重新生成 insight 要记录版本。

### 11.2 长会议处理

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

### 11.3 Partial Result

如果 ASR 成功但 LLM 失败，用户仍然应该能查看 transcript。

如果 structure 成功但 embedding 失败，用户仍然应该能查看 summary/action items，只是 Q&A 暂不可用。

---

## 12. 质量评估指标

### 12.1 ASR 指标

- Word Error Rate / Character Error Rate；
- 时间戳偏移误差；
- 长音频处理成功率。

### 12.2 结构化提取指标

- Action Item precision；
- Action Item recall；
- Decision precision；
- Risk precision；
- Owner / due date extraction accuracy。

### 12.3 引用质量指标

- Citation support rate；
- Citation click success；
- Unsupported insight rate。

### 12.4 Q&A 指标

- Answer groundedness；
- Retrieval hit rate；
- Refusal correctness；
- Citation usefulness。

### 12.5 产品指标

- 从上传到 ready_for_review 的耗时；
- 用户确认 action item 的比例；
- 用户手动修改 AI 输出的比例；
- 用户点击 citation 的比例；
- 单场会议处理成本。

---

## 13. 项目结构建议

```text
MeetMind/
  apps/
    web/
    api/
  packages/
    shared/
  infra/
    docker-compose.yml
  samples/
    meetings/
  doc/
    00-overview.md
    01-product-roadmap.md
    02-system-architecture.md
    03-technology-stack.md
    04-development-plan.md
  README.md
  RULE.md
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

# MeetMind 产品闭环补充方案书

> 版本：2026-06-30  
> 目标：在 Phase 0-8 已完成的工程基础上，补齐从“开发验证闭环”到“用户可自然使用闭环”的产品逻辑。  
> 适用范围：v0.1 收尾、v0.2 单会议增强、v0.3 知识库前置能力。  
> 核心判断：当前代码已具备单会议核心能力，但上传、处理、审阅、发布、问答沉淀和行动追踪之间仍需要补充产品级串联。

---

## 1. 当前判断

MeetMind 当前已经完成核心工程骨架和主要后端能力：

- 会议、资源、任务、转写、洞察、行动项、引用、embedding、Q&A 等核心模型已建立。
- 上传后可创建处理任务，文本/字幕可导入 transcript，音视频可触发转写。
- 结构化链路支持 JSON Schema / Pydantic 校验，并要求关键结果带 citation。
- Q&A 可按会议范围检索 evidence，并生成带 citation 的回答。
- 前端已有会议工作台，覆盖会议列表、上传、详情、Transcript、洞察、行动项、Q&A 和处理任务面板。

但当前更接近“开发验证闭环”，还不是完整“产品使用闭环”：

- 上传后不会自动完成全链路处理，用户需要手动运行 job。
- ASR / LLM 默认禁用，真实会议音频还未完成端到端质量验证。
- embedding 主要在 Q&A 首次提问时按需生成，缺少独立索引阶段体验。
- `published` 状态存在，但缺少正式发布动作和发布前校验。
- Action Item 仍停留在单会议详情内，缺少跨会议追踪视图。
- Q&A 结果会入库，但前端未完整恢复历史会话。
- Meeting Section 数据模型存在，但还没有成为长会议导航和结构化处理主轴。

---

## 2. 补充路线总览

后续补充不建议重新开大架构，而是在现有模块化单体上补齐产品逻辑。

```text
Stage A: v0.1 产品闭环收尾
  -> 自动处理流水线
  -> 真实 provider 验证
  -> Q&A 历史恢复
  -> 发布动作和发布前校验

Stage B: v0.2 单会议体验增强
  -> Section 导航
  -> Action Items 总视图
  -> 处理进度和失败恢复增强
  -> 导出基础结果

Stage C: v0.3 知识库前置能力
  -> Workspace 级搜索
  -> 多会议 Q&A 前置索引
  -> 历史决策与行动项追踪
  -> 基础权限和审计预留

Stage D: v0.4 协作与集成准备
  -> 用户、负责人、工作区
  -> 通知和外部任务系统适配
  -> Provider 配置界面
  -> 成本和质量观测面板
```

优先级判断：

```text
先补“单会议从上传到发布的自然闭环”
再补“行动项跨会议追踪”
最后补“多会议知识库和协作集成”
```

---

## 3. Stage A：v0.1 产品闭环收尾

### 3.1 目标

让普通用户可以不理解 job/API 的情况下完成一场会议的完整处理：

```text
创建会议
  -> 上传音频或转写文本
  -> 系统自动处理
  -> 用户查看 transcript 和结构化结果
  -> 用户审阅行动项和关键洞察
  -> 用户提问并看到带引用答案
  -> 用户发布会议结果
```

### 3.2 开发范围

- 自动处理流水线：
  - 上传音视频后自动排队并执行 `transcribe`。
  - 转写成功后自动创建并执行 `structure`。
  - 结构化成功后自动执行或按 job 记录 `embed`。
  - 任一步失败后保留 partial result。
- Job runner：
  - 先实现应用内本地 runner 或轻量 worker 编排。
  - 保持未来迁移到 Celery worker 的边界。
  - 每个 job 必须幂等。
- 真实 provider 验证：
  - 配置 OpenAI ASR / LLM / Embedding。
  - 使用一段真实会议音频跑通。
  - 记录耗时、失败、成本估算和质量问题。
- Q&A 历史恢复：
  - 前端进入会议时加载已有 `qa_messages`。
  - 支持继续当前会话。
  - 回答 citation 仍可跳转 transcript。
- 发布动作：
  - 增加明确的“发布会议”入口。
  - 发布前检查 transcript、关键 action item / decision citation、未处理失败 job。
  - 发布成功后状态进入 `published`。

### 3.3 不做范围

- 不做多租户权限系统。
- 不接 Jira、Linear、飞书、Slack。
- 不做实时会议机器人。
- 不做复杂云原生 worker 池。
- 不做跨会议问答。

### 3.4 交付物

- 上传后能自动推进到 `ready_for_review`。
- 真实音频样例能跑到 transcript、结构化结果、Q&A。
- 用户能在前端看到历史 Q&A。
- 用户能发布会议，并看到 `published` 状态。
- 失败 job 能明确展示失败原因并支持 retry。

### 3.5 验收标准

- 上传一段真实音频后，无需手动点击 job run，系统能自动完成转写和结构化。
- 文本 transcript 上传后，无需手动点击 structure，系统能自动生成洞察和行动项。
- 任一 provider 失败时，meeting 状态进入对应失败状态，已生成的 transcript 仍可查看。
- Q&A 刷新页面后历史问答仍存在。
- 发布前若关键 action item 或 decision 缺少 citation，发布被拒绝并给出明确提示。
- 发布后的会议仍支持 Q&A 和 citation 跳转。

### 3.6 建议验证命令

```powershell
pnpm infra:up
cd apps/api
.\.venv\Scripts\python -m alembic upgrade head
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .
cd ..\..\apps\web
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

### 3.7 手动验证清单

- 创建会议并上传真实音频。
- 观察前端处理状态自动变化。
- 等待会议进入 `ready_for_review`。
- 点击 action item citation，确认 transcript 正确滚动和高亮。
- 编辑并确认一个 action item。
- 提问一个会议内可回答问题，确认回答带 citation。
- 提问一个会议中不存在的问题，确认系统拒绝编造。
- 发布会议，确认状态变为 `published`。

---

## 4. Stage B：v0.2 单会议体验增强

### 4.1 目标

让单会议体验从“能跑通”变成“好用、可复查、可管理”。

### 4.2 开发范围

- Meeting Section：
  - 从 transcript 生成基础 sections。
  - section 绑定 start/end time 和 segment 范围。
  - insight/action item 尽量关联 section。
  - 前端支持 section 导航。
- Action Items 总视图：
  - 增加全局行动项页面或侧栏视图。
  - 支持按状态、负责人、截止时间、会议筛选。
  - 支持从行动项跳回来源会议和 citation。
- 处理体验增强：
  - 显示每个 pipeline step 的状态。
  - 区分上传成功、处理中、等待审阅、发布完成。
  - retry 后自动继续后续步骤。
- 基础导出：
  - 导出 Markdown。
  - 内容包括 summary、decisions、risks、action items 和 citations。
  - 导出结果保存为 `export` asset。

### 4.3 不做范围

- 不做 PDF 排版级导出。
- 不做团队权限和多人协同编辑。
- 不做跨会议 RAG。
- 不做外部任务系统同步。

### 4.4 交付物

- 会议详情页具备 section 导航。
- 用户可以从一个页面查看所有行动项。
- 处理失败和 retry 体验更清晰。
- 用户可以导出一份带引用的会议 Markdown。

### 4.5 验收标准

- 长 transcript 能按 section 快速定位。
- action item 总视图能筛选 `proposed`、`confirmed`、`in_progress`、`done`、`canceled`。
- 从 action item 总视图点击来源，能回到对应会议和 transcript segment。
- 导出的 Markdown 不丢失 citation 信息。
- retry 成功后不会产生重复 transcript、insight 或 action item。

---

## 5. Stage C：v0.3 知识库前置能力

### 5.1 目标

让会议不再只是单次处理结果，而是能沉淀成持续可检索的知识资产。

### 5.2 开发范围

- Workspace 级搜索：
  - 支持按关键词搜索会议标题、transcript、insight、action item。
  - 支持按时间、状态、会议语言过滤。
- 多会议索引准备：
  - embedding 继续按 `meeting_id` 隔离。
  - 增加 workspace 维度检索接口。
  - 保留权限过滤入口。
- 历史决策追踪：
  - 增加决策列表视图。
  - 支持从决策跳回来源会议和 citation。
- 重复行动项检测：
  - 在同一 workspace 内识别描述相近、负责人相近的 action item。
  - 只做提示，不自动合并。

### 5.3 不做范围

- 不开放任意跨会议聊天入口。
- 不做复杂 rerank 服务。
- 不做企业权限完整落地。
- 不自动改写历史会议内容。

### 5.4 交付物

- 用户可以搜索历史会议内容。
- 用户可以查看历史决策列表。
- 用户可以发现可能重复的行动项。
- 后端具备 workspace 范围检索的接口边界。

### 5.5 验收标准

- 搜索结果必须显示来源会议、时间和 citation。
- 多会议检索不能返回不属于当前 workspace 的数据。
- 重复行动项只提示“可能重复”，不自动取消或合并。
- 证据不足时仍遵守“不编造”规则。

---

## 6. Stage D：v0.4 协作与集成准备

### 6.1 目标

为团队协作、外部系统集成和长期运维做准备。

### 6.2 开发范围

- 用户与工作区：
  - 引入最小用户模型。
  - 支持 action item owner 关联真实用户。
  - 保留 workspace 权限字段。
- 通知与任务系统：
  - 设计任务同步 adapter。
  - 先支持导出或 webhook，不直接深接多个平台。
- Provider 配置界面：
  - 展示当前 ASR / LLM / Embedding provider。
  - 展示 provider 是否可用。
  - 不在前端展示完整 API key。
- 观测面板：
  - 展示 provider 调用次数、平均耗时、失败次数和成本估算。
  - 支持按会议查看处理耗时。

### 6.3 不做范围

- 不做完整企业 SSO。
- 不做复杂审批流。
- 不做自动任务分派。
- 不做多 provider 智能路由策略 UI。

### 6.4 交付物

- 行动项可以关联真实用户。
- provider 配置状态可见。
- 基础成本和失败率可追踪。
- 外部任务系统 adapter 边界明确。

### 6.5 验收标准

- 不暴露 API key、token 或敏感会议全文到普通日志。
- Provider 不可用时前端能明确提示当前缺失配置。
- Action item owner 从纯文本逐步过渡到用户引用时，不破坏历史数据。
- 所有 provider 调用仍记录 provider、model、prompt_version、latency 和 cost estimate。

---

## 7. 关键设计原则

### 7.1 先串联，不重构

当前核心模块已经存在。后续优先把已有模块串成自然流程，不应先做大规模重构。

推荐顺序：

```text
job runner
  -> pipeline orchestration
  -> publish validation
  -> Q&A persistence UI
  -> section/action/search enhancement
```

### 7.2 保持 evidence first

任何补充功能都不能绕过 citation：

- 发布前检查 citation。
- 导出时保留 citation。
- 搜索结果显示 citation。
- 多会议检索返回来源会议和 transcript 位置。

### 7.3 保持 provider adapter 边界

真实 provider 验证不能把 OpenAI SDK 直接写进业务 service。ASR、LLM、Embedding、Q&A 仍通过 adapter 接入。

### 7.4 失败可恢复

每个阶段都必须继续满足 partial result 原则：

- ASR 成功但 LLM 失败，用户仍能看 transcript。
- 结构化成功但 embedding 失败，用户仍能看洞察和行动项。
- Q&A 失败不影响会议审阅和发布。

---

## 8. 推荐实施顺序

### 8.1 第一批：必须先做

1. 自动处理流水线。
2. 真实 provider 配置验证。
3. Q&A 历史恢复。
4. 发布动作和发布前校验。

原因：这四项决定 v0.1 是否能从“代码可测”变成“用户可用”。

### 8.2 第二批：提升单会议可用性

1. Section 导航。
2. Action Items 总视图。
3. 处理进度增强。
4. Markdown 导出。

原因：这些能力会明显降低真实会议使用时的复查成本。

### 8.3 第三批：知识库能力

1. Workspace 搜索。
2. 历史决策追踪。
3. 重复行动项提示。
4. 多会议 Q&A 的接口预留。

原因：这些能力是 MeetMind 从单会议工具变成会议知识系统的关键。

---

## 9. 风险与应对

| 风险 | 影响 | 应对 |
| --- | --- | --- |
| 真实 ASR 质量不稳定 | Transcript 错误导致后续结构化失真 | 保留 transcript 编辑入口，低置信度提示，真实样例回归 |
| LLM citation 不稳定 | 关键结论无法发布 | 后端继续强校验 citation，失败可重试或人工补证据 |
| 自动 pipeline 失败难排查 | 用户不知道卡在哪一步 | 每个 step 独立 job 状态、失败原因和 retry |
| Q&A 首次提问慢 | 用户误以为系统卡住 | 结构化后提前建 embedding，前端显示索引状态 |
| Action item 跨会议膨胀 | 待办列表变乱 | 先做筛选和来源跳转，不急着做自动合并 |
| 过早做权限系统 | 拖慢 v0.1 收尾 | 先保留 workspace/user 字段和过滤边界 |

---

## 10. v0.1 完成定义

v0.1 不再以 Phase 8 文档状态作为唯一完成标准，而以真实用户路径为准。

只有同时满足下面条件，v0.1 才算产品闭环完成：

- 真实会议音频能上传并自动处理到 `ready_for_review`。
- 用户能看到可用 transcript。
- 系统能生成 summary、decisions、risks、action items。
- 每个 decision 和 action item 至少有一个 citation。
- 用户能点击 citation 回到 transcript。
- 用户能编辑、确认、开始、完成或取消 action item。
- 用户能提问当前会议，并得到带 citation 的回答。
- 证据不足时，Q&A 明确拒绝编造。
- 用户刷新页面后，会议详情、审阅状态和 Q&A 历史仍保留。
- 用户能发布会议，发布前系统执行最小质量校验。

---

## 11. 文档维护规则

后续推进时，本文件应与以下文档保持一致：

- `doc/04-development-plan.md`
- `doc/06-progress-tracking.md`
- `README.md`
- `RULE.md`

当补充阶段完成时，应同步更新：

1. 本文件对应阶段状态或验收记录。
2. `doc/06-progress-tracking.md` 的未完成事项和风险。
3. README 中的本地启动、provider 配置或验证说明。


# MeetMind 项目总览

> 版本：2026-06-28  
> 目标：说明 MeetMind 为什么做、做什么、不做什么，以及 v0.1 的最小成功标准。  
> 适用范围：产品定位、核心问题、产品原则、目标用户、第一阶段边界。

---

## 1. 一句话定位

**MeetMind 是一个将会议音频、视频、转写文本和人工记录转化为可信知识与可执行任务的会议智能系统。**

MeetMind 不只是生成会议摘要。它更关注会议内容后续能否被团队真正使用：

- 关键结论能否回到原始发言；
- 行动项是否有负责人、截止时间、状态和证据；
- 会议问答是否基于真实记录；
- 历史会议能否沉淀成可搜索、可复用的知识。

---

## 2. 趋势判断

### 2.1 会议 AI 已经成为办公基础能力

主流办公平台已经把 AI 会议能力内置到产品中：

- Microsoft Teams Intelligent Recap 已支持 AI notes、recommended tasks、speaker markers、topic chapters 等能力。
- Google Meet 的 Gemini note taking 已覆盖会议记录、action items、Google Docs/Calendar 联动。
- Zoom AI Companion 已支持基于 speech-to-text 的 meeting summary，并能通过邮件或聊天分享。

这说明单纯做“会议总结”已经不够有差异化。MeetMind 不能只是“上传录音，然后生成一段纪要”。

### 2.2 下一阶段机会在可信和行动闭环

会议智能下一阶段不是把会议变成漂亮文章，而是把会议变成可使用的工作资产：

- **可信**：每条总结、决策、行动项都能回到原始发言。
- **可追溯**：知道谁在什么时候说了什么。
- **可执行**：Action Items 有生命周期，而不是静态文本。
- **可检索**：会议内容能进入知识库，被后续搜索和问答复用。
- **可治理**：会议内容敏感，必须考虑权限、删除、审计和模型路由。

### 2.3 MeetMind 的核心判断

MeetMind 的系统核心不是聊天框，而是：

```text
会议证据
  -> 结构化知识
  -> 用户审阅
  -> 行动闭环
  -> 可检索知识库
```

AI 负责初步理解和提取，人负责确认和修正。

---

## 3. 当前阶段边界

### 3.1 先做什么

第一阶段重点做一个可信闭环：

```text
上传会议资料
  -> 生成带时间戳的转写
  -> 结构化提取总结、决策、风险、行动项
  -> 每个关键结论绑定原始发言证据
  -> 用户审阅、修正、确认
  -> 支持基于会议内容的问答
```

### 3.2 暂不做什么

当前阶段不优先做：

- 实时会议机器人；
- 桌面软件；
- 日历、邮箱、飞书、Slack、Jira 等完整集成；
- 复杂多租户权限系统；
- 自动执行外部任务；
- 会议效率分析大屏；
- 100% 准确的发言人识别承诺。

这些能力可以后续扩展，但不能拖慢 v0.1 的核心闭环。

---

## 4. 核心问题

会议结束后，团队常见问题不是“没有纪要”，而是：

- 纪要只记录结论，不知道结论从哪里来；
- Action Items 写得模糊，没有负责人、截止时间或上下文；
- 决策散落在聊天、录音、文档里，后面没人找得到；
- 参会者对同一件事理解不一致；
- AI 总结看起来流畅，但难以判断是否漏掉、编造或误解；
- 长会议回看成本太高，想找某一句话很痛苦。

MeetMind 要解决的核心问题是：

> 如何把一场会议转化为“可验证、可检索、可执行”的结构化工作资产？

---

## 5. 产品原则

### 5.1 Source First

转写片段是事实源头。总结、决策、风险、行动项只是从事实源头派生出来的结构化视图。

### 5.2 Structured First

核心 AI 输出必须结构化。关键结果不直接依赖 Markdown，而是通过 JSON Schema / Pydantic 模型进入系统。

### 5.3 Evidence First

没有证据的结论不应被展示为事实。Action Items、Decisions、Risks、Q&A answers 都必须尽量绑定 transcript segment 或时间戳引用。

### 5.4 Human-in-the-loop

AI 输出默认是 proposed。任何任务、决策、风险进入 confirmed 状态前，都应该允许用户审阅和修改。

### 5.5 Async First

v0.1 以会后异步处理为主。实时转写和实时问答是后续增强，不作为第一阶段主路径。

### 5.6 Model-agnostic

ASR、LLM、Embedding 都通过 adapter 隔离，方便在 OpenAI、Qwen、Claude、本地模型等方案之间切换。

### 5.7 Privacy by Design

会议内容默认敏感。系统从早期就要保留删除、权限、审计、脱敏和模型路由空间。

---

## 6. 用户与场景

### 6.1 核心用户

- **会议组织者**：希望快速产出可信纪要和行动项。
- **项目负责人**：关心决策、风险、任务推进和跨会议上下文。
- **普通参会者**：想快速回看错过的内容，确认自己负责什么。
- **团队管理员**：关心数据权限、历史会议沉淀和知识复用。

### 6.2 优先支持的会议类型

- 项目周会；
- 产品需求评审；
- 技术方案评审；
- 客户访谈；
- 事故复盘；
- 头脑风暴后的行动整理。

### 6.3 第一阶段核心用户路径

```text
用户上传会议音频或转写文本
  -> 系统显示处理进度
  -> 用户进入会议详情页
  -> 左侧查看 transcript
  -> 右侧查看 summary / decisions / risks / action items
  -> 点击任意结论跳转到对应原始发言
  -> 用户修正并确认行动项
  -> 用户在 Q&A 中追问会议内容
```

---

## 7. v0.1 最小成功标准

v0.1 只有达到下面标准，才算真正跑通：

- 上传一段真实会议音频后，系统能完成异步处理；
- 用户能看到带时间戳的 transcript；
- 系统能生成结构化 summary、decisions、risks、action items；
- 每个 action item 和 decision 至少有一个 citation；
- 点击 citation 能跳到 transcript 对应位置；
- 用户能修改并确认 action item；
- 用户能向当前会议提问，并得到带引用的回答；
- 当证据不足时，Q&A 会拒绝编造。

---

## 8. 文档地图

建议按以下顺序阅读：

1. `doc/00-overview.md`：项目总览与产品原则。
2. `doc/01-product-roadmap.md`：产品形态和交付路线。
3. `doc/02-system-architecture.md`：系统架构、数据流、核心模块、数据模型、API 草案。
4. `doc/03-technology-stack.md`：技术栈选型与取舍。
5. `doc/04-development-plan.md`：分阶段开发计划与验收标准。
6. `RULE.md`：开发规则、Git 规则、代码规范、阶段交付纪律。

---

## 9. 参考资料

- [Microsoft 2026 Work Trend Index: Agents, human agency, and opportunity](https://www.microsoft.com/en-us/worklab/work-trend-index/agents-human-agency-and-the-opportunity-for-every-organization)
- [Microsoft Teams Intelligent Recap](https://learn.microsoft.com/en-us/microsoftteams/intelligent-recap-calls-meetings)
- [Google Workspace: AI note taking and Take notes for me](https://workspace.google.com/solutions/ai/ai-note-taking/)
- [Zoom AI Companion Meeting Summary](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0058013)

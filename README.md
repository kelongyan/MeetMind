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
| 6 | [开发规则](./RULE.md) | Git、代码规范、低耦合、测试、安全、阶段交付纪律 |

---

## 当前仓库状态

当前仓库处于架构与开发规划阶段，尚未进入应用代码实现。

已完成：

- 项目总览与核心产品原则；
- 产品形态与交付路线；
- 系统架构方案；
- 技术栈方案；
- 分阶段开发计划；
- 工程规则与协作规范；
- GitHub 仓库初始化。

下一步：

1. 开始 Phase 0，搭建前后端基础工程。
2. 建立 Docker Compose、本地数据库和 Redis。
3. 建立后端测试框架和前端基础检查命令。
4. 推送 `phase-0-foundation` 阶段 tag。

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

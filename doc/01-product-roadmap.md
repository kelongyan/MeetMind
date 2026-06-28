# MeetMind 产品形态与交付路线方案书

> 版本：2026-06-28  
> 目标：明确 MeetMind 先做浏览器服务，后续再扩展桌面助手、本地能力和混合部署的产品路线。  
> 适用范围：产品形态、部署形态、阶段边界和后续扩展策略。

---

## 1. 结论

MeetMind 当前阶段采用：

```text
Web-first
  先做浏览器服务

Hybrid-ready
  架构预留本地处理、桌面助手、私有化部署能力
```

一句话判断：

> MeetMind 的主产品应该先是浏览器服务，而不是桌面软件。桌面端后续作为本地采集、本地转写和隐私增强能力补充。

---

## 2. 为什么先做浏览器服务

### 2.1 MeetMind 的核心不是“打开一个本地工具”

MeetMind 真正要解决的是会议知识与行动闭环：

- 上传会议资料；
- 异步转写；
- 结构化理解；
- 引用追溯；
- Action Item 生命周期；
- 单会议和多会议问答；
- 团队协作；
- 权限、审计和治理；
- 历史会议知识库。

这些能力天然更适合浏览器服务和后端系统。

### 2.2 浏览器服务更适合当前闭环

浏览器服务的优势：

- 打开即用，不要求用户安装客户端；
- 前后端职责清晰；
- 异步任务适合在后端 worker 执行；
- 数据库和对象存储天然适合会议知识沉淀；
- 团队协作、权限和分享更自然；
- 后续部署到云端或私有化都方便；
- 更容易观察任务状态、成本、失败和重试。

### 2.3 桌面软件会提前引入额外复杂度

如果第一阶段直接做桌面软件，会遇到：

- Windows/macOS 打包；
- 自动更新；
- 本地权限；
- 系统音频采集；
- 本地 FFmpeg / Whisper / CUDA 环境；
- 本地文件加密；
- 崩溃日志；
- 不同电脑性能差异；
- 协作和同步问题。

这些问题都不是 MeetMind 第一阶段的核心价值。先做桌面端会让项目过早偏离“可信会议智能闭环”。

---

## 3. 产品形态分层

### 3.1 主产品：浏览器 Web App

职责：

- 会议列表；
- 会议创建；
- 文件上传；
- 处理状态展示；
- transcript viewer；
- summary / decisions / risks / action items 展示；
- citation 点击跳转；
- action item 审阅与确认；
- 单会议 Q&A；
- 后续多会议知识库。

用户通过浏览器完成主要工作。

### 3.2 后端服务：Meeting Intelligence Backend

职责：

- 文件接收；
- asset 管理；
- job 管理；
- 媒体处理；
- ASR 转写；
- LLM 结构化理解；
- citation 生成；
- embedding；
- RAG 问答；
- action item 状态流转；
- 权限和审计。

这是 MeetMind 的核心。

### 3.3 后续补充：桌面/本地助手

桌面助手不作为第一阶段主产品。

未来职责：

- 本地会议录音；
- 系统音频采集；
- 本地文件监听；
- 本地 Whisper 转写；
- 敏感会议本地预处理；
- 离线临时缓存；
- 一键同步到 Web 服务。

桌面助手只做采集和本地增强，不负责完整会议知识系统。

---

## 4. 推荐交付路线

### 4.1 v0.1：浏览器服务 MVP

目标：

跑通单会议可信闭环。

范围：

- Web 上传会议资料；
- 后端异步处理；
- 音频转写；
- transcript 展示；
- summary / decisions / risks / action items；
- citations；
- 用户审阅；
- 单会议 Q&A。

不做：

- 桌面端；
- 实时会议；
- 多会议知识库；
- 外部工具集成；
- 复杂权限系统。

### 4.2 v0.2：浏览器服务增强

目标：

让单会议体验稳定，开始沉淀知识库能力。

范围：

- 多会议列表和搜索；
- 项目或标签维度组织会议；
- 导出 Markdown / PDF；
- Prompt 版本管理；
- Citation verifier；
- 更好的 section 导航；
- 基础权限模型。

### 4.3 v0.3：会议知识库

目标：

让会议从单次处理变成持续知识资产。

范围：

- workspace 级搜索；
- 多会议 Q&A；
- 历史决策追踪；
- 项目 timeline；
- 重复 action item 检测；
- 按主题聚合会议上下文。

### 4.4 v0.4：协作与集成

目标：

把会议结果连接到团队工作流。

范围：

- 用户和工作区；
- Action Item 分配；
- 通知；
- Slack / 飞书 / Jira / Linear / Notion 集成；
- 会议 digest 自动发送。

### 4.5 v0.5：桌面/本地助手

目标：

补齐本地采集和敏感会议处理能力。

范围：

- 本地录音；
- 本地文件监听；
- 本地 ASR；
- 本地缓存；
- 同步到 Web；
- 敏感会议 local-only 处理模式。

候选技术：

- Tauri；
- Electron；
- 本地 Python worker；
- 本地 FFmpeg；
- faster-whisper。

当前倾向：

- 优先评估 Tauri，因为体积更轻；
- 如果系统音频采集和生态支持不够，再评估 Electron。

### 4.6 v1.0：混合部署

目标：

支持不同组织的数据和部署偏好。

形态：

```text
Cloud-first
  云端托管，优先速度和效果。

Hybrid
  普通会议云端处理，敏感会议本地或私有处理。

Private Deployment
  私有化部署 API、数据库、对象存储和模型服务。

Local-only
  极高敏感场景，本地处理和本地存储。
```

---

## 5. 架构演进路线

### 5.1 第一阶段架构

```text
Browser
  -> Next.js Web App
  -> FastAPI Backend
  -> Celery Worker
  -> PostgreSQL / pgvector
  -> Redis
  -> Object Storage
  -> AI Providers
```

特点：

- 模块化单体；
- 后端异步任务；
- 单会议处理；
- 云端或本地 provider 可替换。

### 5.2 第二阶段架构

```text
Browser
  -> Web App
  -> Backend API
  -> Worker Pool
  -> PostgreSQL / pgvector
  -> Object Storage
  -> Observability
```

增强：

- 多 worker；
- 更完整 job monitoring；
- prompt/version tracking；
- workspace-level retrieval；
- 基础权限。

### 5.3 第三阶段架构

```text
Desktop Helper
  -> Local Capture
  -> Local Preprocessing
  -> Optional Local ASR
  -> Sync Client
  -> Web Backend
```

增强：

- 本地录音；
- 本地转写；
- 本地敏感数据处理；
- 与 Web 服务同步。

### 5.4 第四阶段架构

```text
Cloud Deployment
Private Deployment
Local Processing Node
Shared Web Interface
```

增强：

- 私有化部署；
- local/hybrid/cloud 模型路由；
- 企业数据治理；
- 审计和保留策略。

---

## 6. 不同形态对比

| 形态 | 优点 | 缺点 | 当前判断 |
| --- | --- | --- | --- |
| 浏览器服务 | 协作自然、部署简单、异步任务清晰、知识库友好 | 依赖后端和网络 | 当前主线 |
| 桌面软件 | 本地采集强、隐私能力强、可离线 | 打包、权限、更新、本地环境复杂 | 后续补充 |
| 纯本地工具 | 数据不出本机、隐私强 | 协作弱、知识库弱、部署支持复杂 | 不作为主线 |
| 浏览器插件 | 轻量、贴近会议网页 | 权限和平台限制多，能力不完整 | 后续按需 |
| 私有化部署 | 数据治理强 | 运维成本高 | v1.0 后评估 |

---

## 7. 关键边界

### 7.1 v0.1 必须克制

v0.1 只做浏览器服务，重点是：

- 上传；
- 转写；
- 结构化；
- 引用；
- 审阅；
- 单会议问答。

不要加入：

- 桌面端；
- 实时录音；
- 系统音频采集；
- 多平台机器人；
- 完整外部任务集成。

### 7.2 后续扩展不应破坏主线

桌面助手、本地模型、私有化部署都应该围绕主系统扩展，而不是另起一套产品逻辑。

核心数据模型仍以 Web 后端为中心：

- meeting；
- asset；
- transcript_segment；
- insight_item；
- action_item；
- citation；
- embedding；
- qa_message。

### 7.3 本地能力必须通过同步边界

桌面助手如果出现，只通过明确同步接口与后端通信：

```text
local asset
local transcript
local processing metadata
sync status
```

不允许桌面端直接操作远端数据库。

---

## 8. 推荐执行顺序

当前推荐：

```text
1. 确定 Web-first 产品形态
2. 完成 Phase 0 工程基线
3. 完成 Phase 1-4 后端可信处理链路
4. 完成 Phase 5 Web 工作台
5. 完成 Phase 6-7 Q&A 和审阅闭环
6. 完成 Phase 8 稳定性与部署准备
7. 再评估桌面/本地助手
```

原因：

- 先验证核心价值；
- 避免过早陷入客户端工程；
- 保持数据模型统一；
- 保留后续本地化空间；
- 让每个阶段都有可验收结果。

---

## 9. 当前决策

已确定：

- 主产品形态：浏览器服务。
- v0.1 不做桌面软件。
- v0.1 不做实时会议。
- 后端作为会议智能核心。
- 桌面端后续只作为本地采集和隐私增强补充。

待后续评估：

- 桌面助手采用 Tauri 还是 Electron。
- 本地 ASR 默认使用 faster-whisper 还是其他方案。
- 私有化部署是否需要支持 Kubernetes。
- 企业版是否需要 local-only 模式。

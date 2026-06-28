# MeetMind 开发规则

> 本文件是 MeetMind 的工程纪律。所有开发、重构、测试、提交和阶段交付都必须遵守。  
> 如果本文件和临时想法冲突，以本文件为准；如果确实需要改变规则，先修改本文件并说明原因。

---

## 1. 项目目标

MeetMind 的核心目标是构建一个可信会议智能系统：

- 能处理会议音频、视频、转写文本和字幕。
- 能生成结构化会议内容。
- 能把关键结论追溯到原始发言。
- 能让用户审阅、修正和确认 AI 结果。
- 能沉淀可检索、可复用的会议知识。

项目优先级：

```text
正确性 > 可读性 > 可维护性 > 性能优化 > 功能数量
```

---

## 2. 阶段开发规则

### 2.0 方案书来源

开发前必须优先阅读并遵守以下方案书：

- `doc/00-overview.md`：项目总览、核心问题、产品原则和 v0.1 成功标准。
- `doc/01-product-roadmap.md`：产品形态路线，明确先浏览器服务，后续扩展桌面/本地/混合部署能力。
- `doc/02-system-architecture.md`：系统架构、核心模块、数据模型、API、RAG 和治理要求。
- `doc/03-technology-stack.md`：技术栈选型、推荐方案、备选方案和暂不推荐路线。
- `doc/04-development-plan.md`：分阶段开发计划与阶段验收标准。
- `doc/05-ui-design.md`：UI 设计规范、视觉风格、页面结构、组件状态和无障碍要求。

技术栈和产品形态相关决策以对应方案书为准。除非先更新方案书并说明原因，否则不要在代码中引入与方案书冲突的框架、架构或部署路线。

### 2.1 阶段来源

所有阶段以 `doc/04-development-plan.md` 为准。

开发前必须确认当前阶段：

```text
Phase 0: 工程基线
Phase 1: 后端核心领域
Phase 2: 上传与异步任务
Phase 3: 语音转写链路
Phase 4: 结构化理解与引用
Phase 5: 会议工作台前端
Phase 6: 单会议 Q&A
Phase 7: 审阅与行动闭环
Phase 8: 稳定性与部署准备
```

### 2.2 阶段状态

阶段状态只能使用：

```text
Not Started
In Progress
Blocked
Done
```

每完成一个阶段，必须更新 `doc/04-development-plan.md` 中对应阶段状态。

### 2.3 阶段完成标准

一个阶段只有同时满足以下条件，才能标记为 `Done`：

- 阶段范围内功能已完成。
- 阶段明确不做的内容没有被偷偷塞进去。
- 阶段验收标准全部满足。
- 测试和检查命令已运行。
- 无明显临时代码、调试代码、无用导入。
- 文档状态已更新。
- Git commit 已创建。
- Git tag 已创建。
- `main` 分支和 tag 已推送到 GitHub。

### 2.4 阶段 tag

阶段 tag 固定为：

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

禁止随意改名，避免后续追踪混乱。

---

## 3. Git 规则

### 3.1 分支规则

- 默认只使用 `main` 分支。
- 未经明确允许，不新建分支。
- 不使用 `git reset --hard`、强推、覆盖远端历史等破坏性操作。
- 不使用 `git add .`，优先 stage 明确文件。

### 3.2 提交规则

提交信息使用以下前缀：

```text
feat: 新功能
fix: 修复问题
docs: 文档修改
refactor: 重构
test: 测试
chore: 工程配置或杂项
```

提交示例：

```powershell
git add apps/api/app/meetings apps/api/tests/meetings
git commit -m "feat: add meeting domain APIs"
```

### 3.3 推送规则

阶段完成后必须推送：

```powershell
git push -u origin main
git push origin <phase-tag>
```

如果远端不存在，需要先添加：

```powershell
git remote add origin <github-repo-url>
```

### 3.4 禁止提交的内容

禁止提交：

- `.env`
- API key
- token
- credentials
- 私密会议录音
- 客户资料
- 本地数据库文件
- 大型临时文件
- 构建产物
- 缓存目录

必须提供 `.env.example`，但里面只能放变量名和安全示例值。

---

## 4. 架构规则

### 4.1 低耦合

模块之间必须通过清晰接口通信，不能互相偷拿内部实现。

禁止：

- API route 里直接写复杂业务逻辑。
- 业务 service 直接调用具体外部模型 SDK。
- 前端组件直接依赖后端数据库字段细节。
- 多个模块共享可变全局状态。

推荐：

- Route 只负责参数解析、权限检查、调用 service、返回响应。
- Service 负责业务流程。
- Repository 负责数据访问。
- Provider adapter 负责外部服务调用。
- Schema / DTO 负责边界数据结构。

### 4.2 单一职责

每个文件、类、函数都应该有清楚职责。

判断标准：

- 文件名能说明它负责什么。
- 修改一个功能时，不需要顺手改大量无关模块。
- 测试某个模块时，可以 mock 它的外部依赖。

### 4.3 依赖方向

依赖方向应保持稳定：

```text
API Layer
  -> Service Layer
  -> Repository Layer
  -> Database

Service Layer
  -> Provider Interface
  -> Provider Implementation
```

禁止反向依赖：

- Database model 不依赖 API route。
- Provider implementation 不依赖业务 route。
- UI 基础组件不依赖具体业务页面。

### 4.4 Adapter 优先

所有可替换外部能力必须通过 adapter：

- ASR provider
- LLM provider
- Embedding provider
- Object storage provider
- Queue provider
- Notification provider

业务代码只能依赖接口，不能依赖具体供应商 SDK。

---

## 5. 后端代码规范

### 5.1 FastAPI 路由

路由层只做：

- 请求参数校验。
- 调用 service。
- 返回响应模型。
- 抛出明确 HTTP 错误。

路由层不做：

- 复杂业务判断。
- 数据库拼装。
- 外部模型调用。
- 文件处理细节。

### 5.2 Pydantic Schema

所有 API 输入输出必须有明确 schema。

规则：

- 不直接暴露 ORM 对象。
- 不把内部字段无筛选返回给前端。
- 时间、状态、枚举值必须类型明确。
- AI 输出必须经过 Pydantic 校验后才能入库。

### 5.3 数据库

规则：

- 数据模型变更必须配 migration。
- migration 必须可从空库跑通。
- 删除字段或表前必须确认没有被当前代码使用。
- 外键关系要清晰。
- 状态字段必须枚举化。

### 5.4 异步任务

规则：

- 长耗时操作必须进队列。
- Job 状态必须可查询。
- Job 失败必须记录 failure_code 和 failure_message。
- Retry 必须尽量幂等。
- 不允许因为一个 provider 失败导致整个后端服务崩溃。

### 5.5 错误处理

规则：

- 对用户可理解的错误，返回清楚错误信息。
- 对开发者排查需要的信息，写入日志。
- 不把 API key、token、完整敏感文本写入普通日志。
- 不吞异常后假装成功。

---

## 6. 前端代码规范

### 6.0 JS 包管理

JS 依赖管理和脚本执行统一使用 `pnpm`。

规则：

- 禁止使用 `npm install`、`npm run`、`yarn` 或 `npx` 作为项目常规命令。
- 文档、脚本和阶段验收命令必须使用 `pnpm`。
- 需要临时执行包命令时，优先使用 `pnpm exec` 或 `pnpm dlx`。
- 前端和未来 shared package 通过 `pnpm workspace` 管理。

### 6.1 组件分层

推荐分层：

```text
app/              路由页面
features/         业务功能模块
components/       可复用 UI 组件
lib/              API client、工具函数、配置
```

页面负责组合，业务组件负责场景，基础组件负责表现。

### 6.2 状态处理

每个异步页面必须处理：

- loading
- empty
- error
- success

禁止页面在请求失败时空白。

### 6.3 可访问性

规则：

- 按钮必须是 button 或具备正确 role。
- 表单输入必须有 label。
- 图标按钮必须有可理解的 aria-label 或 tooltip。
- 主要操作必须可用键盘访问。
- 颜色不能是唯一状态表达。

### 6.4 UI 边界

规则：

- Transcript、Action Items、Citations 必须能在长内容下正常滚动。
- 文本不能溢出按钮和卡片。
- 错误信息要具体，不写“出错了”这种空话。
- 不在前端硬编码 AI provider 细节。

---

## 7. AI 能力规范

### 7.1 Structured First

核心 AI 输出必须结构化：

- Summary 可以渲染为文本，但原始结果要有结构。
- Action Items 必须是对象。
- Decisions 必须是对象。
- Risks 必须是对象。
- Citations 必须是对象。

禁止把一大段 Markdown 当作核心数据源。

### 7.2 Evidence First

以下内容必须有 citation：

- decision
- risk
- action item
- open question
- Q&A answer 中的关键事实

没有 citation 的关键结论只能作为草稿，不能当作已确认事实。

### 7.3 Human-in-the-loop

AI 结果默认状态为 proposed。

进入 confirmed 必须经过用户确认，或经过明确的系统规则确认。

### 7.4 Prompt 管理

Prompt 必须版本化。

每次 AI 调用至少记录：

- provider
- model
- prompt_version
- input size
- output size
- latency
- retry count
- schema validation result

### 7.5 反幻觉规则

AI 不允许：

- 凭空补 owner。
- 凭空补 due date。
- 把讨论中的可能方案写成已确认决策。
- 在证据不足时给肯定回答。
- 隐藏不确定性。

证据不足时，必须明确说明：

```text
未在会议记录中找到足够证据。
```

---

## 8. 测试规范

### 8.1 测试优先级

测试优先覆盖：

- 数据模型状态流转。
- JSON Schema 校验。
- Citation 生成与校验。
- Job 状态和 retry。
- Provider adapter mock。
- Q&A 证据不足拒答。
- 前端关键交互。

### 8.2 测试类型

必须逐步建立：

- Unit tests
- Integration tests
- E2E smoke tests
- Golden sample regression

### 8.3 外部依赖

测试中默认 mock 外部 provider：

- ASR
- LLM
- Embedding
- Object storage

只有少数手动验证脚本允许调用真实 provider。

### 8.4 阶段完成前验证

阶段完成前必须运行该阶段方案书里的验证命令。

如果因为环境原因无法运行，必须在提交说明或阶段记录中写清楚：

- 哪个命令没运行；
- 为什么没运行；
- 替代验证做了什么；
- 后续如何补验证。

---

## 9. 文档规范

### 9.1 必改文档

以下情况必须更新文档：

- 阶段状态变化。
- 数据模型重大变化。
- API 设计变化。
- Provider 选择变化。
- 部署方式变化。
- 隐私和数据处理策略变化。

### 9.2 文档位置

- 项目总览：`doc/00-overview.md`
- 产品路线：`doc/01-product-roadmap.md`
- 系统架构：`doc/02-system-architecture.md`
- 技术栈方案：`doc/03-technology-stack.md`
- 分阶段方案：`doc/04-development-plan.md`
- UI 设计方案：`doc/05-ui-design.md`
- 工程规则：`RULE.md`

### 9.3 文档风格

规则：

- 写清楚当前决策。
- 写清楚不做什么。
- 写清楚验收标准。
- 不写空泛口号。
- 不保留过期结论。

---

## 10. 安全与隐私规范

### 10.1 数据处理

会议数据默认敏感。

规则：

- 原始音视频与结构化结果分开存储。
- 用户必须能删除会议。
- 用户必须能删除原始音视频。
- AI provider 调用必须可追踪。
- 不在日志中输出完整会议内容。

### 10.2 密钥管理

规则：

- 密钥只放环境变量。
- `.env` 不进入 Git。
- `.env.example` 只放安全示例。
- 任何 key 泄露都必须立即轮换。

### 10.3 模型路由

系统应保留三种模式：

```text
local_only
hybrid
cloud_first
```

不同敏感级别的会议后续可以选择不同模型路由。

---

## 11. 性能与成本规范

### 11.1 不提前优化

没有真实瓶颈前，不做复杂性能优化。

但以下信息要从早期开始记录：

- ASR 耗时。
- LLM 耗时。
- Embedding 耗时。
- token 使用量。
- provider 成本估算。
- 文件大小。
- 会议时长。

### 11.2 长会议策略

长会议必须走 chunking：

```text
audio chunks
  -> transcript segments
  -> semantic chunks
  -> chunk-level extraction
  -> meeting-level merge
  -> citation verification
```

禁止把超长 transcript 直接塞进单次 LLM 调用。

---

## 12. 代码审查清单

每次准备提交前自查：

- 改动是否属于当前阶段？
- 有没有引入未要求的功能？
- 有没有违反低耦合原则？
- 有没有直接依赖具体 provider SDK？
- 有没有缺少 schema 校验？
- 有没有没有 citation 的关键 AI 结论？
- 有没有临时日志或调试代码？
- 有没有提交密钥或敏感文件？
- 测试是否覆盖核心行为？
- 文档是否需要同步更新？

---

## 13. 推荐开发顺序

当前推荐顺序：

```text
1. 初始化 Git 和远端仓库
2. 提交现有文档基线
3. 开始 Phase 0
4. 每完成一个阶段，更新文档、提交、打 tag、推送
5. 阶段之间不跳跃开发
```

初始化命令示例：

```powershell
git init -b main
git add README.md RULE.md doc/00-overview.md doc/01-product-roadmap.md doc/02-system-architecture.md doc/03-technology-stack.md doc/04-development-plan.md
git commit -m "docs: establish project architecture and development rules"
git remote add origin <github-repo-url>
git push -u origin main
```

---

## 14. 最重要的底线

任何阶段都不能为了看起来进展快而牺牲以下底线：

- AI 输出必须可验证。
- 关键结论必须可追溯。
- 外部 provider 必须可替换。
- 阶段完成必须有验证。
- GitHub 上必须能追踪每个阶段的交付点。

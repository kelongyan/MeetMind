# MeetMind UI 设计方案

> 版本：2026-06-28  
> 目标：定义 MeetMind 浏览器服务的界面风格、布局体系、组件规范、关键页面和交互状态。  
> 适用范围：Phase 5 会议工作台前端，以及后续 Web App 的所有页面。

---

## 1. 设计定位

MeetMind 的 UI 应该是 **正式、克制、清晰、可信、工作台型**。

它不是营销站，不需要大面积装饰、夸张动效或情绪化视觉。它的核心任务是帮助用户高效完成：

- 上传会议资料；
- 查看处理状态；
- 阅读 transcript；
- 验证 AI 生成的 summary、decisions、risks、action items；
- 点击 citation 回到原始发言；
- 审阅并确认 action item；
- 基于会议内容提问。

整体感受应该接近专业 SaaS 工作台、文档审阅系统和任务管理工具的结合，而不是聊天产品或宣传页。

---

## 2. 设计原则

### 2.1 Trust First

界面必须强化可信感：

- AI 输出要明确标记 proposed / confirmed；
- 关键结论要露出 citation；
- 低置信度内容要有温和提示；
- 用户能快速回到原始 transcript；
- 不用夸张文案暗示 AI 永远正确。

### 2.2 Source Visible

原始发言是系统事实源。UI 中 transcript 不应该被藏太深。会议详情页必须让用户能在结构化结果和原始文本之间快速切换或联动。

### 2.3 Workbench, not Landing Page

第一屏应该是可操作的工作台，而不是宣传区。避免大标题 hero、装饰卡片堆叠、渐变背景和过度插画。

### 2.4 Dense but Calm

会议内容信息量大，界面需要有足够信息密度，但不能拥挤。通过留白、分隔线、层级、标签和固定区域来组织，而不是靠大色块。

### 2.5 Reviewable AI

AI 结果必须可审阅、可编辑、可确认、可撤销。用户不应该感觉自己只能接受模型输出。

### 2.6 Accessible by Default

按钮、表单、状态、引用跳转、键盘导航、颜色对比都要从一开始考虑无障碍。

---

## 3. 视觉风格

### 3.1 色彩方向

整体采用 **白、蓝、灰** 为主。

推荐气质：

```text
白：干净、内容优先
蓝：可信、技术、主操作
灰：秩序、层级、辅助信息
少量状态色：用于成功、警告、错误、风险
```

避免：

- 大面积纯黑深色界面；
- 大面积紫蓝渐变；
- 彩虹式多色标签；
- 过多高饱和蓝色；
- 暖色调主视觉；
- 装饰性背景图案。

### 3.2 色彩 Token 建议

```text
Background:
  page:        #F8FAFC
  surface:     #FFFFFF
  muted:       #F1F5F9

Border:
  default:     #E2E8F0
  strong:      #CBD5E1

Text:
  primary:     #0F172A
  secondary:   #475569
  muted:       #64748B
  disabled:    #94A3B8

Brand Blue:
  primary:     #2563EB
  hover:       #1D4ED8
  soft:        #EFF6FF
  border:      #BFDBFE

State:
  success:     #16A34A
  successSoft: #F0FDF4
  warning:     #D97706
  warningSoft: #FFFBEB
  danger:      #DC2626
  dangerSoft:  #FEF2F2
  info:        #0284C7
  infoSoft:    #F0F9FF
```

### 3.3 配色使用规则

- 主操作按钮使用 brand blue。
- 页面背景使用浅灰白，不用纯白铺满所有区域。
- 卡片和面板使用白色 surface。
- 边框使用浅灰，不使用重阴影。
- 状态色只用于状态，不用于装饰。
- AI proposed 用蓝灰或浅蓝。
- confirmed 用绿色或明确状态标签。
- risk 用 warning 或 danger，但要克制。

---

## 4. 字体与排版

### 4.1 字体

推荐：

```text
font-family:
  Inter,
  ui-sans-serif,
  system-ui,
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  "Microsoft YaHei",
  sans-serif;
```

中文环境要保证：

- 字重不要过细；
- 行高足够；
- 长 transcript 阅读不累；
- 数字和时间戳对齐稳定。

### 4.2 字号层级

```text
Page Title:       24px / 32px / 600
Section Title:    18px / 28px / 600
Panel Title:      15px / 24px / 600
Body:             14px / 22px / 400
Dense Body:       13px / 20px / 400
Caption:          12px / 18px / 400
Timestamp:        12px / 18px / 500
```

### 4.3 排版规则

- 不使用负字距。
- 不用随视口变化的字体大小。
- transcript 正文行高要高于普通表格。
- 时间戳、状态、置信度使用小号但不能低对比。
- 面板标题不要用 hero 级大字。

---

## 5. 布局体系

### 5.1 应用整体布局

推荐结构：

```text
┌──────────────────────────────────────────────────────────────┐
│ Top Bar                                                       │
├───────────────┬──────────────────────────────────────────────┤
│ Sidebar       │ Main Content                                  │
│               │                                              │
│ Meetings      │ Meeting List / Meeting Detail / Review / QA  │
│ Knowledge     │                                              │
│ Settings      │                                              │
└───────────────┴──────────────────────────────────────────────┘
```

### 5.2 桌面端尺寸

```text
Sidebar width:        240px
Top bar height:       56px
Page max content:     none for workbench
Content padding:      24px
Panel gap:            16px
Card radius:          8px max
Panel radius:         8px max
```

### 5.3 移动端策略

v0.1 以桌面工作台为主，但不能在移动端完全崩坏。

移动端策略：

- Sidebar 收起为顶部菜单；
- 会议详情页从双栏变成上下结构；
- Transcript 和 insights 使用 tabs；
- 长操作按钮全宽；
- 避免横向溢出。

### 5.4 不使用的布局

禁止：

- Hero landing 首屏；
- 大面积渐变背景；
- 嵌套卡片；
- 页面 section 全部做成浮动卡片；
- 用装饰性图形占据主要视野；
- 只有聊天框没有工作台结构。

---

## 6. 信息架构

### 6.1 主导航

v0.1 推荐导航：

```text
Meetings
Knowledge
Action Items
Settings
```

其中：

- Meetings：会议列表、上传、详情；
- Knowledge：后续多会议知识库；
- Action Items：后续跨会议任务视图；
- Settings：provider、隐私、工作区配置。

v0.1 可以先实现 Meetings，其余导航可以隐藏或禁用，避免假入口。

### 6.2 会议详情信息层级

优先级：

```text
1. 会议标题、状态、处理进度
2. Transcript
3. Summary
4. Action Items
5. Decisions
6. Risks
7. Q&A
8. Metadata
```

### 6.3 右侧洞察面板排序

推荐：

```text
Action Items
Decisions
Risks
Summary
Open Questions
```

原因：MeetMind 的价值在可执行和可信引用，Action Items 应该比普通摘要更突出。

---

## 7. 核心页面设计

### 7.1 Meetings 列表页

目标：

让用户快速找到会议、看到处理状态、上传新会议。

布局：

```text
Top Bar
Sidebar
Main:
  Header: Meetings + Upload Button
  Filter Row: Search / Status / Date / Owner
  Table or List:
    Title
    Status
    Duration
    Created At
    Action Items Count
    Last Updated
```

状态显示：

- uploaded；
- transcribing；
- structuring；
- ready_for_review；
- published；
- failed。

设计要点：

- 默认用表格或紧凑列表，不用大卡片网格；
- status badge 要可扫描；
- failed 状态提供 retry 入口；
- 上传按钮固定在页面右上或 header 区域。

### 7.2 上传页面 / 上传弹窗

目标：

让用户明确知道支持什么文件、上传后会发生什么。

内容：

- 文件拖拽区域；
- 支持格式说明；
- 会议标题输入；
- 可选语言；
- 隐私/模型路由提示；
- 上传进度；
- 上传成功后进入 job 状态页或会议详情页。

设计要点：

- 不把上传和处理混为一谈；
- 上传成功后显示“处理中”，不暗示已经完成；
- 大文件上传要有进度和可取消状态；
- 失败错误要说明是上传失败、格式错误还是处理失败。

### 7.3 会议详情页

这是 MeetMind 最重要的页面。

推荐桌面布局：

```text
┌──────────────────────────────────────────────────────────────┐
│ Meeting Header: title / status / duration / actions           │
├──────────────────────────────┬───────────────────────────────┤
│ Transcript Panel              │ Insight Panel                 │
│                               │                               │
│ [00:01:20] Speaker A ...      │ Action Items                  │
│ [00:01:40] Speaker B ...      │ Decisions                     │
│ [00:02:05] Speaker A ...      │ Risks                         │
│                               │ Summary                       │
└──────────────────────────────┴───────────────────────────────┘
│ Q&A Panel or Drawer                                             │
└──────────────────────────────────────────────────────────────┘
```

推荐比例：

```text
Transcript: 58%
Insights:   42%
```

交互：

- 点击 insight 高亮对应 transcript segment；
- 点击 citation 滚动到原文；
- transcript 当前引用片段使用浅蓝背景；
- 用户可编辑 proposed action item；
- confirmed 状态不可直接覆盖，需要进入编辑动作。

### 7.4 Transcript Panel

每条 transcript segment 包含：

```text
timestamp
speaker
text
confidence marker optional
```

视觉规则：

- timestamp 使用等宽或半等宽风格；
- speaker 使用中性色 badge；
- 当前引用片段使用 `brand soft` 背景；
- 低置信度片段使用 warning dot，不要大面积警告色；
- 长文本自然换行。

### 7.5 Insight Panel

Insight 类型：

- Action Item；
- Decision；
- Risk；
- Summary；
- Open Question。

卡片结构：

```text
Header: type badge + status
Title / description
Owner / due date / confidence
Citation chips
Actions: edit / confirm / dismiss
```

设计规则：

- 卡片边框轻，背景白；
- 不在卡片里再嵌套卡片；
- citation chip 使用链接样式；
- proposed 和 confirmed 状态必须明显区分；
- action item 是最突出区域。

### 7.6 Review 页面

目标：

让用户集中处理 AI 生成结果。

布局：

```text
Left: AI Proposed Items
Right: Source Evidence / Transcript Context
Bottom or Header: Confirm All / Save Draft / Publish
```

规则：

- 不提供无脑“全部确认”为默认主操作；
- confirm all 需要二次确认；
- 每个 item 都能查看来源；
- 修改 owner / due date 时保留原始 AI 提取文本。

### 7.7 Q&A 页面/面板

Q&A 不应该压过证据链。

回答结构：

```text
Answer
Sources
Related Action Items / Decisions
Ask follow-up
```

规则：

- 回答必须展示 citations；
- 证据不足时用普通信息状态，不用错误状态；
- 不把 Q&A 做成全屏聊天产品；
- 当前会议范围要明确显示。

---

## 8. 组件规范

### 8.1 Button

类型：

```text
Primary     主要动作，如 Upload、Confirm
Secondary   次要动作，如 Edit、Retry
Ghost       轻量动作，如 Copy、Open source
Danger      删除、取消确认
Icon        引用跳转、更多操作
```

规则：

- 主按钮使用蓝色；
- 每个页面只保留 1 个最强主操作；
- 删除类操作必须使用 danger；
- 图标按钮必须有 tooltip 或 aria-label；
- 按钮高度保持稳定，不随文本变形。

### 8.2 Badge

用途：

- job status；
- insight type；
- action status；
- speaker；
- risk level。

规则：

- badge 用于短文本，不承载长说明；
- 不使用高饱和大色块；
- proposed 使用蓝灰；
- confirmed 使用绿色；
- failed 使用红色；
- processing 使用蓝色或中性加载状态。

### 8.3 Table / List

会议列表优先表格或紧凑列表。

规则：

- 支持搜索和筛选；
- 状态列靠前；
- 时间列格式统一；
- 空状态提供上传入口；
- failed row 提供 retry。

### 8.4 Tabs

用于：

- Transcript / Insights 移动端切换；
- Summary / Action Items / Decisions / Risks；
- Q&A / Metadata。

规则：

- tabs 不超过 5 个；
- 当前 tab 状态明确；
- 不把主导航做成 tabs。

### 8.5 Drawer / Dialog

用途：

- 上传文件；
- 编辑 action item；
- 查看 citation 详情；
- 删除确认。

规则：

- 表单编辑优先 drawer；
- 危险确认用 dialog；
- drawer 不再嵌套 dialog，除非是删除确认；
- 关闭前如果有未保存修改，需要提醒。

### 8.6 Empty / Loading / Error

每个异步区域必须有：

- loading；
- empty；
- error；
- success。

错误信息要具体：

```text
无法读取转写结果，请稍后重试。
文件格式不支持，请上传 mp3、wav、mp4、m4a、webm、txt、srt 或 vtt。
结构化理解失败，可重新运行 AI 处理。
```

---

## 9. 状态设计

### 9.1 Processing Status

状态视觉：

```text
uploaded             neutral
media_processing     blue
transcribing         blue
segmenting           blue
structuring          blue
citing               blue
embedding            blue
ready_for_review     warning / info
published            success
failed_*             danger
```

### 9.2 Action Item Status

```text
proposed      blue gray
confirmed     green
in_progress   blue
done          gray / green
canceled      muted
```

### 9.3 AI Confidence

不要把 confidence 做成夸张百分比分数。推荐：

```text
High confidence
Needs review
Low confidence
```

低置信度必须提示用户核对 citation。

---

## 10. Citation 交互

Citation 是 MeetMind 的核心交互。

### 10.1 Citation Chip

样式：

```text
[00:03:21] Speaker B
```

点击行为：

- 滚动 transcript 到对应 segment；
- 高亮该 segment；
- 右侧 insight 保持选中状态；
- 如果 transcript panel 不可见，自动切换到 transcript。

### 10.2 高亮规则

- 当前引用：浅蓝背景；
- 多个引用：同组编号或连续高亮；
- 高亮 2-3 秒后保留轻微边框或左侧蓝线；
- 不使用闪烁动画。

### 10.3 引用不足

如果 insight 缺少 citation：

- 显示 `Needs source`；
- 不允许直接 confirmed；
- 提供重新生成或手动绑定 citation 的入口。

---

## 11. 响应式设计

### 11.1 Desktop

主目标尺寸：

```text
1366 x 768
1440 x 900
1920 x 1080
```

会议详情使用双栏布局。

### 11.2 Tablet

策略：

- Sidebar 可折叠；
- Transcript / Insights 可保持双栏或 tabs；
- Q&A 作为底部 drawer。

### 11.3 Mobile

策略：

- 单栏；
- Transcript / Insights / Q&A 使用 tabs；
- 上传流程可用；
- 复杂审阅体验允许弱化，但不能内容溢出。

---

## 12. 无障碍规范

必须满足：

- 所有按钮可键盘访问；
- 图标按钮有 aria-label；
- 表单控件有 label；
- 错误信息与输入关联；
- 状态不能只靠颜色表达；
- 文本和背景对比度足够；
- citation 跳转后焦点合理移动；
- loading 不阻塞屏幕阅读器理解当前状态。

---

## 13. 动效规范

动效只用于帮助理解状态变化。

允许：

- panel 展开/收起；
- drawer 进入/退出；
- citation scroll 和 highlight；
- loading skeleton；
- 轻量 hover。

禁止：

- 大面积背景动画；
- 装饰性粒子；
- 复杂入场动画；
- 闪烁高亮；
- 影响阅读 transcript 的动效。

---

## 14. 实现建议

技术栈参考 `doc/03-technology-stack.md`。

前端建议：

- 使用 TailwindCSS token 化颜色、间距、圆角；
- 使用 shadcn/ui 作为基础组件；
- 使用 lucide-react 图标；
- 使用 TanStack Query 管理异步状态；
- 保持组件按 feature 拆分；
- transcript viewer、insight panel、citation link 做成独立组件。

建议组件目录：

```text
apps/web/
  components/
    ui/
    layout/
  features/
    meetings/
      meeting-list/
      upload/
      meeting-detail/
      transcript/
      insights/
      citations/
      qa/
      review/
```

---

## 15. 页面验收标准

Phase 5 前端工作台至少满足：

- Meetings 列表可扫描；
- 上传入口明确；
- job 状态清楚；
- 会议详情页能同时查看 transcript 和 insights；
- citation 点击能定位 transcript；
- action item 可编辑、确认、取消；
- Q&A 回答展示 sources；
- loading / empty / error 状态齐全；
- 桌面布局不拥挤；
- 移动端不横向溢出；
- 图标按钮有 tooltip 或 aria-label；
- 页面没有装饰性大渐变、营销 hero 或无意义卡片堆叠。

---

## 16. 设计底线

任何 UI 实现都不能牺牲以下底线：

- 原始证据必须容易访问；
- AI 结果必须可审阅；
- 关键状态必须可见；
- 主要流程必须可完成；
- 界面必须保持正式、克制、清晰；
- 白蓝灰是主色调，状态色只服务状态；
- 不为了视觉效果降低信息密度和可读性。

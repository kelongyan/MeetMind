# MeetMind 前端 UI 重构升级方案书

> 版本：2026-07-01
> 目标：在不改变核心业务流程和信息架构的前提下，把 MeetMind 前端升级为统一、克制、证据导向的专业工作台。
> 范围：`apps/web`
> 非目标：新增业务功能、修改后端 API、改变会议工作流、引入新的交互范式。

---

## 1. 现状结论

当前前端的问题，不是某一个组件“长得丑”，而是整套视觉系统还没有真正收口。

- 颜色系统偏散，主色、状态色、证据色的职责不够清楚。
- 页面里卡片太多，边框、阴影、圆角同时出现，视觉层级发虚。
- 会议工作台、知识库、运维页都在用同一种后台模板语言，缺少主次。
- 标题、说明、元信息、状态标签的字号和权重差距不够大。
- 长内容场景很多，但列表、转写、问答、行动项的排版规则还不够稳定。
- 暗色模式存在，但还没有形成和浅色模式同样完整的语义表达。

所以这次重构的重点，不是做“更花哨的 UI”，而是做“更像一个可信工作台”的 UI。

---

## 2. 重构目标

1. 建立统一的视觉语言，让所有页面看起来属于同一套系统。
2. 强化信息层级，让用户第一眼知道哪里是主工作区、哪里是证据、哪里是状态。
3. 降低卡片感，改成更克制的工作台式布局。
4. 让颜色服务于语义，而不是服务于装饰。
5. 保证长文本、长列表、长转写在桌面宽度下稳定可读。
6. 保留现有交互流程，只升级视觉和布局，不改业务逻辑。

---

## 3. 视觉总原则

### 3.1 风格定位

整体风格定义为：**证据工作台（Evidence Workbench）**。

- 不是营销页。
- 不是产品官网。
- 不是花哨的插画式后台。
- 是一套偏专业、偏克制、偏高信息密度的审阅界面。

### 3.2 视觉准则

- 主色只负责“行动”。
- 证据色只负责“引用和来源”。
- 状态色只负责“成功、警告、失败”。
- 页面背景负责托住内容，不参与抢戏。
- 卡片只在需要被独立识别的区域使用。
- 不使用渐变 orb、发光背景、装饰性插画。
- 不让任何文本溢出按钮、标签、卡片和面板。

---

## 4. 视觉系统

### 4.1 色彩系统

建议把颜色分成 4 组：页面与表面、品牌动作、证据引用、状态语义。

| 语义 | 浅色模式 | 深色模式 | 用途 |
|---|---|---|---|
| 页面背景 | `#F5F7FB` | `#0B1220` | 页面最底层背景 |
| 主表面 | `#FFFFFF` | `#111827` | 卡片、面板、弹层 |
| 次表面 | `#F8FAFC` | `#172033` | 侧栏、分区底色 |
| 分割线 | `#D9E2EC` | `#243244` | 边框、列表分隔 |
| 主文字 | `#0F172A` | `#E5EEF9` | 标题和正文 |
| 次文字 | `#475569` | `#AAB8C8` | 说明、元信息 |
| 主品牌蓝 | `#2457F5` | `#6BA4FF` | 主按钮、导航激活、关键链接 |
| 证据青绿 | `#0F766E` | `#2DD4BF` | citation、来源、证据标签 |
| 成功绿 | `#15803D` | `#4ADE80` | 已确认、完成 |
| 警告橙 | `#B45309` | `#FBBF24` | 待处理、风险提醒 |
| 错误红 | `#C2410C` | `#F87171` | 失败、驳回、危险操作 |

规则：

- 品牌蓝不要覆盖所有状态。
- citation 和 evidence 必须和品牌蓝区分开，优先使用青绿。
- 同一页面上尽量只出现 1 个主要强调色和 1 个辅助强调色。
- 背景不要再叠加复杂渐变。

### 4.2 字体与排版

建议继续使用无衬线字体体系，但把层级拉开。

推荐字体栈：

```css
Inter, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
ui-sans-serif, system-ui, sans-serif
```

字号建议：

- 页面标题：28px 到 32px，字重 600
- 区块标题：18px 到 20px，字重 600
- 卡片标题：14px 到 16px，字重 600
- 正文：14px 到 15px，字重 400
- 元信息：12px 到 13px，字重 400

排版规则：

- 标题行高略紧，正文行高略松。
- 时间戳、数量、状态码等数字用等宽数字显示优先。
- 中文正文不要追求过宽的行长，长内容区控制在更易扫读的宽度。

### 4.3 间距、圆角、阴影

建议统一到 8px 网格。

- 页面外边距：移动端 16px，桌面端 24px 到 32px
- 区块间距：16px 到 24px
- 卡片内边距：16px 到 20px
- 圆角：按钮和标签 6px 到 8px，面板 8px 到 10px
- 阴影：只给一级表面，二级内容尽量只用边框

规则：

- 不再让每个子块都像“浮起来的卡片”。
- 主要分层靠背景、边框和留白，不靠重阴影。

### 4.4 状态与图标

- 图标只辅助理解，不替代文字。
- 状态标签固定短、统一、可扫描。
- 成功、警告、失败、进行中四类状态保持同一套视觉规则。
- 空状态和错误状态要有明确的语义，不要只给灰字。

---

## 5. 页面级布局策略

### 5.1 全局壳

全局壳的目标是先把“像一个系统”这件事做出来。

- 顶部栏稳定在 64px 左右。
- 左侧导航保持固定宽度，建议 288px 到 304px。
- 主内容区保持足够宽度，桌面端尽量别超过 1600px 后再继续放大。
- 页面背景统一，内容区使用同一套表面和分割线规则。
- 移动端侧栏用抽屉，不把布局逻辑改成另一套风格。

### 5.2 会议工作台

这是最重要的主页面，必须作为视觉基准。

建议结构：

- 顶部：会议标题、状态、时间、语言、处理概况。
- 中部左侧：转写主区，强调时间轴和证据阅读。
- 中部右侧：洞察、问答、处理任务三个信息域。
- 底部或侧边：审阅动作和发布动作。

规则：

- transcript 是主内容，不要被右侧面板抢戏。
- citation 高亮只做清晰提示，不做夸张动效。
- 右侧面板可以有轻分区，但不要再套一层层卡片。
- tabs 只负责切换内容，不负责制造视觉存在感。

### 5.3 知识库页

知识库页应该更像搜索结果页，而不是四分之一屏幕的卡片拼贴。

- 主区优先展示搜索结果列表。
- 右侧放历史决策和重复行动项提示。
- 结果项更适合列表化和条目化，不需要强卡片阴影。

### 5.4 运维页

运维页建议走更偏表格和矩阵的语言。

- provider 配置用状态行展示。
- 调用观测用统计条和行列表展示。
- 任务同步用简洁状态面板展示。
- 避免把所有指标都做成同等权重的方卡片。

---

## 6. 分阶段实施方案

### Phase 0：视觉基线和设计 token

目标：先统一底层语义，再改页面。

范围：

- `apps/web/app/globals.css`
- `apps/web/components/ui/button.tsx`
- `apps/web/components/ui/card.tsx`
- `apps/web/components/ui/badge.tsx`
- `apps/web/components/ui/input.tsx`
- `apps/web/components/ui/select.tsx`
- `apps/web/components/ui/tabs.tsx`
- `apps/web/components/ui/skeleton.tsx`
- `apps/web/components/ui/scroll-area.tsx`
- `apps/web/components/theme-toggle.tsx`
- `apps/web/lib/constants.ts`

交付物：

- 统一的浅色和深色语义 token。
- 卡片、按钮、输入框、标签、tabs 的基础样式收口。
- 页面背景、表面、分割线、文字层级统一。
- 证据色和品牌色区分清楚。

验收：

- 全站不再直接依赖零散的硬编码颜色。
- 基础组件在浅色和深色下看起来同属一套系统。
- 不出现明显的圆角、阴影、边框风格冲突。

验证：

- `pnpm --filter @meetmind/web lint`
- `pnpm --filter @meetmind/web typecheck`

### Phase 1：壳层和导航

目标：把首页壳子先做稳。

范围：

- `apps/web/components/layout/app-shell.tsx`
- `apps/web/components/layout/app-header.tsx`
- `apps/web/components/layout/app-sidebar.tsx`
- `apps/web/app/layout.tsx`

交付物：

- 更稳定的顶部栏和侧边栏布局。
- 左侧导航、上传入口、刷新按钮统一视觉语言。
- 移动端抽屉和桌面端固定栏一致。
- 让首页第一屏就有“工作台”的感觉。

验收：

- 桌面端和移动端都能保持一致的导航语义。
- 侧栏不再像另一个独立页面。
- 头部品牌区、证据提示、操作按钮层级清楚。

验证：

- `pnpm --filter @meetmind/web lint`
- `pnpm --filter @meetmind/web typecheck`

### Phase 2：会议工作台主屏

目标：把最重要的会议详情页打成整套 UI 的主样板。

范围：

- `apps/web/features/meetings/meeting-workbench.tsx`
- `apps/web/features/meetings/components/meeting-detail/meeting-detail.tsx`
- `apps/web/features/meetings/components/meeting-detail/meeting-header.tsx`
- `apps/web/features/meetings/components/transcript/transcript-panel.tsx`
- `apps/web/features/meetings/components/transcript/transcript-segment.tsx`
- `apps/web/features/meetings/components/transcript/section-nav.tsx`
- `apps/web/features/meetings/components/insights/*`
- `apps/web/features/meetings/components/qa/*`
- `apps/web/features/meetings/components/jobs/*`
- `apps/web/features/meetings/components/meeting-list/*`

交付物：

- 会议详情页成为最完整、最精致的页面。
- transcript 采用清晰的时间轴和证据高亮。
- 右侧信息域更像审阅面板，而不是堆叠卡片。
- action item、decision、risk、question 的层级明显。

验收：

- 在 1440px 宽度下，用户能快速看出主工作区和辅助区。
- 文字不会挤压、折行混乱或互相遮挡。
- citation、状态、按钮、tabs 有统一的视觉规则。

验证：

- `pnpm --filter @meetmind/web test`
- `pnpm --filter @meetmind/web lint`
- `pnpm --filter @meetmind/web typecheck`

### Phase 3：知识库、行动项、运维页

目标：让其他页面跟上主页面的视觉标准。

范围：

- `apps/web/features/meetings/components/knowledge/knowledge-overview.tsx`
- `apps/web/features/meetings/components/action-items/action-items-overview.tsx`
- `apps/web/features/meetings/components/operations/operations-overview.tsx`
- `apps/web/features/meetings/components/shared/status-badge.tsx`
- `apps/web/features/meetings/components/shared/status-note.tsx`
- `apps/web/features/meetings/components/shared/panel-state.tsx`

交付物：

- 知识库页更像搜索和结果页。
- 行动项页更像管理页，不再像普通列表卡片。
- 运维页更像可扫描的状态面板。
- 所有次级页面共享同一套表面、分割线和状态表达。

验收：

- 各页面风格一致，不再出现明显的一页一套风格。
- 空状态、加载态、错误态统一。
- 状态标签可读、稳定、不抢内容。

验证：

- `pnpm --filter @meetmind/web test`
- `pnpm --filter @meetmind/web build`

### Phase 4：收尾、回归和稳定性

目标：把重构做成可长期维护的系统，而不是一次性美化。

范围：

- `apps/web/features/meetings/design-*.test.ts`
- `apps/web/features/meetings/view-model.test.ts`
- `apps/web/features/meetings/api.test.ts`
- 需要时补充视觉回归断言

交付物：

- 关键 token、布局和语义类名被测试锁住。
- 长文本、空状态、错误状态、深色模式完成回归检查。
- 基础可访问性问题清理完成。

验收：

- 不再出现明显的文本溢出、卡片错位或密度失衡。
- 深色模式和浅色模式都能保持一致的阅读体验。
- 关键页面在桌面常见宽度下稳定。

验证：

- `pnpm --filter @meetmind/web lint`
- `pnpm --filter @meetmind/web typecheck`
- `pnpm --filter @meetmind/web test`
- `pnpm --filter @meetmind/web build`

---

## 7. 风险与约束

### 7.1 风险

- 仅改视觉不改结构，可能出现“看起来好了，但局部仍旧乱”的情况。
- 长转写内容和复杂问答内容容易在新布局里溢出。
- 深色模式如果 token 不统一，最容易暴露层级问题。
- 如果每个页面继续单独写局部样式，统一性会再次被打散。

### 7.2 约束

- 不扩交互，不加新流程。
- 不把页面重构成营销式视觉。
- 不引入新的大体量依赖。
- 不让 UI 改造反过来影响现有数据结构和 API。

---

## 8. 最终验收标准

UI 重构完成后，应该满足下面这些标准：

- 页面一眼能看出是会议工作台，不是通用后台模板。
- 颜色有明确语义，品牌、证据、状态职责分明。
- 会议详情页成为全站最强的视觉基准页。
- transcript、citation、action item、QA 的层级清楚，长内容可稳定阅读。
- 知识库和运维页与主页面风格一致。
- 浅色和深色模式都能保持统一的阅读体验。
- 关键页面没有明显文本溢出、拥挤、遮挡和层级失控。

---

## 9. 执行顺序建议

建议按这个顺序推进：

1. 先做 Phase 0，把 token 和基础组件统一。
2. 再做 Phase 1，把壳层和导航稳住。
3. 然后做 Phase 2，把会议工作台打成样板。
4. 再推进 Phase 3，把次级页面收口。
5. 最后做 Phase 4，把回归和稳定性补齐。

这条顺序的好处很简单：先统一底层，再统一页面，最后统一体验。

---
id: cu-web-state-snapshot-replay
section: computer-use
order: 8
level: A
title: 网页 Agent 如何做状态快照与失败复现？
quick: "分层存快照：URL、DOM/a11y 摘要、关键网络响应、cookie 分区和带时间戳的动作序列。复现先用固定网络响应与时钟的 mock，再考虑受控实网，并找出第一个和录制分叉的步骤。截图存不下节点身份、登录态和网络状态，只能当附件。"
tags:
  - Reproducibility
  - Web Agent
  - Snapshot
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: WebArena
    url: https://arxiv.org/abs/2307.13854
    type: primary
  - title: Playwright Trace Viewer
    url: https://playwright.dev/docs/trace-viewer
    type: primary
---

网页 Agent 的快照要分层存结构和网络，复现先在 mock 上逐步对齐 I/O，找到第一个分叉的步骤。只存一张失败截图几乎复现不了：页面改版、登录态、A/B、异步请求和 cookie 分区，都会让「同一个 URL」变成另一个状态。

比如线上报「Agent 偶尔点错按钮」。手里只有截图的话，同样的像素可能对应不同的节点，你回答不了「点的是哪个 role」，也分不清是 grounding 漂了还是页面变了。WebArena 一类基准能比较，是因为站点和 fixture 被冻住了；Playwright trace 能逐步对齐，是因为它记了 DOM、网络和动作时间线，不只是像素。这题讲怎么保存单次失败的状态并重放，整条 benchmark run 的版本包见 `cu-reproducible-benchmark-run`。

## 快照分三层

轻量层存 URL、viewport、locale、无障碍信息 / DOM 摘要 hash、可见控件名单。中量层存完整 DOM 或 accessibility tree、关键网络响应哈希、cookie 分区标识、localStorage 里的非秘密键。重量层是浏览器上下文导出和容器镜像 digest。动作序列和每步的 observation 都要绑时间戳。树摘要和截图都要留，DOM 和视觉怎么融合定位见 `cu-dom-a11y-visual-grounding`。

重量快照成本高，我会按失败率抽样：所有失败都留轻量层，归因不明再升到中量。不必给每次成功的 run 都存全量 DOM。

cookie 值、认证 token 和个人身份信息（PII）默认脱敏，用 hash 关联，全文放受控存储。验证码、真人审核、没法 mock 的第三方支付标成 `non_replayable`，别假装能复现。

## Replay 先 mock，再谈实网

复现的优先级是 deterministic mock（录制的网络与时钟）$\gt$ 受控预发 $\gt$ 真实站点。重放时对齐同一个 seed、同一个冻结时间、同一个 cookie 分区，逐步断言 I/O。时钟和随机源写进同一份 replay 合同：只冻模型 seed、不冻 `Date.now()`，邮件类任务的状态照样会变。

分叉点 $t^*$ 定义为第一个 observation hash 或网络响应和夹具对不上的步骤，它之后的模型动作就别再当根因了。Playwright 的 trace 把 DOM 快照、网络和动作放在同一条时间线上，正好用来回答「哪一步 DOM 已经和录制分叉」，适合做中量复现，不过 cookie 分区和 mock 版本号它替代不了，还得自己记。如果分叉率 $\rho \gt \rho_{\max}$，先修夹具再比策略，否则两个模型没有共同的环境可比。

新策略也可以放到同一个快照上重放，看两种策略从哪一步开始不同：旧策略在 $t$ 点了 A，新策略点了 B。这是评测回归，和演示录像是两回事。

会让评测结果虚高的做法有：在不断变化的生产站点上反复调到任务成功再截图、不标 `non_replayable`、把环境分叉算成模型退步、快照含秘密却进了通用日志。报告里附上快照层级、mock 版本、分叉步、能不能复现。能逐步对齐 I/O 才叫复现，截图只是附件。现场被问「线上偶现点错」，我会先问有没有中量快照和分叉点，再考虑要不要重训模型。

## 追问

**为什么纯截图不够？**
缺 DOM 身份、网络副作用和登录态，像素相同也可能是另一个节点。

**验证码怎么办？**
标成不可复现，交给人工处理。强行 live 重放，评测就变成拼运气。

**cookie 怎么存？**
分区标识和 hash 进日志，值脱敏；复现用预置 fixture，别复制生产会话。

**和 `cu-reproducible-benchmark-run` 怎么分？**
那题是发布一条可比 run 的版本包，这题是单次失败的状态夹具和分叉定位。

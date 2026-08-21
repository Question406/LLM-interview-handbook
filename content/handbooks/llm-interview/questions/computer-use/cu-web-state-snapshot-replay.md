---
id: cu-web-state-snapshot-replay
section: computer-use
order: 8
level: A
title: 网页 Agent 如何做状态快照与失败复现？
quick: 记录 URL、DOM/a11y 摘要、关键网络响应、cookies 分区与动作序列；复现时优先 deterministic mock，其次受控实网。纯截图不够。
tags:
  - Reproducibility
  - Web Agent
  - Snapshot
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: WebArena
    url: https://arxiv.org/abs/2307.13854
    type: primary
  - title: Playwright Trace Viewer
    url: https://playwright.dev/docs/trace-viewer
    type: primary
---

只存一张失败截图，几乎无法复现网页 Agent。页面改版、登录态、A/B、异步请求和 cookie 分区都会让「同一 URL」变成另一个状态。面试陷阱是把截图当快照，或把 live 站点重放当成可回归评测。WebArena 一类基准能比较，是因为站点与 fixture 被冻结；Playwright trace 能逐步对齐，是因为记录了 DOM、网络与动作时间线，而不只是像素。本题讲单次失败怎么拍状态、怎么重放；整条 benchmark run 的版本包见 `cu-reproducible-benchmark-run`。

## 快照要分层，像素只是一层

轻量：URL、viewport、locale、a11y / DOM 摘要 hash、可见控件名单。中量：完整 DOM 或 accessibility tree、关键网络响应哈希、cookie 分区标识、localStorage 中的非秘密键。重量：浏览器上下文导出、容器镜像 digest。动作序列与每步 observation 必须绑定时间戳。纯截图缺结构：同像素可能对应不同节点，也无法回答「点的是哪个 role」。DOM 与视觉的融合定位见 `cu-dom-a11y-visual-grounding`；快照里应同时留树摘要和截图，否则复现时无法判断是 grounding 漂了还是页面变了。隐私上默认脱敏 cookie 值、token、PII；用 hash 关联，全文放受控存储。验证码、真人审核、不可 mock 的第三方支付标成 `non_replayable`，不要假装能复现。

## Replay：先 mock，再谈实网

复现优先级：deterministic mock（录制的网络与时钟）$\gt$ 受控预发 $\gt$ 真实站点。Replay 对齐：同一 seed、同一时间冻结、同一 cookie 分区、逐步断言 I/O。Playwright trace 一类时间线可以回答「哪一步 DOM 已经与录制分叉」。分叉点 $t^*$ 定义为第一个 observation hash 或网络响应与夹具不一致的步骤；其后的模型动作不要再当根因。新策略在同一快照上重放，用来找 divergence：旧策略在 $t$ 点 A，新策略点 B。这是评测回归，不是演示录像。

可被刷的点：对着会变的生产站点调绿再截图；不标 `non_replayable`；把环境分叉算成模型退步；快照含秘密却进通用日志。报告附：快照层级、mock 版本、分叉步、是否可复现。面试口径：能逐步对齐 I/O 的快照才叫复现；截图是附件。WebArena 冻结的是整站 fixture；你的产品调试至少要冻结到网络夹具和 DOM hash。现场被问「线上偶现点错」时，先问有没有中量快照和分叉点，而不是先重训模型。

重量快照成本高，按失败率抽样：所有失败留轻量，归因不明再升级中量。不要默认对每次成功 run 存全量 DOM。时钟与随机源写进同一份 replay 合同；只冻模型 seed、不冻 `Date.now()`，邮件类任务仍会漂。Playwright 的 trace 把 DOM 快照、网络和动作放在同一时间线上，适合做中量复现；它仍然替代不了 cookie 分区与 mock 版本号。若分叉率 $\rho \gt \rho_{\max}$，先修夹具再比策略，否则模型对比没有共同环境。

## 追问

- **为什么纯截图不够？** 缺 DOM 身份、网络副作用和登录态；像素相同也可能是另一个节点。
- **和 `cu-reproducible-benchmark-run`？** 那题是发布一条可比 run 的版本包；本题是单次失败的状态夹具与分叉定位。
- **验证码怎么办？** 标不可复现并人工；强行 live 重放会把评测变成运气。
- **cookie 怎么存？** 分区标识与 hash 进日志，值脱敏；复现用预置 fixture，不要复制生产会话。

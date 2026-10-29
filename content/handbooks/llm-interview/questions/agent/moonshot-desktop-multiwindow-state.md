---
id: moonshot-desktop-multiwindow-state
section: agent
order: 104
level: A
title: 月之暗面：桌面端多窗口协作时，如何避免 Agent 状态冲突？
quick: >-
  任务状态只放在主进程或服务端的一个权威 store 里，窗口只发意图、显示投影，用版本号或操作日志同步。每次更新带上读取时的 base
  revision，store 做 compare-and-swap，冲突时合并或请用户选，计划和权限宁可展示冲突。会产生副作用的动作还要检查 lease、带
  idempotency key，并定义好取消后的处理。
tags:
  - Moonshot AI
  - AI-Native
  - Multi-Agent
  - Concurrency
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 月之暗面 Desktop 研发工程师面经（候选人原帖）
    url: >-
      https://www.nowcoder.com/feed/main/detail/09158c1da13b420bbe00ba1751177efb?urlSource=sitemap
    type: candidate-first-hand
---

## 真题记录

- 公司：月之暗面（Moonshot AI）
- 团队 / 岗位：研发工程师（AI-Native 方向）
- 届别 / 流程：原帖未披露；二面
- 面试时间：2026-07-23；帖子发布于 2026-07-30
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、轮次与面试日期明确，届别未披露）
- 原始措辞：**“如果桌面端支持多窗口协作，前端怎么避免不同窗口状态打架？”**

避免打架的办法是只留一份任务真相：Task、步骤、产物、审批、权限都放在主进程或服务端的单一权威 store 里，窗口只发意图、显示投影。选中项、滚动位置这种展示状态可以留在窗口本地。写入带版本号做 compare-and-swap，副作用靠 lease 和 idempotency key 保证只执行一次。同步管的是大家看见的一致，lease 管的是副作用只执行一次，这两件事要分开答。

最危险的情况是两个窗口同时点「运行」。如果每个窗口都是独立 SPA，各持一份 React 状态，靠最后写入获胜，那就可能发起两次工具调用、写两遍文件。这是副作用冲突，比文案不同步严重得多。

写入这边，每个更新携带 `baseRevision`。存储端做 compare-and-swap：版本匹配就接受并递增，不匹配就拒绝，或者按字段、按 operation 合并，再向各窗口广播有序的变更。文本草稿可以用 CRDT / OT 或字段级 merge；执行计划和权限决策宁可展示冲突，也不要静默合并，否则一个窗口撤销了读取、另一个窗口批准了删除，合出来的结果没人解释得了。断线重连时按事件序列补齐，不允许用陈旧的内存快照覆盖新状态。前端可以乐观更新，但必须能回滚到 store 的权威版本。

Desktop 主进程是协调者。窗口只发 intent（编辑字段、请求运行、请求取消），主进程做 CAS 和租约，再把结果投影回 UI。这样关窗、崩溃、重开都不会丢已经执行过的步骤，也不会让旧草稿覆盖已批准的计划。月之暗面这道二面题和任务中心是同一个设计，UI 只是可审计状态的投影，见 `moonshot-desktop-task-center`。

副作用这边，多个窗口都点运行时，只有持有 task lease 的 worker 能发起工具调用。每个外部请求带 idempotency key；暂停和取消写成持久的状态转换，所有窗口看到的是同一个状态机，不会各自显示一套「进行中」。lease 过期要有续约和抢占规则，免得死租约卡住任务。Agent 重试、分支、关窗口，都不能让副作用执行两次；写本地文件或外发之前，先看 lease 和授权版本。evidence 和文件授权也是任务状态的一部分，窗口 A 缩小了权限，窗口 B 就不能再拿旧的 capability 读盘，见 `moonshot-desktop-local-file-permission`。上下文证据包也以 store 里的 manifest 为准，避免两个窗口把不同的网页快照送进同一次模型调用，见 `moonshot-desktop-multimodal-context`。

所以被问「怎么避免打架」，我会先讲权威 store 和副作用分离，再谈 CRDT。多数 Agent 状态不适合无冲突复制。

## 追问

**计划冲突为什么不自动 merge？**
步骤顺序和权限都是决策，静默合并会得到一个没人确认过的计划。应该弹冲突 UI，或者让一方放弃。

**一个窗口离线编辑怎么办？**
本地把 operation 排队，上线后按 base revision 重放；重放失败就提示分叉，不要覆盖线上已经执行的步骤。

**两个 Agent 各管一个窗口行不行？**
可以，但必须共享同一个 Task store 和 lease。各用各的，就成了两个任务，谈不上多窗口协作。

**前端只用 WebSocket 推送够不够？**
推送只是投影。没有 CAS 和事件日志，乱序和重连时照样会打架。

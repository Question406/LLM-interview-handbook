---
id: moonshot-desktop-multiwindow-state
section: agent
order: 104
level: A
title: 月之暗面：桌面端多窗口协作时，如何避免 Agent 状态冲突？
quick: >-
  任务状态统一保存在主进程或服务端的 store 中，用版本号或操作日志同步各窗口。每次更新携带读取时的 base revision，由
  存储端检查版本，发现冲突时合并或请用户选择。执行会产生副作用的动作时，还要检查 lease、使用幂等键，并定义取消后的处理方式。
tags:
  - Moonshot AI
  - AI-Native
  - Multi-Agent
  - Concurrency
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 月之暗面 Desktop 研发工程师面经（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/09158c1da13b420bbe00ba1751177efb?urlSource=sitemap
    type: candidate-first-hand
---

## 真题记录

- 公司：月之暗面（Moonshot AI）
- 团队 / 岗位：研发工程师（AI-Native 方向）
- 届别 / 流程：原帖未披露；二面
- 面试时间：2026-07-23；帖子发布于 2026-07-30
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、轮次与面试日期明确，届别未披露）
- 原始措辞：**“如果桌面端支持多窗口协作，前端怎么避免不同窗口状态打架？”**

常见误区是：把每个窗口当独立 SPA，靠最后写入覆盖。桌面多窗口协作要先区分展示状态和任务真相。选中项、滚动位置可以窗口本地；Task、步骤、产物、审批、权限必须落在主进程或服务端的单一权威 store。月之暗面二面和任务中心是同一设计：UI 只是可审计状态的投影，见 `moonshot-desktop-task-center`。更危险的是两个窗口同时点「运行」，那是副作用冲突，不是文案不同步。

## 权威 store + 带版本的写入

每个更新携带 `baseRevision`。存储端 compare-and-swap：版本匹配则接受并递增，不匹配则拒绝或按字段 / operation 合并，再向各窗口广播有序变更。文本草稿可用 CRDT / OT 或字段级 merge；执行计划和权限决策宁可展示冲突，也不要静默合并，否则一个窗口撤销读取、另一个窗口已批准删除，合并结果无法解释。

断连重连从事件序列补齐，禁止用陈旧内存快照覆盖新状态。前端乐观更新可以，但必须能回滚到 store 的权威版本。evidence 与文件授权也是任务状态的一部分，窗口 A 缩小权限后，窗口 B 不能继续拿旧 capability 读盘，见 `moonshot-desktop-local-file-permission`。

## 副作用用 lease 和幂等，不靠「谁先点」

多窗口都点运行时，只允许持有 task lease 的 worker 发起工具调用。每个外部请求带 idempotency key；暂停 / 取消写成持久状态转换，其他窗口看到的是同一状态机，而不是各自一套「进行中」。lease 过期要可续约和抢占规则，避免死租约卡住任务。

Agent 重试、分支、关窗口都不能让副作用执行两次。写本地文件或外发前看 lease + 授权版本。上下文证据包也以 store 里的 manifest 为准，避免两窗口把不同网页快照送进同一次模型调用，见 `moonshot-desktop-multimodal-context`。同步管看见的一致，lease 管副作用只执行一次。前端常见误区是把 React 状态当真相，多窗口各持一份再「最后写入获胜」。Desktop 主进程才是协调者：窗口只发 intent（编辑字段、请求运行、请求取消），主进程做 CAS 和租约，再投影回 UI。关窗、崩溃、重开都不会丢已执行步骤，也不会用旧草稿覆盖已批准的计划。二面问「怎么避免打架」，先答权威 store 与副作用分离，再谈 CRDT；多数 Agent 状态不适合无冲突复制。

## 追问

- **为什么计划冲突不要自动 merge？** 步骤顺序和权限是决策，静默合并会得到没人确认过的计划。应冲突 UI 或一方放弃。
- **一个窗口离线编辑怎么办？** 本地排队 operation，上线后按 base revision 重放；失败则提示分叉，不要覆盖线上已执行步骤。
- **两个 Agent 各管一个窗口行不行？** 可以，但必须共享同一 Task store 和 lease；否则是两个任务，不是多窗口协作。
- **前端只用 WebSocket 推送够不够？** 推送是投影。没有 CAS / 事件日志，乱序和重连仍会打架。

---
id: arl-checkpoint
section: agentrl
order: 14
level: A
title: Agent State Checkpoint / Restore 怎么做？
quick: >-
  快照要同时保存 Agent 的逻辑状态和外部环境状态：任务进度、记忆与上下文摘要、工具结果，
  以及未完成事务、文件系统或容器快照、外部资源句柄，
  还要记录策略和 Harness 版本。
tags:
  - Agent State
  - Reliability
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: LangGraph Persistence
    url: https://langchain-ai.github.io/langgraph/concepts/persistence/
    type: primary
---

只把对话文本存下来不够。恢复后文件系统已变、网页 session 过期、事务状态未知，Agent 会根据已经过时的状态继续执行。看起来像「接着聊」，其实 MDP 已经换了。常见误区是：把 checkpoint 当成 chatbot 的 session 序列化。生产 Agent 的持久化（如 LangGraph thread checkpoint）存的是图状态与通道，不是聊天记录副本。

## 同时保存逻辑状态和外部环境

一次可恢复的快照至少覆盖两类东西：

- **逻辑 Agent 状态：** 任务目标与约束、当前 plan / 子目标、memory 或 context summary、已确认的 tool 结果、待澄清问题、策略与 harness 版本。
- **外部世界句柄：** 工作目录或容器 snapshot、浏览器 cookie / tab、数据库事务或订单 ID、打开的文件锁、未完成的异步 job。

缺任何一类，restore 后 观测结果（observation） 和真实世界会对不齐。版本也要入快照：模型、工具 字段和类型规范（schema）、提示、权限集一变，旧轨迹里的 action 可能不再合法。这和 `arl-environment-reset` 同一假设：没有定义清楚的 $s_t$，后续奖励没有意义。

## 三类状态，恢复策略不同

把字段分成三类，不要一套「整包 pickle」了事：

- **可回放的纯观察：** 已拉取的检索结果、只读 API 回包。可以存原文或内容哈希，恢复时直接喂回上下文。
- **版本化产物：** 代码 diff、生成文件、中间表格。存对象存储 + 内容哈希，恢复时 checkout 到同一 commit / 目录树。
- **不可逆副作用：** 已发邮件、已扣款、已删数据。不能靠「再执行一遍」恢复。必须记录 durable transaction ID，恢复后重新 query 真相，而不是相信内存里的「我发过了」。

超时后不知道写操作有没有落地，属于第三类：下一跳是查单，不是 replay，见 `arl-retry`。Checkpoint 里应留下 `UNKNOWN_SIDE_EFFECT` 和查询句柄，否则恢复进程会双发。

## 恢复时先核对环境，再继续策略执行

Restore 顺序建议：加载 harness 版本 → 恢复文件系统 / 容器 → 用事务 ID 刷新外部真相 → 校验逻辑状态与观察是否一致 → 才允许策略继续生成。不一致就停：标 dirty，不要让模型「猜世界还是不是那样」。长任务还要能从任意 tool 边界恢复，而不是只在用户回合存一次。崩溃往往发生在工具执行中。评测应注入：恢复后目录哈希变了、session 过期、事务其实已成功。看 Agent 是查状态还是盲目接着点。

Checkpoint 存的是 $(s_t, \text{handles}, \text{versions})$，不是聊天日志。可回放的存哈希，不可逆的存事务 ID 并重查；对不齐就标 dirty，禁止根据不一致的状态继续优化。

## 追问

- **只存 conversation 为什么会出现数值异常？** 文本说「文件已写」，磁盘上没有或写的是另一份，后续动作会改错对象。逻辑与世界必须一起恢复。
- **训练中要不要 checkpoint？** 长 horizon 采样轨迹（rollout） 崩溃重跑很贵，可在 tool 边界做可恢复快照；但脏恢复的轨迹应丢弃，不要当 on-policy 样本。
- **和 reset 的差别？** Reset 定义 $p(s_0)$，checkpoint 保存任意 $s_t$。两者都要能断言世界哈希；一个用于开局，一个用于续跑。
- **多 Agent 怎么存？** 共享黑板只存已验证字段，各自 scratch 分开。恢复后先对齐共享状态版本，再让工人继续，见 `arl-multiagent`。

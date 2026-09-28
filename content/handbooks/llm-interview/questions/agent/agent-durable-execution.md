---
id: agent-durable-execution
section: agent
order: 210
level: S
title: Agent 的 Durable Execution 要持久化什么，才能在进程崩溃后安全续跑？
quick: 我会持久化工作流状态、已提交副作用的幂等键、待审批门闩和外部真源指针。纯对话文本不够。恢复时先 reconcile 外部状态，再决定续跑。
tags:
  - Durable Execution
  - Reliability
  - Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Temporal — Understanding Temporal (durable execution)
    url: https://docs.temporal.io/evaluate/understanding-temporal
    type: primary
---

错法：把 checkpoint 当成聊天记录序列化，进程重启后「接着聊」。对话文本没记工具有没有落地、审批卡在哪、订单号是什么。崩溃后再生成一步，支付会双花，邮件会重发。Temporal 把工作流做成可重放的事件历史：输入、决策、Activity 请求与结果、定时器、人工门闩都是持久事件。Worker 挂了，用历史 replay 到崩溃点再往下走，不是加载一段散文。

## 必须落盘的不是台词，是事件与句柄

一次可续跑的 Agent 工作流至少持久化：

- 工作流身份与版本：run id、harness / 模型 / tool schema 版本。代码升级后，旧 in-flight 流程要能排空或走兼容窗口，不能用新分支偷偷 replay 旧历史。
- 确定性事件：用户输入、计划断言、工具调用的请求与已确认结果、人工审批通过/拒绝。模型的 Thought 可以摘要，但不能当唯一真相。
- 副作用的幂等键与外部真源指针：订单 id、转账流水、已发邮件的 provider message id。存「我创建过订单」不够，要能 query 外部系统。
- 待审批门闩：谁在等、超时策略、break-glass 记录。恢复后不能把未批准的写操作当成已完成。

工程目标是至少一次执行加去重：Activity 可能重试，但同一 `idempotency_key` 只落地一次。严格 exactly-once 在分布式里几乎做不到；效果上的 once 靠幂等接口加持久去重表。超时后下一跳是查单，不是 replay 那次写调用，见 `arl-retry`。

## 恢复协议：先对世界，再决定是否续跑或 re-plan

恢复顺序：加载事件历史与版本 → 用事务 id 刷新外部真相 → 跳过已完成副作用 → 校验逻辑状态与观察是否一致 → 才允许策略继续。不一致就标 dirty，禁止在错误世界上接着点。外部已经变了（库存没了、权限被收、页面改版）时，应触发 `agent-when-to-replan` 的闸门，别死守崩溃前那张步骤表。

这和 `arl-checkpoint` 要分开。那题是 Agent 状态快照：把 $(s_t, \text{handles}, \text{versions})$ 钉住，供 RL / 仿真在 tool 边界恢复，脏恢复的轨迹应丢弃。本题是生产工作流耐久性：事件溯源、Activity 重试、审批门闩、版本化 workflow code。训练里一份脏 $s_t$ 会污染梯度；生产里一份脏事件会双花真钱。两者都要外部真源，但持久化对象不同：一个是 MDP 状态，一个是业务事件日志。

评测应注入：进程在写操作超时后被杀、恢复时订单其实已成功、schema 已升到 v2。看系统是查状态并跳过，还是再扣一次款。

## 追问

- **和 `arl-checkpoint` 重复吗？** 不重复。那题钉的是训练/仿真里的 $s_t$；本题钉的是生产事件历史与副作用去重。都要查外部真相，对象不同。
- **workflow 代码改了怎么办？** 版本化。旧 run 用旧代码排空，或显式 migration；禁止用新分支 replay 旧事件。
- **模型非确定性怎么 replay？** 决策结果必须作为事件写入历史；replay 时读已记录的工具结果，不要重新采样 Thought 当真相。
- **崩溃发生在工具执行中？** 当成未知副作用：用幂等键查终态。已成功则跳过，未成功才允许按原 Activity 重试。

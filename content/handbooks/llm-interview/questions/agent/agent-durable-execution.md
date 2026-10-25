---
id: agent-durable-execution
section: agent
order: 210
level: S
title: Agent 的 Durable Execution 要持久化什么，才能在进程崩溃后安全续跑？
quick: "要持久化的是工作流事件：状态、已提交写操作的幂等键、还没完成的审批，以及能去外部系统查记录的标识，光存对话文本不够。恢复时先拿这些标识核对外部状态，跳过已完成的副作用，再决定继续执行还是重新规划。"
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

我会持久化工作流的事件历史，再加上每个写操作的幂等键、还没完成的审批，以及能去外部系统查真实记录的标识。光把对话文本存下来不够。恢复时先核对外部状态，再决定是继续执行还是重新规划。

常见的做法是把 checkpoint 当成聊天记录序列化，进程重启后「接着聊」。可对话文本里没有记工具到底执行成功没有、审批走到了哪一步、订单号是多少。比如 agent 调了付款接口，还没收到返回进程就崩了，重启后模型看对话以为还没付，再生成一步，就重复付款了，发邮件也一样。

Temporal 的做法是把工作流做成可重放的事件历史：输入、决策、Activity 的请求和结果、定时器、人工门闩都是持久事件。Worker 崩溃后，系统按事件历史重放到崩溃点再继续。套到 Agent 上，要存的有四类东西。

先是工作流身份和版本：run id，以及 harness / 模型 / tool 字段和类型规范（schema）的版本。代码升级后，旧的 in-flight 流程要能排空或者走兼容窗口，不能拿新的代码分支去重放旧的事件历史。然后是确定性事件：用户输入、计划断言、工具调用的请求和已确认的结果、人工审批的通过或拒绝。模型的 Thought 可以摘要存，但不能当唯一真相。再就是副作用的幂等键和外部真源指针，比如订单 id、转账流水、已发邮件的 provider message id。只存「我创建过订单」不够，要能拿这个 id 去 query 外部系统。最后是待审批的门闩：谁在等、超时策略、break-glass 记录。恢复后不能把没批准的写操作当成已完成。

工程上的目标是至少一次执行加去重：Activity 可能重试，但同一个 `idempotency_key` 只落地一次。分布式系统里严格的 exactly-once 几乎做不到，效果上的「只执行一次」靠幂等接口加持久的去重表。所以写调用超时以后，下一步是去查单，别重放那次写调用，见 `arl-retry`。

恢复的顺序是：加载事件历史和版本，用事务 id 刷新外部真相，跳过已经完成的副作用，校验逻辑状态和观察是否一致，之后才让策略继续。对不上就标成 dirty、停下后续操作，免得根据过时的状态往下走。外部已经变了，比如库存没了、权限被收回、页面改版，就要走 `agent-when-to-replan` 的闸门，不能照搬崩溃前的计划。

评测可以注入几种情况：写操作超时后进程被杀、恢复时订单其实已经成功、schema 已经升到 v2。看系统是去查状态然后跳过，还是再扣一次款。

## 追问

**这和 `arl-checkpoint` 重复吗？**
不重复，持久化的对象不同。那题是 Agent 状态快照，把 $(s_t, \text{handles}, \text{versions})$ 钉住，供强化学习（RL）或仿真在 tool 边界恢复，脏恢复的轨迹直接丢掉。这题是生产工作流的耐久性：事件溯源、Activity 重试、审批门闩、版本化的 workflow code。训练里一份脏的 $s_t$ 会污染梯度，生产里一份脏事件会双花真钱。两边都要查外部真源，一个存的是 MDP 状态，一个存的是业务事件日志。

**workflow 代码改了怎么办？**
做版本化。旧 run 用旧代码排空，或者做显式 migration，禁止用新分支 replay 旧事件。

**模型是非确定性的，怎么 replay？**
决策结果必须作为事件写进历史。replay 时读已经记录的工具结果，不重新采样 Thought 当真相。

**崩溃正好发生在工具执行中间呢？**
当成未知副作用处理：用幂等键查终态，已经成功就跳过，确认没成功才按原来的 Activity 重试。

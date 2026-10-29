---
id: xiaohongshu-multitenant-limit
section: systems
order: 184
level: A
title: 小红书 Agent 一面：多员工同时用如何限流降级？多租户怎么理解？
quick: >-
  租户是配额、账单和 data isolation requirements，应用是租户内的产品与 SLO 档位。按租户、应用和必要的用户层分配
  QPS、并发与 token 预算，过载时先降并行和检索宽度，再换模型、限时排队，最后拒收。
tags:
  - Xiaohongshu
  - Rate Limit
  - Multi-tenant
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 小红书Ai agent算法一面 攒人品
    url: 'https://www.nowcoder.com/feed/main/detail/6819d2a74f00489ea3e3913a5139346a'
    type: candidate-first-hand
  - title: Kubernetes Resource Quotas
    url: 'https://kubernetes.io/docs/concepts/policy/resource-quotas/'
    type: primary
---

我会按租户和应用分别设配额，再在租户内保证员工之间公平。租户负责账号、数据权限、账单和资源隔离，应用是同一租户里的客服、创作、审核等 Agent / 工作流。比如一个员工开 50 个会话，应先受到用户与租户配额限制，不能耗尽共享 vLLM 的 KV，让同事和其他业务一起被拒绝。

员工 $\neq$ 租户。同一部门共享租户桶时，还需要用户级 weighted fair queue，防止单人挤占部门配额。限流键可以是 `tenant_id + app_id`，必要时加 `user_id`。数据上要隔离索引、对话和笔记权限；配额上也要防止创作 Agent 拖慢审核 Agent。审核、安全等关键路径可以设独立保活池，与尽力而为的闲聊区分。多租户因此还划分了失败影响范围，多个 API key 本身并不足够。

先按租户设令牌桶，再按应用设子桶，同时限制入站 QPS、在途并发和 token / 分钟，另有每日 token 预算。长上下文 Agent 常先碰到 token 预算，短问答更容易碰到并发；只设 QPS 挡不住 128k 上下文消耗。租户内的定时任务、评测回放和员工调试也会争资源，应放低优先级子桶，权重按 SLO 分配，避免挤掉在线会话。

过载时可以依次关闭多 Agent 并行、缩短检索 top-k、换小模型、只检索不生成，再限时排队，最后拒收并返回明确错误。关键应用禁止降到只检索。先拒收可能让用户立即重试，反过来加重压力；排队也必须有 deadline，避免队列长期占内存、消耗任务链剩余时间。

拒收或排队失败时返回明确的 429 / 错误和 retry-after，客户端需要尊重它并采用 backoff，不能再把请求丢回模型重试。写操作带 idempotency key，否则排队或重试成功两次就会双写。前端超时后自动重打，也可能瞬间打满租户桶。

看板按与限流相同的 `tenant_id + app_id` 分组，观察 p95、拒绝率、降级率和 token 消耗，记录使用了哪档模型、是否跳过检索，用户侧最好也能看到已降级。只看集群平均值或 p95，会掩盖某条业务线持续被挤占的情况。

## 追问

**为什么全局限流还不够？**
它不能保证租户和关键应用之间的公平。忙租户可能吃满资源，让其他租户和审核等关键业务一起收到 429。

**限流和任务链熔断是一回事吗？**
不是。租户桶满是限流，工具依赖错误率高是熔断。一个租户被限流不应打开全局 circuit，二者可以都采用 fail-fast 和可恢复返回，但阈值与主键应分别设计。

相关：`xiaohongshu-agent-timeout-circuit-breaker`


## 真题记录

- 公司：小红书
- 团队 / 岗位：AI Agent 算法
- 届别 / 流程：一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“如果很多员工同时用，会不会有一些限流或者降级策略”**；**“有不同租户、不同应用，这个概念是怎么理解的”**

---
id: drustz-9de0badff3c6aedebe
section: agent-core
order: 26
level: A
title: 05 · Reliability 与 Failure Recovery · 5. 自学资料
quick: 作者文档章节 · 05 · Reliability 与 Failure Recovery · 5. 自学资料
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Core、Gaps 与 Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/05_reliability.md
    type: primary
---
## 5. 自学资料

按优先级排序；前 4 条覆盖面试 80% 的追问。

1. [How to do distributed locking — Martin Kleppmann](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) — fencing token 的正典出处；看懂"为什么 Redlock 不安全"就看懂了分布式锁的全部争论 · 预计 20 min
2. [Designing robust and predictable APIs with idempotency — Stripe](https://stripe.com/blog/idempotency) — idempotency key 的设计动机与 client 重试规范；配合 [API 参考页](https://docs.stripe.com/api/idempotent_requests)（24h TTL、只对 POST、失败响应也缓存）· 预计 15 min
3. [The four types of Activity timeouts — Temporal](https://temporal.io/blog/activity-timeouts) — 四种 timeout 各检测什么、怎么配，durable execution 面试的标准答案来源 · 预计 15 min
4. [Timeouts, retries, and backoff with jitter — AWS Builders' Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) — retry storm、单层重试、"幂等才可重试"的第一手工程经验 · 预计 20 min
5. [Transactional outbox — microservices.io](https://microservices.io/patterns/data/transactional-outbox.html) — 状态与事件原子化的标准模式页，短小，直接对应 agent 的 intent journal · 预计 10 min
6. [Implementing Stripe-like Idempotency Keys in Postgres — brandur.org](https://brandur.org/idempotency-keys) — 前 Stripe 工程师的完整实现：recovery point、原子 phase、并发锁竞争，比官方 blog 深一层 · 预计 25 min
7. [Why Do Multi-Agent LLM Systems Fail? (MAST) — arXiv](https://arxiv.org/abs/2503.13657) — 3 大类 14 种 failure mode 的实证 taxonomy（150 条 trace 人工标注，κ=0.88），与本文件七类互补 · 预计 30 min（只看 taxonomy 图表 10 min）
8. [Exponential Backoff And Jitter — AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) — full / equal / decorrelated jitter 的模拟对比，backoff 公式选型的依据 · 预计 15 min
9. [Detecting Activity failures — Temporal docs](https://docs.temporal.io/encyclopedia/detecting-activity-failures) — timeout + retry policy 的权威语义定义，写 config 时的查阅页 · 预计 15 min

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/05_reliability.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/05_reliability.md)。作者整理资料；许可和第三方来源范围见阅读指南。

---
id: drustz-24e4512c6f5f42e7ad
section: agent-core
order: 76
level: A
title: 分布式水平扩展（单机 harness → cluster） · 自学资料
quick: 作者文档章节 · 分布式水平扩展（单机 harness → cluster） · 自学资料
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/scaling.md
    type: primary
---
## 自学资料

1. [Temporal 架构文档（temporalio/temporal repo）](https://github.com/temporalio/temporal/blob/main/docs/architecture/README.md) — frontend/history/matching 拆分、shard、event sourcing 的第一手描述，自建 durable execution 前必读的工业参照 · 25 min
2. [How to do distributed locking（Kleppmann）](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) — fencing token 的原始论证 + 为什么 Redlock 不安全；本页所有 lease/fencing 说法的出处 · 15 min
3. [Temporal Workflow Definition（官方 docs）](https://docs.temporal.io/workflow-definition) — determinism 约束的精确表述与 versioning/patching，回答「LLM 调用为什么必须包 activity」的依据 · 15 min
4. [Redis Streams（官方 docs）](https://redis.io/docs/latest/develop/data-types/streams/) — consumer group / PEL / XACK / XAUTOCLAIM 完整语义，读完能手写可靠消费循环 · 20 min
5. [Queue System using SKIP LOCKED（Neon guide）](https://neon.com/guides/queue-system) — 带完整 SQL 的 Postgres 队列实现走查，对照本页 claim SQL 复习 · 10 min
6. [Message Delivery Guarantees for Apache Kafka（Confluent docs）](https://docs.confluent.io/kafka/design/delivery-semantics.html) — at-most/at-least/exactly-once 的准确定义与实现边界，面试说投递语义别口胡 · 10 min
7. [LiteLLM Router 文档](https://docs.litellm.ai/docs/routing) — 6 种路由策略 + cooldown/retry/fallback 全部参数；自建网关也照这份 API 抄作业 · 15 min
8. [ContinueAsNew in Temporal（indeedeng/iwf wiki）](https://github.com/indeedeng/iwf/wiki/ContinueAsNew-in-Temporal-%28or-Cadence%29-workflow) — 为什么 replay 模型必须截断 history、状态怎么安全跨代，long-horizon agent run 直接相关 · 10 min

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/scaling.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/scaling.md)。作者整理资料；许可和第三方来源范围见阅读指南。

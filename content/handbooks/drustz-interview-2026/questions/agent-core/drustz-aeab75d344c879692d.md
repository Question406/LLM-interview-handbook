---
id: drustz-aeab75d344c879692d
section: agent-core
order: 71
level: A
title: 分布式水平扩展（单机 harness → cluster） · 30 秒版本（3 句话）
quick: 作者文档章节 · 分布式水平扩展（单机 harness → cluster） · 30 秒版本（3 句话）
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
## 30 秒版本（3 句话）

1. 单机 SQLite harness 走向分布式只需外部化三样东西：task queue（typed queue 解耦提交与执行）、event log（Postgres 单表 → 分区 → Kafka）、调度（按 run_id 分片的 orchestrator）——每一步由明确的瓶颈指标触发，不提前做。
2. 分布式后唯一必须守住的不变量：任意时刻每个 run 只有一个 writer（lease + fencing token）；重试、replay、shard rebalance 的正确性全是这条不变量的推论。
3. Agent loop 天然 long-running 且非确定（LLM 输出），Temporal 式 durable execution 不能照搬——LLM/tool 调用必须作为 activity 持久化结果、replay 时跳过，workflow 本体保持 deterministic；面试里讲清这层映射是 senior 信号。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/scaling.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/scaling.md)。作者整理资料；许可和第三方来源范围见阅读指南。

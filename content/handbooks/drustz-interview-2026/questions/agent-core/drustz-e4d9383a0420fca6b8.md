---
id: drustz-e4d9383a0420fca6b8
section: agent-core
order: 13
level: A
title: 02 · State、Durable Execution 与 Memory · 4. Worker lease ⭐⭐⭐
quick: 作者文档章节 · 02 · State、Durable Execution 与 Memory · 4. Worker lease ⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/02_state_and_memory.md
    type: primary
---
## 4. Worker lease ⭐⭐⭐

- DB 事务 claim task，写 `worker_id/lease_until/attempt`。
- heartbeat 延长 lease。
- result commit 必须携带 attempt/fencing token；过期 worker 的迟到结果被拒绝。
- retry 前检查 operation status。

分布式多 worker 扩展见 [../03_gaps/scaling.md](?book=drustz-interview-2026&section=agent-core&question=drustz-2689044041125af3f2)。

> 高分句：lease 防止双跑，fencing token 防止迟到写——两个缺一不可。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/02_state_and_memory.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/02_state_and_memory.md)。作者整理资料；许可和第三方来源范围见阅读指南。

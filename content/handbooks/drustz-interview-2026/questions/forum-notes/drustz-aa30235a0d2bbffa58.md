---
id: drustz-aa30235a0d2bbffa58
section: forum-notes
order: 245
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 5: Scaling & Trade-offs'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 5: Scaling & Trade-offs'
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
## Phase 5: Scaling & Trade-offs

### Addressing Non-Functional Requirements

**Fast API acknowledgement**

- Persist metadata in PostgreSQL and enqueue asynchronously
- Return `202 Accepted` immediately after durable write
**Durability**

- Keep job/attempt state in PostgreSQL as source of truth
- Rebuild in-memory queues from DB after Redis loss
- Use outbox/event log for reliable notifications and ready-queue rehydration
**Recovery from preemption**

- Heartbeat leases + fenced attempts
- Periodic checkpoints to object storage
- Lease monitor automatically requeues lost jobs
**Scheduling latency**

- Maintain a small warm worker buffer per GPU type/model
- Partition queues by `priority_tier + model_version + gpu_type`
- Prefer local-region or already-warm compatible workers

### Bottlenecks and Mitigations

**1. GPU cold-start latency**

Problem: Booting an external GPU worker can take tens of seconds or minutes.

Mitigation:

- Keep a warm idle buffer for popular models
- Predict demand using recent queue depth
- Separate premium and best-effort pools
**2. Checkpoint overhead**

Problem: Large checkpoint uploads can slow active generation and consume storage.

Mitigation:

- Checkpoint at coarse time intervals, not every step
- Store compressed or delta checkpoints if supported by the model runtime
- Retain only the newest checkpoint(s)
**3. Split-brain execution**

Problem: A network partition can make the scheduler think a worker died while the worker keeps running.

Mitigation:

- Reject all writes without the latest fencing token
- Mark only one attempt as current in the DB
- Make completion/failure APIs idempotent
**4. Provider outage or shrinking pool**

Problem: External vendor capacity can suddenly drop.

Mitigation:

- Route across multiple providers/regions
- Surface longer ETA to clients
- Apply admission control or rate limiting rather than overload the queue indefinitely

### Trade-off: Push vs Pull Scheduling

| Approach | Pros | Cons |
| ---------- | ---------------------------------- | ------------------------------------- |
| **Push** | Lower scheduler round-trip latency | More fragile when workers disappear |
| **Pull** | Natural fit for volatile workers | Slightly more polling/control traffic |
| **Hybrid** | Can optimize hot pools | More operational complexity |

For this problem, choose **pull scheduling**:

- Workers are ephemeral
- One worker handles one video
- Pull simplifies liveness and assignment correctness

### Trade-off: Checkpoint Frequency

| Approach | Pros | Cons |
| ------------------------ | ------------------------------- | ------------------------------------ |
| **Frequent checkpoints** | Less lost work | More storage and generation overhead |
| **Sparse checkpoints** | Cheaper and simpler | More recomputation on failure |
| **Adaptive interval** | Better cost/performance balance | Harder to tune and reason about |

A strong interview answer is to start with a fixed interval, then discuss adapting it by job duration, queue pressure, and provider reliability.

### Trade-off: One Video Per Worker

Why keep one active video per worker instead of sharing a worker across jobs?

- GPU memory is large but model runtime is heavy
- Per-job interference makes latency and checkpoint timing less predictable
- Scheduling becomes simpler and failure isolation is stronger
If the interviewer asks about higher utilization, discuss batching or multi-tenancy only for smaller models or lower-quality tiers.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。

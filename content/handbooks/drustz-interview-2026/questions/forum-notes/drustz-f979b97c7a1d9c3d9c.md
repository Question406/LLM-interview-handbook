---
id: drustz-f979b97c7a1d9c3d9c
section: forum-notes
order: 241
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 1: Requirements'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 1: Requirements'
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
## Phase 1: Requirements

### Functional Requirements

- **Users should be able to** submit a video generation request with prompt, model version, duration, and output settings
- **Users should be able to** get asynchronous job status, progress, and the final downloadable video
- **Users should be able to** cancel a queued or running generation job
- **The system should be able to** assign each queued job to an available GPU worker, with at most one active video per worker
- **The system should be able to** recover from worker termination, provider failure, or transient network issues without losing accepted jobs
Assume prompt safety checks, billing, and content moderation happen upstream or in a separate service. The focus here is scheduling, worker lifecycle, and failure handling for video generation.

Do not block the client request until generation finishes. Video creation takes minutes, so the public API must be asynchronous and return a durable `job_id`.

### Non-Functional Requirements

| Requirement | Target | Rationale |
| --------------------------------- | ------------ | -------------------------------------------------- |
| **Request acknowledgement (P95)** | < 500ms | Fast control-plane response for job creation |
| **Scheduling latency (P95)** | < 30 seconds | Jobs should start quickly when capacity exists |
| **Progress freshness** | < 5 seconds | Users expect visible status updates |
| **Accepted-job durability** | No lost jobs | Once accepted, a job must survive service failures |
| **Availability** | 99.9% | Generation service should remain usable |
| **Work lost on preemption** | < 30 seconds | Checkpointing should bound wasted GPU work |

In an interview, call out that queue wait may exceed the target during GPU shortages. The system should expose ETA and enforce admission control rather than pretending infinite capacity.

### Capacity Estimation

**Assumptions:**

- 100K video generations per day
- Peak submission rate: 20 jobs/sec
- Average generation time: 3 minutes on one GPU worker
- Average final video size: 25 MB
- Workers send progress updates every 5 seconds
- Workers heartbeat every 10 seconds for lease renewal
**Compute requirement:**

- 20 jobs/sec x 180 sec = 3,600 concurrent running jobs at peak
- With a 10% warm buffer, target ~4,000 ready/busy workers across pools
**Control-plane throughput:**

- Job creates: ~20 writes/sec
- Heartbeats: 3,600 / 10 = 360 heartbeats/sec
- Progress updates: 3,600 / 5 = 720 progress events/sec
- Checkpoint writes are much less frequent and still modest relative to GPU compute cost
**Storage requirement:**

- Final artifacts: 100K x 25 MB = 2.5 TB/day
- Checkpoints can exceed final output volume, so keep only the latest few and apply aggressive TTL/lifecycle policies
The metadata/control plane is not the bottleneck here. GPU capacity, cold starts, and lost work from preemption dominate the design.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。

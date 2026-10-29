---
id: drustz-23ac06e8c4001fb44e
section: forum-notes
order: 242
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 2: Data Model'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 2: Data Model'
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
## Phase 2: Data Model

### Core Entities

```text
GenerationJob
├── id: UUID
├── user_id: UUID
├── idempotency_key: string
├── prompt_ref: string (encrypted prompt/input blob)
├── model_version: string
├── duration_sec: int
├── resolution: string
├── priority_tier: enum (free, pro, enterprise)
├── status: enum (queued, assigned, running, completing, completed, failed, cancelled)
├── progress_pct: int
├── latest_checkpoint_ref: string
├── final_artifact_id: UUID
├── failure_reason: string
├── created_at: timestamp
├── started_at: timestamp
└── completed_at: timestamp

JobAttempt
├── id: UUID
├── job_id: UUID (FK)
├── attempt_no: int
├── worker_id: UUID (FK)
├── provider_instance_id: string
├── fencing_token: UUID
├── status: enum (leased, running, lost, failed, succeeded)
├── last_heartbeat_at: timestamp
├── lease_expires_at: timestamp
├── checkpoint_ref: string
├── failure_reason: string
├── started_at: timestamp
└── ended_at: timestamp

Worker
├── id: UUID
├── provider: string
├── provider_instance_id: string
├── gpu_type: string
├── region: string
├── status: enum (booting, idle, busy, draining, lost, terminated)
├── current_job_id: UUID
├── registered_at: timestamp
├── last_heartbeat_at: timestamp
└── drain_deadline: timestamp

Artifact
├── id: UUID
├── job_id: UUID (FK)
├── type: enum (input, checkpoint, final_video)
├── object_key: string
├── size_bytes: bigint
├── checksum: string
├── created_at: timestamp
└── expires_at: timestamp

JobEvent
├── id: UUID
├── job_id: UUID (FK)
├── attempt_id: UUID (FK)
├── type: enum (queued, leased, progress, checkpointed, completed, failed, cancelled)
├── payload: jsonb
└── created_at: timestamp
```



### Entity Relationships

```text
User 1:N GenerationJob
GenerationJob 1:N JobAttempt
Worker 1:N JobAttempt
GenerationJob 1:N Artifact
GenerationJob 1:N JobEvent
```



Separate the logical job from execution attempts. The job represents one requested video; each attempt represents one run on one worker. This separation makes retries and preemption recovery much cleaner.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。

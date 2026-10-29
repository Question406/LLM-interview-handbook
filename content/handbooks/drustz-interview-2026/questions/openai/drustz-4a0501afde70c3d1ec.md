---
id: drustz-4a0501afde70c3d1ec
section: openai
order: 42
level: A
title: Design Sora Video Generation
quick: locally-saved-topic-editorial · Design Sora Video Generation
companies:
  - openai
tags:
  - DrustZ
  - locally-saved-topic-editorial
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/design-sora-video-generation
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Design Sora Video Generation Scheduling

### Design Sora Video Generation Scheduling

Design the backend for Sora-style video generation. A client submits a prompt and video settings, your service accepts the job, schedules it onto an external GPU pool, tracks progress, and returns the final video artifact. The hardest part is that **each worker can generate only one video at a time**, and the external GPU pool is elastic and preemptible, so workers may be terminated at any point during generation. This problem primarily tests whether you can design **durable job orchestration**, **capacity-aware scheduling**, and **failure recovery on unreliable compute**.

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

## Phase 3: API Design

### Protocol Choices

| Operation | Protocol | Reason |
| ----------------------------- | ----------- | --------------------------------------- |
| Public job lifecycle | REST | Simple async request-response API |
| Progress/result notifications | Webhook/SSE | Efficient async delivery to clients |
| Worker control plane | gRPC / RPC | Typed, efficient heartbeats and leasing |

### Public REST Endpoints

```text
# Job lifecycle
POST   /api/video-generations                 Create generation job
GET    /api/video-generations/{job_id}        Get job status, progress, result
DELETE /api/video-generations/{job_id}        Cancel queued/running job
GET    /api/video-generations/{job_id}/events Get progress/event history
```



**Create job request:**

```json
{
  "prompt": "A cinematic drone shot over a snowy mountain at sunrise",
  "model_version": "sora-v1",
  "duration_sec": 10,
  "resolution": "720p",
  "callback_url": "https://client.example.com/webhooks/video-status",
  "idempotency_key": "req_7cfa9c1a"
}
```



**Create job response (202):**

```json
{
  "job_id": "job_123",
  "status": "queued",
  "estimated_wait_seconds": 45
}
```



**Get job response (200):**

```json
{
  "job_id": "job_123",
  "status": "running",
  "progress_pct": 62,
  "attempt_no": 2,
  "result_url": null,
  "failure_reason": null
}
```



### Internal Worker APIs

```text
POST /internal/workers/register                Worker registers after boot
POST /internal/workers/{worker_id}/lease       Worker requests one job
POST /internal/attempts/{attempt_id}/heartbeat Extend lease / report liveness
POST /internal/attempts/{attempt_id}/progress  Update progress / ETA
POST /internal/attempts/{attempt_id}/checkpoint Persist resume point
POST /internal/attempts/{attempt_id}/complete  Mark job success with artifact ref
POST /internal/attempts/{attempt_id}/fail      Mark job failure and classify retryability
```



Every `heartbeat`, `progress`, `checkpoint`, `complete`, and `fail` request must include the `fencing_token` from assignment. If a stale worker comes back after losing its lease, its writes must be rejected.

## Phase 4: High-Level Design

### Architecture Overview

### Component Responsibilities

**API Service**

- Validates request shape and idempotency key
- Persists `GenerationJob` durably before acknowledging
- Emits a durable ready signal so Redis queues can be rebuilt after crashes
- Enqueues the job by priority/model/GPU requirements
- Exposes status, cancel, and result retrieval APIs
**Scheduler**

- Owns queue selection and worker-job matching
- Assigns at most one active job per worker
- Creates fenced `JobAttempt` records transactionally
- Uses Redis as a readiness index, but claims jobs authoritatively in PostgreSQL
- Prefers resume-from-checkpoint over restart-from-zero
**Capacity Manager**

- Watches queue depth, wait time, and idle worker buffer
- Calls the external provider API to scale pools up/down
- Marks workers as `draining` when the provider warns of shutdown
**Lease Monitor**

- Detects missed heartbeats and expired leases
- Marks attempts as `lost`
- Requeues jobs using the latest durable checkpoint
**GPU Worker**

- Pulls one job at a time
- Loads model/runtime, generates frames/video, emits progress
- Writes checkpoints and final artifact to object storage
- Stops accepting new work when draining
Treat Redis ready queues as an optimization, not the source of truth. The authoritative state transition from `queued` to `assigned` should happen in PostgreSQL so stale Redis entries cannot create double assignment or lost jobs.

### Data Flow: Job Submission and Assignment

In production, the API would usually write the job row and an outbox/ready event in the same PostgreSQL transaction, then a dispatcher would populate Redis asynchronously. The simplified diagram shows the happy path, but the key interview point is that a Redis miss must not lose an accepted job.

### Data Flow: Generation, Checkpoint, and Completion

### Data Flow: Worker Preemption and Recovery

### Deep Dive: Lease-Based Scheduling With Fencing

The key invariant is: **one logical video job can have only one valid active attempt at a time**.

Use worker pull plus leased execution:

- Workers register as `idle` and ask for work when ready
- Scheduler uses Redis to find candidate jobs, then atomically claims one queued job in PostgreSQL and creates a `JobAttempt`
- Attempt gets `lease_expires_at = now + 30s` and a unique `fencing_token`
- Worker heartbeats every 10s to extend the lease; progress can be reported more frequently
- If lease expires, the attempt is treated as dead even if the old worker later reconnects

```typescript
function assignJobToWorker(
  workerId: string,
  capabilities: WorkerCapabilities,
): Assignment | null {
  const candidateIds = peekReadyJobIds(capabilities); // Redis hint/index only

  beginTransaction();

  const job = claimQueuedJob(candidateIds); // DB row lock / compare-and-swap
  if (!job) {
    rollback();
    return null;
  }

  const attempt = createJobAttempt({
    jobId: job.id,
    workerId,
    fencingToken: randomUUID(),
    leaseExpiresAt: nowPlusSeconds(30),
  });

  markJobAssigned(job.id, attempt.id);
  markWorkerBusy(workerId, job.id);
  commit();
  removeReadyHint(job.id); // best-effort cleanup

  return attempt;
}
```



If Redis and PostgreSQL ever disagree, PostgreSQL wins. Stale ready hints are acceptable because the final claim is protected by the job row state.

Why pull beats push here:

- Workers can disappear without warning, so assigning only to currently alive workers reduces wasted dispatches
- Provider cold starts are slow, so booted workers should immediately pull from the queue
- Pulling naturally respects the "one worker, one video" rule

### Deep Dive: Checkpointing Strategy

Without checkpointing, a terminated worker can waste several minutes of GPU time. With checkpointing:

- Worker uploads resume state every 20-30 seconds or at major generation milestones
- Scheduler records only the latest durable checkpoint reference
- Replacement workers resume from the newest checkpoint
- If no checkpoint exists yet, retry from the start
Checkpoint trade-off:

- More frequent checkpoints reduce lost work
- But checkpoints cost upload bandwidth, storage, and latency
Practical interview answer:

- Start with a 30-second checkpoint interval
- Keep only the latest 1-2 checkpoints per active job
- Delete old checkpoints after success or terminal failure

### Deep Dive: Provider Volatility

External GPU pools are not fully under your control, so treat them as unreliable infrastructure:

- If the provider emits `draining` or preemption warnings, mark the worker `draining` and stop assigning new jobs
- If the worker vanishes without notice, rely on heartbeat timeout
- Use multiple providers or regions for failover at higher scale
- Keep the system-of-record for jobs in your own database, never only inside the provider queue
Do not "hand off" the job entirely to the GPU provider and assume it is now safe. If the provider loses the task or the instance dies, you need your own durable job state and retry history.

### Cancellation Flow

- If job is `queued`, remove it from the queue and mark `cancelled`
- If job is `running`, mark cancel requested in DB and notify the worker on next heartbeat or via a control channel
- Worker should checkpoint only if useful, then stop and release the GPU
- Late success from a cancelled stale attempt is rejected via fencing token + terminal job state check

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

## Common Pitfalls

Returning success to the client before the job is durably stored. A crash between accept and enqueue can silently lose the generation request.

Assuming the GPU provider will always send a preemption warning. In practice, heartbeat loss is the only reliable failure signal for many pools.

Allowing stale workers to finalize a video after the job was already retried elsewhere. Without fencing, you can end up with conflicting outcomes.

Using a single giant FIFO queue for all models and GPU types. Mismatched jobs will sit behind incompatible workers and hurt latency.

## Interview Checklist

### Requirements Phase

- [ ] Clarified that generation is asynchronous
- [ ] Stated the one-worker-per-video constraint
- [ ] Called out external GPU pool volatility as a core design driver

### Design Phase

- [ ] Introduced durable job state plus retryable attempts
- [ ] Explained worker pull, leases, and fencing tokens
- [ ] Covered checkpoint upload and resume flow
- [ ] Described cancellation and result delivery

### Scaling Phase

- [ ] Addressed GPU cold starts and warm pools
- [ ] Discussed provider outage and shrinking capacity
- [ ] Covered checkpoint interval trade-offs
- [ ] Mentioned queue partitioning and priority tiers

## Summary

| Aspect | Decision | Rationale |
| ----------------------- | --------------------------------------------- | ---------------------------------------------- |
| **Client API** | Async `POST` returning `job_id` | Video generation takes minutes |
| **Scheduling model** | Worker pull + lease-based assignment | Fits volatile external GPU workers |
| **Execution semantics** | One active attempt per job with fencing token | Prevents duplicate/conflicting completion |
| **Failure recovery** | Heartbeats + checkpoint/resume + requeue | Bounds lost work when workers are terminated |
| **State storage** | PostgreSQL + Redis + object storage | Durable metadata, fast queues, large artifacts |
| **Capacity strategy** | Warm buffers + provider-aware scaling | Reduces cold starts and queue wait |

The most important insight is that this system is not primarily a "video pipeline" problem; it is a **durable orchestration problem on unreliable GPUs**. If you preserve job ownership, liveness, and resume state correctly, the rest of the system becomes much easier to scale.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100240*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/design-sora-video-generation)
- [相关来源](https://www.1point3acres.com/bbs/thread-1180717-1-1.html)
- [相关来源](https://www.1point3acres.com/bbs/thread-1177818-1-1.html)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

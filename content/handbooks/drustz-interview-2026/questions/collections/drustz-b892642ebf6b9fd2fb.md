---
id: drustz-b892642ebf6b9fd2fb
section: collections
order: 16
level: A
title: Anthropic 题库（爬取全量） · ML System Design
quick: 作者文档章节 · Anthropic 题库（爬取全量） · ML System Design
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 主题题库与复习资料
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/anthropic.md
    type: primary
---
## ML System Design

### System Design Q1：LLM Inference Batch API（题库最高频 SD 题）
*hard · 频率: very high (16+ 讨论) · 2026-06*

55 min，'Very High' 频率，16+ 关联讨论，标签 llm-inference/batching/kv-cache/gpu。题面（公开部分）：设计一个 HTTP API，对外暴露 LLM 推理的 batch 处理功能。1p3a 题解页结构：The Challenge → 需求澄清 → 规模/资源估算 → API 设计 → 数据存储 → 基础架构 → 组件深挖 → 修复潜在问题（正文需登录）。SD Q3 也是 inference API 主题，有帖专门对比 Q1 vs Q3（interview thread 1158532）；另有 SD Q4 求助帖（thread 1169228、1163059）。变种：'API batch string function combining API requests for LLM APIs'（infra SDE 设计轮，bbs thread 1123616 区域）。

**解法**: 核心考点（我的推断+行业标准答案）：continuous batching（Orca 式 iteration-level scheduling）、KV cache 管理/PagedAttention、prefill vs decode 分离、排队与 SLA（p99 TTFT/TPOT）、prefix caching、backpressure 与 rate limit、GPU 池扩缩容 vs 冷启动、idempotent retry与结果存储（batch job 异步 API：提交→轮询/webhook）。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/problems/post/7100012&gt;)

### Design a GPU inference batching system (Anthropic's most-reported system design question)
*medium · 频率: very high (called 'most commonly reported' Anthropic SD question) · 2026-01*

Prompt: 'You have a single GPU that can process up to 100 inputs per batch. Users submit requests synchronously and wait for results. Design the system that receives inputs, batches them, processes them on the GPU, and returns responses to the correct users.' Extension version: end-to-end LLM query batching — request intake, batching policy, GPU routing, load balancing, response delivery. Follow-ups: how do you determine GPU capacity; failover handling; what happens when a batch member fails; queueing vs latency trade-off. Asked in the 50-55 min phone screen and/or onsite (4-5 rounds, 45-55 min each). Exponent notes Anthropic questions 'use AI framing but test classic distributed systems infrastructure' and staff candidates must drive the conversation. Same question appears in Exponent's question bank tagged Anthropic + 7 other companies.

**解法**: Core pattern: request queue + batch scheduler with dual trigger (max batch size 100 OR max wait timeout, e.g. 10-50ms) to bound tail latency; correlation IDs / futures to route responses back to blocked callers; backpressure via bounded queue + 429s; discuss dynamic/continuous batching (vLLM-style) as improvement since sequences finish at different times; multi-GPU extension = consistent-hash or least-loaded dispatch, health checks, retry-on-failure with idempotency. Mention SLO split: TTFT vs throughput, and priority queues for paid tiers.

来源: &lt;[来源链接](https://www.tryexponent.com/blog/anthropic-system-design-interview&gt;)

### System design 高频真题：LLM sampling/推理 API（Google Doc 共享文档轮）
*hard · 频率: very high（3+ 独立报告 + 多聚合站） · 2026-01*

Anthropic system design 轮的标志性形式：不用画图工具，在共享 Google Doc 里写设计。最高频题（多个独立报告）：Exponent Safeguards 面经原文 "Design an API to let users sample from large language models efficiently, with good batching and request orchestration"；interviewing.io 版本 "Designing an API for serving large language models efficiently, covering request batching, queuing, and GPU utilization under variable load"。相关变体（聚合站）：LLM 推理系统架构（batching、延迟优化、GPU 调度、部署、容错）、"Design an API for an LLM with a Safety Layer"、KV cache 管理、多区域部署。考察点：变负载下的批处理与排队、throughput vs 延迟 tradeoff、GPU 利用率。

**解法**: 核心词：continuous/in-flight batching、paged KV cache（vLLM 思路）、prefill 与 decode 分离调度、按 SLA 分级队列 + backpressure、流式返回（SSE）、speculative decoding、prefix cache 命中、按 token 计费与配额。给出容量估算（单卡 tokens/s、显存 = 权重+KV）会加分。（我的推断，基于业界标准实践）

来源: &lt;[来源链接](https://www.tryexponent.com/experiences/anthropic-senior-software-engineer-interview-2ffa5f&gt;)

### Anthropic 系统设计真题：设计高并发 batched LLM 推理 API（含完整需求）
*hard · 频率: high (recurring theme across 3+ sources) · 2026-07*

OfferEngineering 2026-07 完整收录（与 L4 面经'distributed inference API/GPU scheduling and batching for LLM inference workloads'相互印证）。题面：设计服务 LLM 请求的高并发推理 API。客户端提交 prompt+model+生成参数+优先级+是否流式；GPU worker 池有限，核心挑战是 batching——把兼容请求合批提高throughput和 GPU 利用率同时满足交互路径 <500ms-1s 延迟目标。功能需求：同步/流式响应、重试+request ID+幂等、过载时排队/背压/限流/按优先级丢弃。非功能：throughput vs 延迟平衡（等待凑批 vs 尾延迟）、GPU 显存（长 prompt、KV-cache 增长、prefill vs decode 行为差异）、突发流量稳定性、worker 崩溃时受影响请求的安全重试、可观测性（队列深度/批大小/GPU 利用率）。

**解法**: 讲 continuous batching（vLLM 式 iteration-level scheduling）、PagedAttention 管 KV-cache、prefill/decode 分离、admission control + token-bucket 限流、per-tier 队列 + deadline-aware flush（max_wait_ms 或凑满 batch 先到先触发）、worker 心跳 + 请求级 checkpoint 重试。候选人有 post-training 背景，这题应主答推理系统细节。

来源: &lt;[来源链接](https://www.reddit.com/r/OfferEngineering/comments/1us7dqf/anthropic_system_design_question_design/&gt;)

### System Design: Design ChatGPT (conversational AI backend with SSE token streaming)
*hard · 频率: Anthropic freq 6/10 (OpenAI 9, Amazon 4, xAI 4) · 2026-04 (published)*

UNLOCKED - FULL 37KB expert-reviewed solution captured (saved at /tmp/h2h_chatgpt_content.md). Stage: Onsite. Design the backend for a ChatGPT-like service: multi-turn conversations, durable history (resume days later), context assembly, GPU-cluster inference dispatch, token streaming via Server-Sent Events. Given targets: TTFT <=500ms p50 / 2s p95; durable conversation persistence. Full doc structure: clarifying Q&A (6 items with interviewer answers + takeaways), functional/non-functional requirements, back-of-envelope estimation, data model + access patterns + storage tradeoff, API design (send-message + SSE event contract + history fetch), high-level architecture, chat completion flow, TTFT budget breakdown, admission control and caching, deep dives (GPU inference scheduling and CONTINUOUS BATCHING; context window management and token budget assembly; streaming delivery contract and failure/reconnect recovery), other considerations (safety guardrails pipeline latency budget, multi-model routing and gradual rollout, conversation summarization for extended context, cost management and tier-based throttling), and explicit interviewer expectations broken down by Junior/Intermediate/Senior level.

**解法**: Full official solution captured locally; key spine: API gateway -> conversation service (durable store) -> context assembler (token budget: system prompt + summarized history + recent turns) -> inference scheduler with continuous batching on GPU pool -> SSE streamer with resumable event ids; separate fast path for streaming vs durable write path.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69d6f527c4c1bc791ee229e3&gt;)

### System Design: Distributed AI Model Downloader (500GB model to 1000 hosts)
*hard · 频率: Anthropic freq 8/10 (Anthropic-only tag); last reported 2026-07-08 · 2026-04 (published)*

LOCKED (long preview captured). Stage: Onsite. Internal datacenter tool: fetch a ~500GB model from an external repository and replicate to every host in a 1000-host GPU cluster in minutes not hours, under strict per-link bandwidth caps. Preview's clarifying Q&A establishes: on-demand command-driven distribution of specific model versions (not continuous registry sync); goal is minimizing total distribution time within SLA (~10-20 min window discussion); every host needs a complete verified copy (integrity checking). Core tension: external egress is the bottleneck, so download once (or few times) from the source and fan out peer-to-peer inside the cluster. Full requirement analysis/architecture/deep dives paywalled.

**解法**: My inference (consistent with the preview): chunk the model file; a small set of seed hosts pull distinct chunks from the external repo in parallel (respecting egress cap); then BitTorrent-style peer-to-peer chunk exchange / tree- or pipeline-based multicast inside the cluster so aggregate internal bandwidth scales with host count; per-chunk checksums + final manifest hash for verification; scheduler tracks chunk availability maps, handles stragglers/failed hosts by re-replication. Time lower bound ~ size/per-host-NIC-bandwidth with pipelining.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69dbccaee4441834b3f72fae&gt;)

### System Design: AI Prompt Playground (this is the written-Google-Doc SD round)
*medium · 频率: Anthropic freq 9/10 (Anthropic-only tag) · 2026-04 (published)*

LOCKED (long preview captured). Stage: Onsite. Web-based tool for iterative prompt engineering against LLMs: each run is a stateless one-shot request (no conversational memory); user edits prompt/parameters, runs, inspects output, repeats; winning prompts saved/exported. Preview clarifying Q&A: single-user projects only (no realtime collaboration -> one writer per project simplifies versioning); prompts up to 100K tokens / several hundred KB payloads must be handled gracefully; playground must feel instant despite slow external LLM calls; every iteration durably versioned so users can experiment without losing a good prompt. Per hack2hire's process blog, Anthropic runs this SD round entirely as a WRITTEN Google Doc discussion - no diagrams expected; interviewers press on requirements, schema, and scaling roughly equally and drive pacing aggressively. Full solution paywalled.

**解法**: My inference: focus on (1) prompt/version data model - append-only version chain per project, content-addressed blobs for large prompts, autosave drafts vs committed versions; (2) run execution - async job + streaming partials to feel instant, timeout/retry on LLM provider, idempotency keys; (3) large payload handling - chunked upload, size limits, server-side token counting; (4) run history storage linking prompt-version + params + output + cost/latency metrics; (5) scaling reads and provider rate-limit queueing. Practice writing this as prose in a doc, not diagrams.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69dbcc73e4441834b3f72fad&gt;)

### System Design: GPU Inference Serving System (dynamic batching under tight latency budget)
*hard · 频率: Anthropic freq 10/10 (Anthropic-only tag, their most-reported SD); last reported 2026-07-05 · 2026-04 (published)*

LOCKED (long preview captured). Stage: Onsite. Layer between user prompts and GPU models: accept many concurrent HTTP requests, group into batches, dispatch to GPU worker pool, return individual responses. Preview clarifying Q&A pins the constraints: SINGLE synchronous completion per request (explicitly NO token streaming); end-to-end p99 <= 500ms total, of which inference execution itself is ~100ms, leaving ~400ms budget for queueing + network + coordination; GPUs cost-effective only with large batches; slow GPU warm-up makes dynamic scaling hard under traffic spikes. Core tension: batch size (throughput) vs queueing delay (latency). Full solution paywalled.

**解法**: My inference: central (or per-model) batching queue with a max-wait timer (e.g., dispatch when batch full OR after T ms, T tuned so queue wait + inference fits p99); size-aware batching by sequence length; per-GPU worker loop pulling batches; admission control/load shedding when queue depth implies SLA miss; warm pool + predictive pre-scaling because of slow warm-up; request hedging/retries on worker failure; metrics on queue delay vs batch occupancy. Discuss why continuous batching applies to autoregressive generation vs fixed batching for single-shot scoring.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69db22a2e4441834b3f72b81&gt;)

### System Design: GPU Scheduling Platform (shared training/batch-job cluster)
*hard · 频率: Anthropic freq 3/10 (OpenAI 10, Databricks 6); last reported 2026-06-22 · 2026-04 (published)*

LOCKED (long preview captured). Stage: Onsite. Scheduling + execution layer for a shared GPU cluster: users submit containerized batch jobs (ML training, fine-tuning, batch inference) with resource requirements and priority; platform queues by priority, places on nodes with capacity, runs in containers, monitors, auto-handles failures. Preview clarifying Q&A: each job fits on a single node (gang scheduling for distributed training explicitly deferred to follow-up); node can become unreachable between placement decision and job start - every placement is a distributed commitment across scheduler, database, and remote node agent, any of which can fail mid-assignment. Full solution paywalled.

**解法**: My inference: priority queues with preemption policy; two-phase placement (reserve in DB -> ack from node agent -> commit; lease/timeout to reclaim on agent silence); reconciliation loop comparing desired vs actual state (Kubernetes-controller style); heartbeat-based node health, job checkpointing and restart policy; fairness (per-team quotas, DRF) as follow-ups; gang scheduling and bin-packing/fragmentation for multi-GPU as advanced follow-ups.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69d71cbfc4c1bc791ee22b22&gt;)

### Anthropic · System Design 题库（7 题，重 AI 推理基础设施 + Prompt Playground 书面轮）
*hard · 频率: onsite 常见 — Anthropic 频率：Design GPU Inference Serving System 10、Design AI Prompt Playground 9、Design Distributed AI Model Downloader 8、Design ChatGPT 6、Design Slack-like Chat System 7、Design Facebook Messenger 4、Design GPU Scheduling Platform 3 · 2025-12 至 2026-02*

Anthropic SD 全 7 题（均 Onsite，正文需登录；practice URL 形如 .../anthropic/system-design/{id}/practice）：Design GPU Inference Serving System(Hard, id 69db22a2e4441834b3f72b81, Anthropic 频率10)、Design AI Prompt Playground(Medium, 69dbcc73e4441834b3f72fad, 频率9)、Design Distributed AI Model Downloader(Hard, 69dbccaee4441834b3f72fae, 频率8)、Design ChatGPT(Hard, 69d6f527c4c1bc791ee229e3, 频率6)、Design Slack-like Chat System(Hard, 69c9fe5dff3ebde766ced6f4, 频率7)、Design Facebook Messenger(Medium, 69d2bf7307421ca06eb8e38c, 频率4)、Design GPU Scheduling Platform(Hard, 69d71cbfc4c1bc791ee22b22, 频率3)。据 process blog：其中 Prompt Playground 轮为纯 Google Doc 书面讨论无需画图；另有一轮更常规 SD（如 batch inference API 设计）。

**解法**: （我的推断）对该 post-training 候选人极对口：GPU Inference Serving（KV-cache、continuous/dynamic batching、tensor/pipeline 并行、token 流式、多租户 SLO）、Model Downloader（大权重分发、P2P/BitTorrent 式、分片校验、断点续传）、Prompt Playground（多版本 prompt/eval、A-B、trace 存储）。练书面表达 requirements/schema/scaling 深度，别依赖画图。

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/system-design&gt;)

### Handle 100,000 requests/sec for an LLM token-generation service (Anthropic)
*hard · 频率: multiple reports · 2026-01*

Prompt: 'Handle up to 100,000 requests per second for an LLM token-generation service.' Tests throughput reasoning, horizontal scaling, request routing at volume. Related Anthropic-tagged question from Exponent's bank: 'Implement a streaming database with the given constraints and requirements.' Evaluation criteria reported: abstraction ability (strip AI framing to find the core infra problem), trade-off articulation, proactive failure-mode reasoning, scale reasoning under real constraints (not generic 'add servers').

**解法**: My inference: size in tokens/sec not RPS — 100K RPS × avg output tokens dictates GPU pool; per-node continuous batching, KV-cache memory as the binding constraint (KV bytes = 2·layers·kv_heads·head_dim·dtype per token), paged KV allocation; layered routing (edge LB → regional cell → model replica group), sticky sessions for multi-turn to exploit prefix cache; admission control + token-bucket rate limiting; degrade gracefully (shorter max_tokens, smaller fallback model, cached responses).

来源: &lt;[来源链接](https://www.tryexponent.com/blog/anthropic-system-design-interview&gt;)

### Design an agentic AI system that autonomously adapts to new tasks (Anthropic, ML roles)
*hard · 频率: single-to-few reports · 2026-01*

Prompt from Exponent's Anthropic guide and question bank: 'Design an agentic AI system that can autonomously adapt to new tasks.' More domain-specific than Anthropic's infra-flavored questions; expected coverage: agent loop (plan → act → observe), tool/function-calling interfaces, short/long-term memory, termination conditions, sandboxing and safety guardrails, evaluation of agent behavior.

**解法**: My inference: orchestrator with typed tool schemas (reduces hallucinated calls), task decomposition + reflection step, episodic memory store (vector DB) + working-memory context budget, guardrails before tool execution (allowlists, dry-run), bounded loop with max-steps + cost budget, eval harness with golden tasks + LLM-as-judge + human escalation; adaptation to new tasks via tool registry discovery and few-shot exemplar retrieval rather than retraining.

来源: &lt;[来源链接](https://www.tryexponent.com/questions?role=ml-engineer&type=system-design&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。

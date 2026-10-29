---
id: drustz-38c74ef05f786f13bd
section: collections
order: 51
level: A
title: 通用 ML 理论 + ML System Design 资源库 · ML System Design
quick: 作者文档章节 · 通用 ML 理论 + ML System Design 资源库 · ML System Design
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/theory-and-mlsd.md
    type: primary
---
## ML System Design

### Design ChatGPT (Hello Interview problem breakdown)
*hard · 频率: very high (cross-listed on 3+ major prep platforms) · 2025*

Functional requirements: send prompts and receive AI-generated responses; view past conversations and resume with prior context maintained. Non-functional: low latency-to-first-token (called the critical metric), efficient GPU allocation (GPUs = the scarce resource), 200M+ DAU scale. High-level design in two flows: prompt submission + AI response generation; chat history retrieval + context-aware resumption. Deep dives flagged: token streaming optimization and smoothness (SSE, resumability), GPU routing and request scheduling across workers, tier-based access control preventing resource monopolization, cost control for lengthy conversations via summarization/context management. Detailed solutions are premium-gated; free tier shows the structure above. Also appears as 'Design ChatGPT' mock on Exponent and in ByteByteGo's GenAI book — the single most cross-listed LLM SD question.

**解法**: Skeleton: stateless API/chat service + conversation store (NoSQL, conversation_id → messages) + inference fleet with continuous batching; stream via SSE with sequence numbers + resume tokens; context management: sliding window + rolling summary + prefix caching; GPU scheduler: priority queues by tier, preemption of free-tier, KV-cache-aware routing (route follow-up turns to replica holding prefix cache); billing/abuse: token metering at gateway.

来源: &lt;[来源链接](https://www.hellointerview.com/learn/system-design/problem-breakdowns/chatgpt&gt;)

### Design ChatGPT (Exponent mock interview walkthrough)
*medium · 频率: very high (canonical practice question) · 2024*

Functional: create/update/view/delete conversations; thumbs up/down message rating feeding model retraining; text input sanitization (profanity/insult detection). Non-functional: login + rate limiting for DDoS, scalability for concurrent users, tolerance for long backend latency. Back-of-envelope: 100-byte avg messages × 200M msgs/day = 20 GB/day, ~7.3 TB/yr, 76 TB/10yrs; NoSQL recommended. Components: Conversation Service (REST, unique conversation/message IDs), sanitization layer, transformer model with top-k/greedy/nucleus sampling, rating system with fraud-detection risk model, thumbs-down triggers retraining review. Also covers SFT + reward model (RLHF) as the improvement loop and multimodal extension.

来源: &lt;[来源链接](https://www.tryexponent.com/blog/design-chatgpt-system-design-mock-interview&gt;)

### 11 AI/LLM system design questions with answer frameworks (Educative blog, 2026)
*medium · 频率: prep compilation (topic frequency: RAG/serving themes reported very high elsewhere) · 2026*

(1) 'Design a high-QPS LLM inference service' — edge auth/quota/admission control, routing by tenant/model-class/region, intelligent batching, KV-cache reuse, queue-depth scaling, graceful degradation (shorter outputs, fallback models, cached responses), observability (TTFT, p95, tokens/sec, refusal rates, GPU saturation). (2) Throughput vs latency in LLM serving — TTFT vs time-to-last-token pull in opposite directions; micro-batching with ms windows + early token streaming; backpressure; explicit priority policy. (3) KV caching / batching / speculative decoding trade-offs — failure modes: KV memory explosion, draft-model distribution shift, spike latency. (4) SSE vs WebSockets for token streaming — SSE unidirectional/CDN-friendly; WS bidirectional (tool calls, cancellation); resume tokens, heartbeats, backpressure either way. (5) Prompt-injection defense — immutable system prompts, provenance-tracked context, schema-constrained whitelisted tool calls, output validation, continuous red-teaming. (6) RAG + tool orchestration — orchestrator decides retrieve/call/stop; bound context aggressively; log all decisions for replay/audit. (7) Observability/compliance logging — prompt hashes not raw text, model versions, retrieval metadata, tool traces, redaction, retention. (8) Real-time audio transcription + diarization pipeline — latency budget across ASR/speaker-embedding/clustering stages, jitter buffers, edge inference. (9) Capacity planning — size GPU pools on tokens/sec not requests/sec; pre-warmed buffers; cost-aware degradation. (10) Model/prompt lifecycle — version models, prompts, tools independently; shadow + canary deploys. (11) AI incident response — hallucination spikes, safety bypasses, cost explosions without 500 errors; kill switches, throttles, rollback.

来源: &lt;[来源链接](https://www.educative.io/blog/ai-system-design-interview-questions&gt;)

### alirezadir Machine-Learning-Interviews: 9-step MLSD framework + question catalog + 2026 GenAI section
*medium · 频率: very high (23k+ star repo, widely used) · 2026*

9-step framework: problem formulation → offline/online metrics → architectural components → data collection/labeling → feature engineering → model dev + offline eval → prediction service (batch/online/edge) → online testing & deployment (A/B, bandits, canary) → scaling/monitoring/continual training. Question catalog: video/movie/friends/event/game/replacement-product/rental/place recommendation; text/image/video/multimodal search; newsfeed ranking; ads CTR; entity linking; autocomplete; sentiment; language ID; chatbots; QA; OCR; image blurring (Street View); jaywalking detection; ride matching; harmful content & fraud detection; proximity services; delivery-time estimation; healthcare diagnosis. 2026 GenAI additions: RAG-vs-fine-tuning-vs-long-context-vs-tools decision; RAG pipeline (chunking, embeddings, hybrid retrieval + rerank + query rewriting, grounded generation with citations and context budgeting); agentic systems (planning, tool calling, memory, multi-agent orchestration, error recovery); production reliability (rate limiting, retries, idempotency, circuit breakers); guardrails (prompt-injection defense, PII redaction, hallucination checks); evaluation (golden datasets, LLM-as-judge, RAG triad: faithfulness/answer-relevance/context-relevance); cost/latency (token accounting, caching, batching, streaming, model routing). Repo also updated with KV cache, GQA, RoPE, MoE, SFT/DPO/GRPO/RLVR, PEFT topics.

来源: &lt;[来源链接](https://github.com/alirezadir/machine-learning-interviews/blob/main/src/MLSD/ml-system-design.md&gt;)

### 100+ real AI-engineer interviews compendium: LLM system design questions (Adil Shamim, 2026)
*medium · 频率: very high (aggregated from 100+ interviews; RAG-for-support marked most frequent) · 2026*

Most frequently reported SD questions: 'Design a RAG system for a customer support chatbot. How do you evaluate it?' (multiple companies, common opener; probes: retrieval strategy, hallucination prevention, golden datasets); 'How would you design an LLM-powered enterprise search system?' (scaling to 10M+ articles with sharding/caching, NDCG/MRR/precision@k, citations/source attribution, search-engine→answer-engine transformation); 'Design a generative AI document-processing pipeline for unstructured data (emails, PDFs, images)' (OCR integration, chunking, document-wide context when pages have prefatory info, sensitive-data protection); 'Your app gets 1M queries/day — how do you optimize cost?' (very common; multi-layer caching, model tiering/routing, prompt compression, quantization/distillation); 'How do you reduce latency in GenAI applications?' (bottleneck identification, PagedAttention, throughput vs latency); 'Walk through a production-ready agent architecture' (orchestrator logic, safe agent loops, termination conditions); 'Design an agent analyzing support tickets, drafting responses, escalating complex issues' (tool use, HITL); 'How do you evaluate a chatbot?'; 'How do you detect and mitigate hallucinations in production?' (very common); 'How do you debug a RAG chatbot giving confident but wrong answers?'; 'Estimate the budget for a RAG pipeline at enterprise scale (300,000 legal contracts)'; safety: 'Your application generates code that gets executed — how do you prevent malicious code generation/execution?'. Also lists classic SD still asked at Amazon/Databricks (GitHub Actions, Slack, feeds, Uber, KV store, rate limiter, Stripe payments, 1B-notifications/day system) and troubleshooting variant 'p95 latency spiked 100ms→2000ms — find bottlenecks fast'.

来源: &lt;[来源链接](https://adilshamim8.medium.com/every-ai-engineer-interview-question-you-need-to-know-in-2026-from-100-real-interviews-b5b7ae4b961a&gt;)

### llmgenai/LLMInterviewQuestions: 100+ LLM interview questions in 15 categories (claimed asked at Google/Nvidia/Meta/Microsoft)
*medium · 频率: very high visibility repo; per-question frequency unknown · 2025*

Categories: prompt engineering & LLM basics; RAG; document digitization & chunking; embedding models; internal working of vector databases; advanced search algorithms; LM internals; SFT; preference alignment (RLHF/DPO); evaluation of LLM systems; hallucination control; deployment of LLM; agent-based systems; prompt hacking; misc; case studies. Sample system-design-flavored questions quoted: 'How to increase accuracy and reliability & make answers verifiable in LLM'; 'What are the architecture patterns for customizing LLM with proprietary data?'; 'How do you build production-grade document processing and indexing pipeline?'; 'Why does quantization not decrease the accuracy of LLM?'; 'What are the techniques by which you can optimize the inference of LLM for higher throughput?'; 'How to accelerate response time without attention approximation like GQA?'; 'Explain ReAct prompting with a code example'; 'OpenAI functions vs LangChain agents'; 'How to build production grade RAG system, explain each component in detail'. Free 100 questions in repo; extended set behind their paid course (masteringllm.com).

来源: &lt;[来源链接](https://github.com/llmgenai/LLMInterviewQuestions&gt;)

### Vector database deep dive for system design interviews (Hello Interview)
*medium · 频率: high (retrieval layer appears inside most LLM SD questions) · 2025*

When 'design semantic search / RAG retrieval layer' comes up: embeddings 128-1536 dims; the nearest-neighbor-at-scale problem; four ANN index families to know: HNSW, IVF, LSH, Annoy; interview discussion points: filtering + hybrid search (dense + keyword/metadata), insert/update/index-maintenance trade-offs, architecture tiers (start with pgvector/Redis extensions, move to purpose-built vector DBs at scale). Page's guidance: most interviews need when/where judgment more than index internals. Complementary free sources: Weaviate RAG evaluation (RAG triad, NDCG/MRR) and PracHub's rubric — chunking default 512 tokens with 50-100 overlap, recursive chunking over fixed-size, two-stage retrieve-then-rerank with cross-encoder, metadata for access control.

**解法**: My inference for a full 'design vector search' answer: two paths — ingestion (parse → chunk → embed → upsert with metadata, async re-embedding on edits) and query (embed query → ANN top-k with metadata pre/post-filtering → cross-encoder rerank). HNSW for high-recall low-latency in-memory; IVF-PQ for billion-scale memory-constrained; discuss recall@k vs latency vs memory triangle, replication + sharding by namespace, and index rebuild strategy.

来源: &lt;[来源链接](https://www.hellointerview.com/learn/system-design/deep-dives/vector-databases&gt;)

### [重点] KV Cache / 推理系统题清单（20 题）
*mixed (easy→hard) · 频率: Inference Engineering / VLLM 合集核心；#492-#495 是 vLLM PagedAttention 系列 · 2026-07*

#376 KV Cache for Efficient Autoregressive Attention [medium] [来源链接](https://www.deep-ml.com/problems/376) | #418 Estimate KV Cache Size from Model Config [medium] [来源链接](https://www.deep-ml.com/problems/418) | #1012 KV Cache Size Estimator MLA vs MHA vs GQA [easy] [来源链接](https://www.deep-ml.com/problems/1012) | #1019 Estimate KV-Cache Memory MHA vs Linear Attention [easy] [来源链接](https://www.deep-ml.com/problems/1019) | #1021 Estimate KV-Cache with GQA and Cross-Layer Sharing [medium] [来源链接](https://www.deep-ml.com/problems/1021) | #416 Compute Attention Memory Traffic and FLOPs [medium] [来源链接](https://www.deep-ml.com/problems/416) | #417 Classify LLM Prefill vs Decode as Compute/Memory-Bound [medium] [来源链接](https://www.deep-ml.com/problems/417) | #435 KV Cache Memory Budget and Eviction Policy [medium] [来源链接](https://www.deep-ml.com/problems/435) | #436 KV Cache Tiered Offloading Simulator [medium] [来源链接](https://www.deep-ml.com/problems/436) | #492 PagedAttention: Block-wise Attention [hard] [来源链接](https://www.deep-ml.com/problems/492) | #493 Virtual Memory System for KV Cache [medium] [来源链接](https://www.deep-ml.com/problems/493) | #494 Copy-on-Write Memory Sharing for LLM Sampling [medium] [来源链接](https://www.deep-ml.com/problems/494) | #495 Analyzing Memory Fragmentation in LLM Serving [easy] [来源链接](https://www.deep-ml.com/problems/495) | #1011 Pre-allocated Sliding KV Cache Update [hard] [来源链接](https://www.deep-ml.com/problems/1011) | #1014 KV Cache Estimator with Sliding Window Attention [medium] [来源链接](https://www.deep-ml.com/problems/1014) | #1023 Build Causal Mask with Position Offsets for Cached Attention [medium] [来源链接](https://www.deep-ml.com/problems/1023) | #1041 Truncate KV Cache for Sliding Window Attention [medium] [来源链接](https://www.deep-ml.com/problems/1041) | #1053 Sliding Window KV Cache Truncation [medium] [来源链接](https://www.deep-ml.com/problems/1053) | #1032 Tokens-per-Second Throughput from Inference Intervals [medium] [来源链接](https://www.deep-ml.com/problems/1032) | #1036 Trim Input Tokens to Fit Model Context Window [medium] [来源链接](https://www.deep-ml.com/problems/1036)

**解法**: #418 KV cache 大小=2(K,V)·layers·seq·kv_heads·head_dim·dtype_bytes·batch；GQA/MLA 通过减少 kv_heads / 潜在维压缩显著降内存。#492 PagedAttention：把 KV 分块存非连续物理块，用 block table 映射逻辑→物理，attention 按块遍历——推断解法，对候选人做系统方向很对口。

来源: &lt;[来源链接](https://www.deep-ml.com/problems/492&gt;)

### Frontier-lab tribal-knowledge quiz questions (workatafrontierlab.com)
*hard · 频率: site claims these represent recurring frontier-lab interview themes · 2026*

Six verbatim questions billed as what frontier labs (OpenAI/Anthropic/DeepMind-style) test: (1) 'Your 70B model training is at 40% MFU. Walk me through where the other 60% is going.' (2) 'We need to serve this model at 200 tokens/sec per user. What's your KV cache memory budget and how does it constrain batch_size?' (3) 'Why does Chinchilla recommend a different compute-optimal ratio than Kaplan's original scaling laws?' (4) 'Your model's loss spikes at step 50k. Here's the training log. Diagnose it.' (5) 'Explain why speculative decoding gives exact samples from the target distribution, not approximate ones.' (6) 'This operation runs at 2 TFLOPS on an A100 rated for 312 TFLOPS. Is that a problem? Why or why not?' Topic areas: KV cache/gradient checkpointing/OOM debugging, FSDP/ZeRO-3/parallelism, prefill vs decode/PagedAttention, roofline model, numerical stability, scaling laws.

**解法**: My inference: (1) MFU losses: communication (all-gather/reduce-scatter bubbles), pipeline bubbles, data-loading stalls, kernel launch overhead/non-fused ops, recomputation from activation checkpointing, stragglers/restarts. (2) KV bytes/token = 2· $n_{layers}$ ·`n_kv_heads`· $d_{head}$ ·bytes; multiply by context len × batch — batch_size bounded by (GPU mem − weights − activations)/KV-per-seq; GQA/MQA, quantized KV, paged KV raise the bound. (3) Kaplan under-trained: fixed cosine schedule + smaller models led to params-heavy optimum; Chinchilla shows ~20 tokens/param, scale data with params equally. (4) Loss spike: check for bad data shard, lr/warmup schedule boundary, fp16/bf16 overflow (check grad-norm spike first), optimizer state corruption after restart; mitigations: skip batch, grad clipping, lower lr, switch to bf16. (5) Speculative decoding uses rejection sampling — accept draft token with prob min(1,  $p_{target}$ / $p_{draft}$ ), resample from normalized residual on reject, provably yielding the target distribution. (6) Not necessarily — the op is memory-bound (low arithmetic intensity); compare against roofline: bandwidth-limited ops (elementwise, small GEMV in decode) can't hit peak FLOPS; fix via fusion/batching, not more compute.

来源: &lt;[来源链接](https://www.workatafrontierlab.com/&gt;)

### Generative AI system design 9-step framework + 8 worked questions with token economics (System Design Handbook)
*medium · 频率: prep compilation · 2026*

Framework: clarify use case → estimate load & token budget → high-level architecture → RAG deep dive → model interaction patterns (streaming, function calling, routing, sampling) → trade-offs/governance/cost → bottlenecks/observability → security/compliance → wrap-up. Worked questions: 'How would you reduce token costs in an LLM-powered product at scale?' (prompt trimming/templating, semantic prompt caching, route low-risk queries to cheaper models, per-feature token monitoring); 'How do you detect and mitigate ungrounded outputs?' (RAG grounding, classifier/zero-shot flagging, confidence scoring, HITL); 'Design a fast low-latency LLM autocomplete' (edge-hosted small models, 100-200 token completions, stream immediately, warm GPU pools, debounce keystrokes, speculative decoding, <500ms target); 'Protect against prompt injection'; 'Monitor and debug GenAI in production' (tokens/request, P50/P95/P99, RAG hit rate, toxic-output alerts, audit logs by model version); 'Internal documentation Q&A with freshness' (async re-embedding on edits, metadata filtering, snapshot expiry); 'Biggest LLM scaling challenges' (tokens are the scaling unit; GPU throughput bottleneck); 'Fine-tune vs prompt-engineered RAG for domain chatbot' (default RAG, fine-tune later from production logs). Reference numbers: 100K DAU × 10 interactions × 2K tokens = 2B tokens/day; avg 23K tokens/sec, peak 70K/sec (3×); GPT-4 Turbo ~&#36;13K/day; ~40 tok/s per GPT-4 request vs 150-300 tok/s LLaMA-3 on A100; RAG retrieves 3-10 chunks.

来源: &lt;[来源链接](https://www.systemdesignhandbook.com/guides/generative-ai-system-design-interview/&gt;)

### LLM System Design: The Complete Guide — prefill/decode physics & KV cache (System Design Handbook)
*medium · 频率: prep compilation · 2026*

Core interview framework for 'design an LLM service' questions: token-based computation replaces request-based reasoning; self-attention is quadratic in sequence length; prefill (parallelizable, compute-bound) vs decode (sequential, memory-bound) split drives latency and cost modeling; KV-cache management is the critical decode-phase component; embeddings/vector DBs as retrieval infrastructure for RAG; variable latency driven by prompt length, batching, and queue dynamics; tensor parallelism and speculative decoding called out as senior-differentiator topics; cost control framed as first-class requirement ('prevent systems from bankrupting organizations through inference expenses').

来源: &lt;[来源链接](https://www.systemdesignhandbook.com/guides/llm-system-design/&gt;)

### 19 AI system design interview questions (alexeygrigorev / AI Engineering Field Guide)
*medium · 频率: compilation from community-reported interviews · 2025*

Typical AI SD questions: design an AI chatbot (ChatGPT/Claude chat service); Document Q&A / RAG system; AI co-pilot like GitHub Copilot; Hospital voice assistant (noise, privacy, latency, domain vocabulary); legal contract generation with compliance; AI-powered candidate sourcing; system to process 10K user uploads/month (payslips, IDs, references); doctors auto-sending billing info to insurers from patient notes; fraud detection; ChatGPT cross-conversation memory feature; multi-step agentic workflow (meeting scheduling, code review, email campaigns); content/policy violation detection; unified query engine across email/calendar/docs/chat; Perplexity-style real-time LLM search engine. Near-AI/platform questions: real-time vs batch data updates; ingesting structured/unstructured/event data; scalable image-generation pipeline for millions of users; distributed job queue for 100K+ GPU training jobs with preemption and checkpointing; large-scale model deployment system (serving, GPU scaling, versioning, result caching). Repo positions 'AI system design' as a distinct interview category from classic MLSD. Companion files in same repo: 01-theory.md, 02-coding.md, 03-project-deep-dive.md, 05-behavioral.md, 06-home-assignments.md.

来源: &lt;[来源链接](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/questions/04-ai-system-design.md&gt;)

### Chip Huyen's 27 open-ended ML systems design exercises (free online)
*medium · 频率: classic canon; individual questions widely reused by interviewers · 2019*

Full list of 27 questions, e.g.: Duolingo story-difficulty measurement and difficulty editing; credit-card fraud detection from labeled purchases; replacement-item recommendation for out-of-stock e-commerce; Twitter who-to-follow + cold start + limitations of data-driven recsys; Google related-searches generation; Google Images-style image retrieval; trending hashtags; Quora answer ranking + compute cost; Airbnb top-10 rental search; texting autocompletion; StackOverflow similar-questions dedup; Lyft/Uber pool rider matching; estimate % of real high schools listed on Facebook + deploy invalid-school detection at scale; trigger-word ('activate') detection in 10s audio; Netflix-clone watch-abandonment prediction (tired of show vs taking a break); Facebook birthday estimation without direct data; language identification; Zillow house-price prediction + city-level investment decision; iPhone next-app prediction at 90% accuracy; nickname→real-name mapping (Pete/Andy/Nick/Rob); minimize e-commerce time-to-purchase; hotel-booking chatbot; extractive QA over large document collections; 'jaguar' animal-vs-car word sense disambiguation; portfolio stock-swap decision; triangle/circle/square recognizer; CIFAR-10 open-set recognition (is image in the 10 classes or not). Companion to her ML Interviews Book (200+ knowledge questions at huyenchip.com/ml-interviews-book/).

来源: &lt;[来源链接](https://huyenchip.com/machine-learning-systems-design/exercises.html&gt;)

### Exponent public ML-engineer system design question bank with company tags
*medium · 频率: company-tag counts shown per question (e.g. 'Anthropic + 7 others') · 2026*

Publicly visible question titles + company attributions: 'Design an inference batching system for a single GPU' (Anthropic +7 others); 'Design an ML experiment tracking and analysis platform' (Google); 'Design an evaluation framework for ads ranking' (Meta +2); 'Design a next word prediction system' (Meta); 'Design an end-to-end ML solution to detect ads selling weapons' (Meta +2); 'Design TikTok' (Meta, Google +4); 'What metrics would you track to evaluate the performance of your ML pipeline?' (Perplexity AI); 'Design a product recommendation system' (Meta, Reddit, Pinterest +3); 'Implement a streaming database with given constraints' (Anthropic); 'Design a denoising system for sounds' (Google); 'Design an agentic AI system that can autonomously adapt to new tasks' (Anthropic); 'Design a language detection system' (Google); 'Design a system to detect bot players' (Roblox); 'Design a personalized news ranking system' (Meta); 'Design a fake news detection system' (Meta +1); 'Design Facebook Marketplace' (Meta); 'Design a monitoring system for TikTok' (TikTok). Full bank claims 150+ MLSD practice questions (rest behind login).

来源: &lt;[来源链接](https://www.tryexponent.com/questions?role=ml-engineer&type=system-design&gt;)

### Exponent 6-step MLSD framework + example questions by category (2026 guide)
*medium · 频率: prep compilation with company attributions · 2026*

Framework (45-min budget): define problem (8m) → data pipeline (8m) → model architecture (8m) → train & evaluate (8m) → deploy/serve/monitor (8m) → wrap-up (5m). Example questions: 'Design a product recommendation system' (Meta, Pinterest); 'Design Netflix Top Picks'; 'Recommend similar artists on Spotify'; 'Design an evaluation framework for ads ranking' (Meta); 'Design YouTube Search'; 'Design a personalized news ranking system'; 'Detect the language of a text input'; 'Design a fake news detection system'; 'Design an automated comment moderation system'; 'Design a spam detection system on Pinterest'; 'Design a fraud-detection system for Stripe'; 'Design visual search for Pinterest'; 'Design an automatic recycling bin'; 'Design a stock-prediction system from Reddit' (JP Morgan); 'Design YouTube advertising'; 'Design TikTok For You page'; 'Design a monitoring system for TikTok'. Common mistakes: rushing past requirements, hunting for the 'right' answer instead of justifying trade-offs, defaulting to SOTA over practical v1, skipping evaluation/validation.

来源: &lt;[来源链接](https://www.tryexponent.com/blog/machine-learning-system-design-interview-guide&gt;)

### 21 LLM system design Q&A flashcard set (Dr. Sanjay Kumar, Medium)
*easy · 频率: prep compilation · 2025*

Questions with answer sketches: what is LLM system design; explain RAG's role; optimize inference for low latency + high throughput (quantization, caching, batching, distillation, GPU/TPU); NFRs for LLM systems (<1s latency, autoscaling, fallbacks, bias/safety); design a customer-support chatbot case study (React + RAG + vector DB + LangChain + FastAPI + quantized model + Redis + monitoring); handle hallucinations/bias; cloud vs edge deployment; monitoring/eval tools (Prometheus/Grafana, toxicity APIs, A/B); cost-performance balance (tiered models, cold starts, spot instances); prompt engineering for consistency; design rate limiting for LLM APIs (token bucket, priority queues for premium users); quantization trade-offs (fp32→int8, ~1-2% accuracy loss); zero-downtime LLM version rollout (blue-green, shadow testing, canary); design a multi-agent LLM system (router classifies → specialized models, orchestrator, JSON passing, fallback logic); reduce GPU costs (distillation, sparse MoE, spot, caching); feature prioritization for a support bot; LLM project ROI; ethical risks; handling incorrect legal advice (keyword routing to humans, disclaimers, audits); design 'Chat with PDF' (extract → chunk → embed at upload → RAG → cache); scale an LLM app 100→1M users (stateless APIs + K8s, CDN, read replicas, sharding, autoscaling).

来源: &lt;[来源链接](https://skphd.medium.com/llm-system-design-interview-questions-and-answers-2a7a16212492&gt;)

### Book: 'Generative AI System Design Interview' (Ali Aminian & Hao Sheng, ByteByteGo, Nov 2024) — canonical 10-question set
*medium · 频率: the de-facto standard prep books for MLSD/GenAI SD rounds · 2024-11*

Chapter/question list: (1) Introduction + 7-step GenAI SD framework; (2) Gmail Smart Compose; (3) Google Translate; (4) ChatGPT: personal assistant chatbot; (5) Image captioning; (6) Retrieval-Augmented Generation; (7) Realistic face generation; (8) High-resolution image synthesis; (9) Text-to-image generation; (10) Personalized headshot generation; (11) Text-to-video generation. 280+ diagrams; covers training + serving architecture and trade-offs per system. Companion to Alex Xu/Aminian 'Machine Learning System Design Interview' book whose 10 problems (visual search; Street View blurring; YouTube video search; harmful content detection; video recommendation; Eventbrite event recsys; ad click prediction; Airbnb similar listings; personalized news feed; People You May Know) are summarized free in the junfanz1 notes repo: [来源链接](https://github.com/junfanz1/AI-LLM-ML-CS-Quant-Review/blob/main/System%20Design/ML%20System%20Design%20Interview.md)

来源: &lt;[来源链接](https://www.amazon.com/Generative-AI-System-Design-Interview/dp/1736049143&gt;)

### Educative 'Grokking the Generative AI System Design' course: SCALED framework + case-study list (free TOC + 14 free lessons)
*medium · 频率: prep course (widely referenced) · 2026*

Course structure: fundamentals (evaluation metrics for GenAI, parallelism in GenAI models, inference optimization, RAG vs fine-tuning breakout w/ mock interview); back-of-the-envelope calculations for LLM training and deployment; 6-step 'SCALED' framework for GenAI SD problems; design case studies: text-to-text conversational AI (ChatGPT mock interview), text-to-image (DALL·E mock), text-to-speech (ElevenLabs mock), text-to-video (Sora mock), image captioning, ASR, and RAG system architecture. 2026 edition added modules: LLM serving infrastructure, RAG architectures, agentic orchestration platforms. 14 lessons free; mocks premium.

来源: &lt;[来源链接](https://www.educative.io/courses/generative-ai-system-design&gt;)

### 'Design a conversational AI agent for our enterprise knowledge base' + RAG scoring rubric (PracHub 2026)
*medium · 频率: claimed recurring across GenAI loops · 2026*

Called 'a recurring prompt in GenAI interview loops.' Strong answer walks a 4-stage RAG pipeline stage by stage naming trade-offs: (1) document ingestion & chunking (parsing strategy, metadata capture); (2) embedding layer (model selection e.g. text-embedding-3-large vs open-source BGE for cost, hybrid search support); (3) retrieval & re-ranking (vector search + cross-encoder); (4) generation & prompt orchestration (streaming output). Evaluation rubric dimensions: framing (state the probabilistic nature; clarify latency/sensitivity/scale), retrieval depth (retrieve-then-rerank, chunking trade-offs: small chunks lack context, large chunks dilute embedding semantics), cost awareness (tokens as budget, semantic caching, model routing), quality/safety (evals, citations, guardrails, feedback loops), trade-off leadership (proactively surface precision-latency-cost tensions). Variants: cost-optimized / latency-optimized / accuracy-optimized RAG designs.

来源: &lt;[来源链接](https://prachub.com/resources/genai-llm-system-design-interview-guide-2026&gt;)

### Hao Hoang 'Top 25 LLM System Design Interview Questions' (free-PDF workbook; content engagement/paywall-gated)
*medium · 频率: 795 reactions/117 comments on LinkedIn; widely shared · 2025-11*

50+ page workbook where each chapter = interview question + the common wrong answer + technical breakdown + one research paper to cite. Topics confirmed from LinkedIn preview: the tokenizer trap in domain-specific training (tokenization mismatch as production failure mode); speculative decoding for lossless acceleration; KV-cache bottlenecks under concurrent inference; the 'alignment tax' in RLHF (alignment-induced latency/quality trade-offs); scaling laws & compute-optimality. Full 25-question list not retrievable (Substack paywall; LinkedIn post requires engagement to get PDF; archive.org unreachable from this environment). Companion paywalled post: 'Top 25 ML System Design Interview Questions' (2026-01-01, same substack). His free 'Top 50 LLM Interview Questions' (May 2025) knowledge-question set is mirrored openly at [来源链接](https://gist.github.com/rajesamp/c6a509d2f6be84db6cf5d509eabaa08d)

来源: &lt;[来源链接](https://www.linkedin.com/posts/hoang-van-hao_top-25-llms-system-design-interview-questions-activity-7396785599728422913-EedS&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/theory-and-mlsd.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/theory-and-mlsd.md)。作者整理资料；许可和第三方来源范围见阅读指南。

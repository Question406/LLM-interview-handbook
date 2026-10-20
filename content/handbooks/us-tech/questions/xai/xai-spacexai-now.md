---
id: xai-spacexai-now
section: xai
order: 0
level: S
title: "xAI / SpaceXAI: what they are shipping now (Grok, Cursor, Colossus)"
quick: "xAI is now SpaceXAI, a SpaceX subsidiary. For why xAI, name one live surface (Grok tools, Grok Build, Grok Bot, Cursor) and one failure mode in it."
tags:
  - xAI
  - SpaceXAI
  - Grok
  - Cursor
  - Grok Build
  - Post-training
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-29
sources:
  - title: xAI joins SpaceX
    url: https://x.ai/news/xai-joins-spacex
    type: primary
  - title: SpaceX acquires xAI (Reuters)
    url: https://www.reuters.com/business/musks-spacex-merge-with-xai-combined-valuation-125-trillion-bloomberg-news-2026-02-02/
    type: secondary
  - title: Introducing Grok Build
    url: https://x.ai/news/grok-build-cli
    type: primary
  - title: Workflows in Grok Build
    url: https://x.ai/news/workflows
    type: primary
  - title: Designing Grok Bot for a world of persistent agents
    url: https://x.ai/news/designing-grok-bot
    type: primary
  - title: Grok Bot overview
    url: https://docs.x.ai/grok-bot/overview
    type: primary
  - title: Grok 4.7
    url: https://docs.x.ai/developers/grok-4-6
    type: primary
  - title: Context compaction
    url: https://docs.x.ai/developers/advanced-api-usage/context-compaction
    type: primary
  - title: Prompt caching
    url: https://docs.x.ai/developers/advanced-api-usage/prompt-caching
    type: primary
  - title: Grok 4.20 Multi-Agent
    url: https://docs.x.ai/developers/models/grok-4.20-multi-agent-0309
    type: primary
  - title: Cursor is now a part of SpaceX
    url: https://cursor.com/blog/joining-spacex
    type: primary
  - title: xAI tools overview
    url: https://docs.x.ai/docs/agents/tools
    type: primary
---

Public facts only. Do not invent cluster topology, job ladders, or unpublished training recipes. The 15-minute screen still uses the xAI name; the product brand on docs is SpaceXAI.

## Corporate surface (say this once, then drop it)

SpaceX acquired xAI on 2 Feb 2026 and kept it as a subsidiary ([x.ai/news/xai-joins-spacex](https://x.ai/news/xai-joins-spacex); Reuters reported the all-stock deal at about 250 billion dollars for xAI and 1 trillion for SpaceX). Public writing later uses the SpaceXAI name. Cursor's own post says the Anysphere acquisition closed 14 Aug 2026 and that the team would work on Grok Build, Grok Bot, the Grok API, and Cursor.

Interview use: one sentence of context if they ask "do you mean SpaceX or xAI." Then name a team problem. Recruiters still write xAI on the calendar.

## Product surfaces that map to research questions

| Public surface | What it actually is | Research problem you can name | Handbook |
| --- | --- | --- | --- |
| Grok tools / DeepSearch | Server-side `web_search`, `x_search`, code execution | Freshness, citations, empty-search honesty, tool-wait wall clock | `xai-search-agent`, `xai-tool-use` |
| Grok 4.7 (API docs) | Frontier model for coding and agentic work; 500k context; `prompt_cache_key` / `x-grok-conv-id`; compaction on long loops | Prefix-KV hit vs dropping verbose tool traces | `xai-prompt-cache` |
| Context compaction | `POST /v1/responses/compact` turns prior turns into an opaque item; does not rescue an already over-limit request | What to keep vs delete in a long agent; proxy/delay if you study online KV | compaction docs |
| Grok Build | Terminal coding agent; plan/diff; subagents; AGENTS.md / skills / MCP | Coding-agent post-training, executable verifiers, reward hacking | `xai-agent-loop` |
| Grok Build workflows | Host fans a job across many child agents (public post: budget 128, up to 1,024), independent checks, one report | Multi-agent credit assignment, verification, context isolation per child | workflows post |
| Grok 4.20 multi-agent | Documented model id with 1M context for parallel research | Same class of problem as workflows, different serving contract | model card |
| Grok Bot | Named persistent agents on a **user-scoped** cloud VM; Bots share files/logins; screens are not security boundaries | Process isolation, shared mutable state, computer-use confirmation | Bot docs |
| Cursor / Composer | IDE + agentic coding models; Cursor said the SpaceXAI compute partnership was to scale RL / continued pretrain | Reward on diffs, evals, data flywheel | Cursor post |
| Colossus | Public supercompute story | Fault domains and consistent checkpoints, not your personal GPU count | `xai-colossus` |

Two serving axes people mash together:

- **Prompt cache** reuses already-computed KV for an identical token prefix. Broken by template drift, tool-schema reorder, missing `prompt_cache_key`.
- **Compaction** *deletes* verbose history into a blob so the next call is shorter. High compression with a task drop means you deleted an observation the later tool still needed.

Token speculative decoding hides decode. Tool-call speculation hides tool I/O. Do not fuse those two sentences.

## Named team directions (for "why xAI")

Job posts and product pages that exist in public, pick **one**:

- **Coding agents / Grok Build / Cursor.** Reasoning RL, dataset generation, evals, "AI-native software engineering stack." After the phone screen, posted loops often include a coding assessment, two post-training problem sessions, and a work presentation.
- **Reasoning / post-training.** Fine-tune and RL on a pretrained base; they test whether you can formulate a data/reward problem, not whether you memorized Colossus headlines.
- **Search / DeepSearch / Grok tools.** Real-time web and X as first-class tools.
- **Inference / long agent loops.** Cache, compaction, 500k–1M windows, multi-agent fan-out.
- **Grok Bot / computer use.** Durable VM, shared account state, approvals.
- **Training infra / Colossus.** Only if that is the JD. PhD LLM candidates who have never owned a 10k-GPU run should not volunteer this as the home team.
- **Video gen / Imagine.** Exists as a product line. Skip unless that is the posting.

"I like Grok" and "largest cluster" fail this round. Name the row above and one failure mode (wrong tool call, incomplete search set, verifier that cannot execute, compaction that drops a future observation).

## What you must not claim

- Internal router, unpublished MoE recipe, Cursor-internal reward weights.
- That SpaceX rockets are your research interest unless the JD is that org.
- Tesla occupancy / hydra nets as Grok work. Those cards stay in this chapter as contrast only.
- Dollar figures, headcount, or "we will train on Colossus next month" as personal facts.

## Follow-ups

- **Cache or compact?** Cache if the prefix is stable and you still need every token. Compact if tool traces dominate and the next step only needs salient state. Compaction cannot fix `context_length_exceeded`.
- **Why workflows mention "independent skeptics"?** A single agent both finding and grading a bug is the cheap path; the public post sells a second pass that checks claims against sources. Same shape as executable verifiers vs model-guessed expected output.
- **Grok Bot shared computer?** Account-level isolation, not per-Bot. If they ask process vs thread, this is the product example: shared filesystem and cookies are shared memory with a wide blast radius.

---
id: xai-screen-15min
section: xai
order: 0
level: S
title: "xAI: 15-minute video screen, clock and cut reasons"
quick: >-
  Most reported rejections happen here. Budget: 2–3 min recent-first intro, 5–8 min one
  technical decision, 1–2 min a named team (Build / post-training / search / inference /
  Bot). Optional CS verbal or BankAccount race. If the interviewer is 10 min late, use the
  90-second project pitch. Confirm with the coordinator whether coding is in this slot.
tags:
  - xAI
  - 15-minute screen
  - Interview process
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-29
sources:
  - title: The xAI 15-Minute Phone Screen (Complete Guide)
    url: https://aceoffer.app/interviews/xai_phone_screen_guide
    type: secondary
  - title: xAI Interview Question Bank (1Point3Acres)
    url: https://www.1point3acres.com/interview/problems/company/xai
    type: secondary
  - title: xAI Exceptional Engineer (SWE) Interview Guide
    url: https://www.tryexponent.com/guides/xai-exceptional-engineer-swe-interview
    type: secondary
  - title: Member of Technical Staff, Coding Agents / Post Training (job loop)
    url: https://simplify.jobs/p/1bfe5ce2-5b08-407c-8528-525c646ffee4/Member-of-Technical-Staff
    type: secondary
---

Interviewer-dependent, blunt, often Google Meet. Product background for "why xAI" is `xai-spacexai-now`. Memory KV / race mechanics are `xai-kv-txn`.

## Standard 15 minutes

| Slice | What they want | Cut if |
| --- | --- | --- |
| Self-intro, 2–3 min | Current role first. They interrupt with "focus on recent." | Chronological resume from undergrad |
| One project, 5–8 min | Bottleneck, why this method, which alternative died, at API / kernel / training-contract grain | Project-management plot ("we aligned stakeholders") |
| Why xAI / what you want, 1–2 min | A real direction: Grok inference, training infra, agentic RL, video gen, supercompute, **or** (for LLM PhDs) Grok Build / post-training / search / compaction / Grok Bot | "I like Grok" |
| Optional | Process vs thread, shared memory, GIL, async vs threading; or live BankAccount race | Freeze, then recover slowly. Clock has no recovery |
| Reverse Q | You have heard their team | Asking if onsite is LRU / how many LC mediums |

Posted MTS loops after a pass: CV + exceptional-work statement, this screen, then often coding + two post-training sessions + a short talk. Researcher / PhD screens may stay on papers. Do not assume.

## Tactics they actually use

**Late interviewer.** Arrives with 5 effective minutes and still wants the full content. Open with the 90-second project pitch (problem, constraint, the decision you own, one failed alternative, one metric that would falsify it), then 45 seconds on a named team. Stop.

**Coordinator note.** "...as well as a coding question" means prepare `xai-kv-txn` and the live-debug variant below. If the note is papers-only, do not burn the deep-dive on mutexes.

**Two altitudes, pick live.** Same project told as (1) training/reward contract and (2) serving/KV/process contract. Let their first follow-up choose. Prepare a second paper if they are clearly search-eval or coding-verifier.

**Problem language.** State assumptions as questions, wait, restate the contract, then solve. "I'll assume deposit is lost-update on a shared `balance`" without waiting is how a correct fix still fails the round.

**Hesitation on verbal CS.** A pause plus a correct answer still reads as fail because there is no time to rebuild confidence. If you do not know GIL, say so in one clause and give the OS answer you do know.

## 90-second project pitch (template)

Problem in one sentence (wall-clock sits on tool I/O / search set is incomplete / verifier cannot execute). Constraint that made the obvious method fail. The decision you made (algorithm, loss, isolation, or API). Alternative you killed, with the failure condition. How you would know you were wrong in production (Hit@1 up, wall-clock flat; compression up, task down).

No roadmap, no team size, no "we shipped v2."

## Optional BankAccount

They paste `deposit` that reads balance, `sleep`s, writes back. Shared state is `balance`. Critical section is the whole read-modify-write; sleep only widens the window. Two threads read 100, both write 110, one deposit vanishes. Fix: mutex around the RMW, or CAS loop. If they forbid editing the original class, wrap it. Say which lines the lock covers. Details: `xai-kv-txn`.

## Live-debug variant (booked 15, runs 30–45)

CoderPad, failing unit tests, Python (sometimes the same BankAccount). Difficulty is usually easy. People still fail by leaving an exception path unhandled when time ends. Order: restated contract, smallest failing test, fix, then scan remaining `except` / `None` / empty list cases before you declare done.

## Follow-ups

- **PhD vs SWE?** Same clock. Grain of the deep-dive changes: GRPO / reward / eval protocol vs lock granularity. Job posts for Coding Agents still include a later coding assessment.
- **Tesla cards in this chapter?** Contrast only. Do not use occupancy nets as your xAI story.
- **Ethics / mission slogans?** Ground in empty-search and citation contracts (`xai-search-agent`). Do not say you applied because there is no ethics round.

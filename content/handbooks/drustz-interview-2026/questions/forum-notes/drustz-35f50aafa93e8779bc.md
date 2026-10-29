---
id: drustz-35f50aafa93e8779bc
section: forum-notes
order: 87
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 6: Deep Dive into Key Components'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 6: Deep Dive into Key Components'
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## Step 6: Deep Dive into Key Components

In an interview, focus on these hard problems.

### 1. Handling 10MB Prompts

**The Problem:** 10MB of text makes browsers slow. Also, AI models cannot read 10MB (context window limits).

- **Browser Fix:** Use **Monaco Editor** with "virtual scrolling." This only draws the text you can currently see on the screen, not the whole file.
- **Execution Fix:**

Calculate the number of tokens using a tokenizer library.
- **Validate:** If the prompt is 10MB (2.5M tokens) but the model only supports 200K tokens, **block the request**. Show an error: "Prompt too long."
- The 10MB limit is for *storage and editing*, not for running the AI.

### 2. Version Control (Snapshots + Diffs)

**The Problem:** If a user saves 1000 times, storing 10MB 1000 times is too expensive.
**The Solution:**

- **Version 1:** Save full text (Snapshot).
- **Version 2:** Save only the changes (Diff).
- ...
- **Version 10:** Save full text again (Snapshot).
- **Reconstruction:** To read Version 5, the system takes Snapshot 1 and adds the changes from V2, V3, V4, and V5.

### 3. Syncing Multiple Tabs

**The Problem:** A user has the same prompt open in two tabs.
**The Solution:**

- **Same Device:** Use `BroadcastChannel` API. If you type in Tab A, Tab B updates automatically.
- **Conflict:** If Tab A and Tab B try to save different things at the exact same time, use **Optimistic Locking**. The server checks the version number. If they don't match, ask the user which version to keep.

### 4. Search Strategy

**The Problem:** Searching the full text of huge prompts is slow and expensive.
**The Solution:**

- **Fast Search:** Store the first 500 characters in PostgreSQL. This is free and fast.
- **Deep Search:** Use **Elasticsearch** for the full text, but truncate prompts to 100KB to save money. Most important keywords are usually at the start.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。

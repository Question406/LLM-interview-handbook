---
id: drustz-c0c339a193fcaf98a1
section: forum-notes
order: 141
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · The Challenge
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · The Challenge
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
## The Challenge

Design an HTTP API for a Large Language Model (LLM) service. Users send single requests, but the system must group these requests into batches to run efficiently on GPUs.

### The Problem Requirements

You have a backend function you must use. You cannot change it.

```python
def batchstring(inputs: list[str]) -> list[str]:
    """
    Processes a batch of string inputs and returns string outputs.

    Constraints:
    - Input size: 1-100 strings per batch
    - Output size: 1-100 strings (one per input)
    - Latency: ~100ms per batch (fixed time, does not change with size)
    - Concurrency: Each GPU instance can only process ONE batch at a time
    """
    # Fixed implementation - you cannot modify this
    pass
```



### What We Need to Build

You need to design a system that:

- Takes single requests from users (via HTTP).
- Groups them into batches inside the system.
- Sends these batches to GPUs.
- Matches the answers back to the correct users.
- Keeps the system fast (low Latency).

### Questions the Interviewer Might Ask

Be ready for questions like:

- **Scale:** How many requests per second (RPS)? (e.g., 100 vs 10,000).
- **Speed:** How fast must the response be? (e.g., P95 < 500ms).
- **Users:** Do paid users get priority?
- **Hardware:** How many GPUs do we have?
- **Routing:** How does the server know which user gets which answer?
- **Errors:** What happens if a GPU crashes?

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。

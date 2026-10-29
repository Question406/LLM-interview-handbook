---
id: drustz-6947deaf76ffc4411f
section: forum-notes
order: 72
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

In an interview, you can't design everything perfectly. Focus on these 3 critical areas.

### Strategy 1: Grouping Requests (Batching)

This is the most important part. We trade a tiny bit of waiting time for much better efficiency.

**The Problem:** When should we send a batch to the GPU?

**Approaches:**

**Option A: Fixed Batch Size (Efficient)**

- Wait until you have exactly 32 requests.
- **Pros:** GPU works perfectly.
- **Cons:** If traffic is low, the first user waits a long time for 31 other people.
**Option B: Timeout-Based (Fast - Recommended)**

- Wait until you have 32 requests OR until 40ms has passed.
- **Pros:** Fast even during low traffic.
- **Cons:** Sometimes sends small batches (less efficient).
**Option C: Adaptive**

- Change the batch size and timeout automatically based on traffic.
- **Pros:** Best of both worlds.
- **Cons:** Hard to build.
**Discussion Points:**

- Larger batches = Better GPU use, but slower for users.
- Smaller batches = Faster for users, but wastes GPU power.

### Strategy 2: Scaling Up and Down

**The Problem:** Traffic changes all the time. How do we adjust?

**Things to know:**

- **Horizontal Scaling:** Adding more machines.
- **Cold Start:** Turning on a new GPU takes 1-5 minutes. You can't just switch it on instantly.
**Approach:**

- Don't run GPUs at 100%. Aim for 70-80%. This leaves room for sudden spikes while new servers turn on.
- **Scale UP** when:

GPU usage > 80% for 2 minutes.
- Queue has more than 100 items.
- Latency is getting too high.
- **Scale DOWN** when:

GPU usage < 50% for 10 minutes.
- Remove servers slowly so you don't accidentally remove too many.

### Strategy 3: Tracking System Health

**The Problem:** How do you know if the system is broken?

**Metrics to Track:**

- **Utilization:** How hard are the GPUs working?
- **Throughput:** Requests per second.
- **Latency:** How long does a request take? (Track P95 and P99).
- **Queue:** How many requests are waiting?
- **Errors:** How many requests failed?

### Strategy 4: Calculating GPU Needs

**Given:** 1,000 requests/second.

**Factors:**

- **Inference time:** 50ms per batch.
- **Batch size:** 32.
- **Overhead:** It takes time to group requests (~20ms) and move data (~5ms).
**Calculation:**

```text
1. Total time per batch: 50ms (work) + 20ms (wait) + 5ms (move) = 75ms.
2. Batches per GPU per second: 1000ms / 75ms = 13.3 batches.
3. Requests per GPU per second: 13.3 batches × 32 requests = 426 requests.

4. GPUs needed (Raw): 1000 / 426 = 2.35.
5. GPUs needed (Safe limit of 70% usage): 2.35 / 0.7 ≈ 4 GPUs.
```



### Strategy 5: Controlling Traffic Flow

**The Problem:** What if a GPU crashes and the others get overwhelmed?

**Solution: Dynamic Rate Limiting**

You need to limit users based on the *current* health of the system.

- **Green Zone (Queue < 100):** Normal. Accept everyone.
- **Yellow Zone (Queue 100-500):** Warning. Slow down free users.
- **Red Zone (Queue > 500):** Critical. Reject new requests (Error 429).
**Formula:**
If you have 10 GPUs and each can handle 100 RPS, your capacity is 1,000 RPS.
If 5 GPUs break, your capacity drops to 500 RPS. You must immediately lower the rate limit.

### Strategy 6: Caching Answers

**The Problem:** Why calculate the same answer twice?

**Option A: Exact Match (Key-Value Store)**

- If the prompt is exactly the same, return the saved answer.
- **Fast and safe.**
**Option B: Similarity Match (Vector DB)**

- If the prompt is *almost* the same, return a saved answer.
- **Risk:** The answer might be wrong for the new context.
- **Cost:** Calculating similarity takes time. Only use this if saving the inference time is worth the effort.

### Strategy 7: Handling Timeouts and Retries

**The Problem:** A request takes too long. What do we do?

**Timeouts:**

- **Client Timeout:** The user gives up after 5 seconds.
- **Server Timeout:** We stop trying after 4 seconds (to give a clean error before the client gives up).
**Retries:**

- **Client:** Can retry on network errors or Rate Limit errors (429).
- **Server:** If a GPU crashes, try one more time on a different GPU. Do not retry too many times, or you will crash the whole system.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。

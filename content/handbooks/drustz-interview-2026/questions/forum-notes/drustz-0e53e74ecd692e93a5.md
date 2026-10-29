---
id: drustz-0e53e74ecd692e93a5
section: forum-notes
order: 147
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 5: Basic System Architecture'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 5: Basic System Architecture'
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
## Step 5: Basic System Architecture

Here are the main parts of the system.

```text
[User] -> [Load Balancer] -> [API Server 1] -> [Redis Queue] -> [Batcher] -> [GPU]
                                     ^                                        |
                                     |                                        |
                                     L__________[Redis Pub/Sub]_______________|
```



### Component Roles

- **Load Balancer:** Sends user requests to different API servers.
- **API Server:**

Takes the user request.
- Assigns a `request_id`.
- Puts the request in the **Redis Queue**.
- Waits for the answer.
- **Batching Service:**

Takes requests from the **Redis Queue**.
- Groups them into a batch (wait for 32 items or 50ms).
- Sends the batch to a GPU.
- **GPU Worker:**

Runs the `batchstring()` function.
- Returns the result to the Batching Service.
- **Redis Pub/Sub:**

Used to send the answer back from the Batching Service to the API Server.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。

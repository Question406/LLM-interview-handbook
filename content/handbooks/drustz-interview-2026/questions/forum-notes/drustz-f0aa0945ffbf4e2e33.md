---
id: drustz-f0aa0945ffbf4e2e33
section: forum-notes
order: 206
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · 5. Scaling and Important Choices
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · 5. Scaling and Important Choices
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
## 5. Scaling and Important Choices

### Improving Speed

- **Cold Starts:** Use **Warm Pools**.
- **Output Latency:** Use **Kafka** partitioned by `sandbox_id`. This ensures text arrives in the correct order.

### Bottlenecks

- **Sandbox Manager:** If this crashes, no one can run code.

*Fix:* Run multiple copies. Store state in Redis, not in memory.
- **Kafka Load:** 50,000 active streams is a lot.

*Fix:* Use `sandbox_id` as the partition key. Use a cluster of Kafka brokers.

### VM Lifecycle (Saving Money)

Servers are expensive. We need a strict lifecycle.

- **Provisioning:** Creating the container.
- **Warm:** Sitting in the pool, waiting for a user.
- **Running:** User is actively working.
- **Idle:** User hasn't typed in 30 minutes.
- **Terminated:** Shut down to save money.
*Cost Tip:* Give free users a short timeout (5 mins idle). Give paid users a long timeout (30 mins idle).

### Alternatives to Containers

**AWS Lambda / Firecracker:**

- *Pros:* Extremely fast startup (milliseconds). Very secure.
- *Cons:* Harder to set up than Docker/Kubernetes.
- *Verdict:* Use Firecracker if you are building a huge enterprise competitor. Use Kubernetes for a standard system design interview.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。

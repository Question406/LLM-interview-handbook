---
id: drustz-50739e59be4fa6ed6a
section: forum-notes
order: 240
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Design Sora Video Generation Scheduling
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Design Sora Video Generation Scheduling
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
## Design Sora Video Generation Scheduling

### Design Sora Video Generation Scheduling

Design the backend for Sora-style video generation. A client submits a prompt and video settings, your service accepts the job, schedules it onto an external GPU pool, tracks progress, and returns the final video artifact. The hardest part is that **each worker can generate only one video at a time**, and the external GPU pool is elastic and preemptible, so workers may be terminated at any point during generation. This problem primarily tests whether you can design **durable job orchestration**, **capacity-aware scheduling**, and **failure recovery on unreliable compute**.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。

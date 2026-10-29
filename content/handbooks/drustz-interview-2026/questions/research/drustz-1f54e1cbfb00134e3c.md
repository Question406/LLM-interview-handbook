---
id: drustz-1f54e1cbfb00134e3c
section: research
order: 59
level: A
title: Anthropic 系统设计真题：设计高并发 batched LLM 推理 API（含完整需求）
quick: supplemental-research-note · Anthropic 系统设计真题：设计高并发 batched LLM 推理 API（含完整需求）
companies:
  - anthropic
tags:
  - DrustZ
  - supplemental-research-note
  - 公司面试 · 补充研究笔记
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.reddit.com/r/OfferEngineering/comments/1us7dqf/anthropic_system_design_question_design/
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

OfferEngineering 2026-07 完整收录（与 L4 面经'distributed inference API/GPU scheduling and batching for LLM inference workloads'相互印证）。题面：设计服务 LLM 请求的高并发推理 API。客户端提交 prompt+model+生成参数+优先级+是否流式；GPU worker 池有限，核心挑战是 batching——把兼容请求合批提高throughput和 GPU 利用率同时满足交互路径 <500ms-1s 延迟目标。功能需求：同步/流式响应、重试+request ID+幂等、过载时排队/背压/限流/按优先级丢弃。非功能：throughput vs 延迟平衡（等待凑批 vs 尾延迟）、GPU 显存（长 prompt、KV-cache 增长、prefill vs decode 行为差异）、突发流量稳定性、worker 崩溃时受影响请求的安全重试、可观测性（队列深度/批大小/GPU 利用率）。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.reddit.com/r/OfferEngineering/comments/1us7dqf/anthropic_system_design_question_design/)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

---
id: drustz-995dd5ef51def6eeca
section: research
order: 11
level: A
title: >-
  Anthropic L4 SWE onsite 编码轮题目清单（2025 offer 面经）：线程安全缓存/流式 tokenizer 性能
  debug/并发预订系统
quick: >-
  supplemental-research-note · Anthropic L4 SWE onsite 编码轮题目清单（2025 offer
  面经）：线程安全缓存/流式 tokenizer 性能 debug/并发预订系统
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
      https://www.reddit.com/r/InterviewCoderHQ/comments/1tirugm/anthropic_swe_interview_experience_2025_l4_remote/
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

InterviewCoderHQ 详细 offer 面经（L4 remote，6 YoE backend）：技术店面=用 ThreadPoolExecutor 构建 async 处理管线、处理并发安全、debug 性能瓶颈（55-90分钟）。onsite 编码轮三题型：(1) build a thread-safe cache with configurable eviction policy；(2) debug a performance bottleneck in a streaming tokenization system；(3) design and implement a reservation service with concurrency constraints。共同主题：multithreading、async processing、API design、streaming、pipeline debugging。评分看代码可读性、并发正确性、架构决策、debug 方法论，而非时间复杂度。作者称没刷 LeetCode 是正确选择，备考 6 周聚焦 Python 并发原语 + 生产级代码（错误处理/日志）。注：该 sub 由面试辅导产品运营，细节与多个独立报告吻合但属二手整理。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.reddit.com/r/InterviewCoderHQ/comments/1tirugm/anthropic_swe_interview_experience_2025_l4_remote/)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

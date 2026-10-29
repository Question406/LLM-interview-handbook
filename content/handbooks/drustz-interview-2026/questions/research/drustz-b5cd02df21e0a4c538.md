---
id: drustz-b5cd02df21e0a4c538
section: research
order: 122
level: A
title: Memory Allocator：75min 店面设计内存分配器（关联帖 1179374）
quick: supplemental-research-note · Memory Allocator：75min 店面设计内存分配器（关联帖 1179374）
companies:
  - openai
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
    url: 'https://www.1point3acres.com/bbs/thread-1179374-1-1.html'
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

thread-1179374（2026-06-06,《OAI screen》, Positive/Easy/Pass, hardware 相关 infra 岗）Wayback 快照回复区还原：题为设计 memory allocator，要求 malloc/free、free block 合并（coalescing）、减少碎片（fragmentation reduction）；楼主用 C++，『每次从头 linear scan 来 malloc 和 coalesce free memory block』达到 O(N)；75 分钟轮，仅最后 5 分钟 Q&A。官方题库：memory-allocator，coding，频率 medium，6 个来源帖，75min phone screen，首报 2025-12-01，last_asked 2026-06-11。相关 OJ 变体标题：'In-Memory Memory Allocator with malloc/free, First-Fit and Best-Fit'、'Implement malloc and free with First-Fit Allocation and Discuss Best-Fit Optimization'、'Design a Memory Allocator with Coalescing'。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.1point3acres.com/bbs/thread-1179374-1-1.html)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

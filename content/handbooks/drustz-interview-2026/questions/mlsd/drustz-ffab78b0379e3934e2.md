---
id: drustz-ffab78b0379e3934e2
section: mlsd
order: 22
level: A
title: >-
  06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 06 · Search /
  Retrieval Post-training：Exa 类 AI Web Search
quick: >-
  作者文档章节 · 06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 06 ·
  Search / Retrieval Post-training：Exa 类 AI Web Search
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md
    type: primary
---
# 06 · Search / Retrieval Post-training：Exa 类 AI Web Search

⏱ 通读约 35–45 分钟 ｜ 面试前优先背「90 秒开场」「训练目标」「Eval 表」「面试题」

> **三档阅读入口**（别从头读到尾，按你的时间预算选）
> - **Exa 面试前 3 分钟** → §一 90 秒开场 + §十五 面试前一页速记 + [13 · Exa 公司卡](?book=drustz-interview-2026&section=mlsd&question=drustz-8542776e5697e93de9)
> - **只有 15 分钟** → §一 + §五 为什么 click ≠ positive + §六 negative sampling + §十四 15 分钟白板模板
> - **完整（Day 2 下午）** → §一/§四/§五/§六/§七/§八/§九 + §十五
>
> 这题的两个题眼：**§五 点击的四种偏差**、**§六 hard negative 的 false-negative 陷阱**（top-k 里混着未标注的相关文档，直接当负例会伤召回）。Exa 自己在博客里讲过「从网页挖 embedding 训练数据的新方法」，§四 就是这个问题的正面回答。

这篇回答的不是「如何接一个向量数据库」，而是：**如何训练、评估并上线一个服务 AI agent 的 web search system**。它同时覆盖两类经常被混在一起的问题：

1. **Search stack 的模型训练**：query understanding、retriever、reranker、snippet/excerpt、quality/freshness。
2. **Search agent 的 post-training**：让 LLM 学会何时搜、搜什么、读哪些页面、何时停止、如何引用。

> 核心原则：先把 relevance、evidence、freshness 和 task success 分成独立可测的目标，再决定哪些组件共享训练信号。点击率不是 relevance，最终答案分数也不能替代 retrieval recall。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/06_search_post_training.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md)。作者整理资料；许可和第三方来源范围见阅读指南。

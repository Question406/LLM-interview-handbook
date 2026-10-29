---
id: drustz-a1cd72bbcacd2f0e8a
section: mlsd
order: 68
level: A
title: 09 · ML System Design 题库 · C. Code Review LLM（6 题）
quick: 作者文档章节 · 09 · ML System Design 题库 · C. Code Review LLM（6 题）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/09_question_bank.md
    type: primary
---
## C. Code Review LLM（6 题）

### C1. 设计一个能发现 bug 并给出 comment 的 code-review LLM。

答题锚点：PR diff + repo context + tests/analyzers；detection/localization/generation 分解；repo/time split；precision budget；cascade + verifier。详见 [04_case_code_review_llm.md](?book=drustz-interview-2026&section=mlsd&question=drustz-7ba2d317f214182b45)。

### C2. GitHub 历史 comment 都能作为正例吗？

答题锚点：style/nit/duplicate/obsolete/incorrect；resolution、subsequent patch、reaction、expert rubric；未评论代码不是负例。

### C3. 你会用什么 reward function？

答题锚点：hard security/build；issue correctness、localization、actionability、non-duplicate、severity；tests/static analysis；false-positive/verbosity/cost penalty；provenance 分开。

### C4. Unit tests 通过能否作为 RLVR 的全部 reward？

答题锚点：tests incomplete、overfit/hard-code、nonfunctional/security/style；hidden tests、static analysis、semantic review、patch minimality、held-out repos。

### C5. 如何评估 bot 是否减少 reviewer 工作？

答题锚点：comment precision/serious bug recall + time-to-review + accepted/actioned + reviewer override/fatigue；randomized rollout，不能只看 comment 数。

### C6. 如何把成本降 10 倍？

答题锚点：incremental diff/context retrieval、static tool first、small classifier/router、cache repo embeddings、async deep review、limit candidates/tokens、大模型只处理 uncertain/high-value。

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/09_question_bank.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/09_question_bank.md)。作者整理资料；许可和第三方来源范围见阅读指南。

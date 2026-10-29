---
id: drustz-d90c68aa3f87c2361c
section: mlsd
order: 32
level: A
title: >-
  06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 7.3 Excerpt /
  evidence selector 与 answer model
quick: >-
  作者文档章节 · 06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 7.3
  Excerpt / evidence selector 与 answer model
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
## 7.3 Excerpt / evidence selector 与 answer model

对于 agent，返回整页导航栏比低排名更可能浪费 token。训练 excerpt selector：

1. 从人工 evidence span、citation span、answer-bearing passage 得监督。
2. 训练 passage ranker 或 span selector。
3. 给每个 excerpt 保存 URL、page version、char/token offsets。
4. 生成答案后做 claim → span entailment 检查。

Answer model 的 SFT 样本应包含：

```text
question
retrieved evidence with stable source ids
answer with atomic claims
claim → source/span mapping
explicit abstention when evidence incomplete
```



训练时加入四类反例：无答案、相互冲突、过时、恶意 prompt injection。目标不是“总能回答”，而是 evidence 不足时能继续搜或 abstain。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/06_search_post_training.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md)。作者整理资料；许可和第三方来源范围见阅读指南。

---
id: drustz-6925cd066e9abd1ada
section: mlsd
order: 58
level: A
title: 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 十六、Cost model：钱花在哪里、如何降
quick: >-
  作者文档章节 · 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 十六、Cost
  model：钱花在哪里、如何降
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md
    type: primary
---
## 十六、Cost model：钱花在哪里、如何降

### 16.1 Funnel 成本公式

设 raw `B_0` bytes，每 stage 保留率 `r_i`，则 stage `j` 输入：

\[
B_j = B_0\prod_{i<j}r_i
\]

所以便宜、高 recall 的 policy/format/language/obvious spam filters 应尽早；昂贵 OCR/LLM classifier/semantic dedup 放后面。但 rights/safety gate 的顺序由 policy 决定，不能为了省钱先非法处理。

### 16.2 主要成本中心

| Stage | 成本 | 优化 |
|---|---|---|
| Crawl/store | bandwidth、object storage、requests | change-aware recrawl、compression、content hash |
| Parse/OCR | CPU/GPU、long-tail files | MIME routing、native text first、page confidence |
| Quality models | inference GPU | cheap prefilter、batching、small distilled classifier、uncertainty routing |
| Dedup | shuffle、RAM、index | blocking、signature compression、incremental clusters |
| Tokenization | CPU、I/O | batched vectorized tokenizer、pretokenized immutable shards |
| Training loader | object-store egress/GPU idle | locality/cache/prefetch、shard sizing |
| Reprocessing | repeated full DAG | immutable layers、content-addressed cache、stage-level versioning |

### 16.3 不能为了 cost 牺牲的东西

- rights/consent enforcement；
- provenance；
- deletion ability；
- held-out eval independence；
- PII/secrets safety gates；
- raw sample audits。

Cost optimization 应画 quality/safety/throughput Pareto，而不是只报 TB/hour。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/07_pretraining_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。

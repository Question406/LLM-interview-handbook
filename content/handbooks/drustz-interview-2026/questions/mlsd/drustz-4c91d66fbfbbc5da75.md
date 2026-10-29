---
id: drustz-4c91d66fbfbbc5da75
section: mlsd
order: 43
level: A
title: 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 一、90 秒开场（建议背下来）⭐⭐⭐
quick: >-
  作者文档章节 · 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 一、90
  秒开场（建议背下来）⭐⭐⭐
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
## 一、90 秒开场（建议背下来）⭐⭐⭐

> 我会先从目标能力、语言/领域、context length、参数与 compute budget、许可和安全边界反推 token budget 与 source mixture。数据链分为 immutable raw acquisition、结构化 extraction、language/safety/quality filtering、exact/near/semantic dedup、benchmark decontamination、mixture sampling、tokenization/packing 和 versioned sharding。每条 document 都带 source URI、fetch time、license/consent、content hash、父子变换与 filter decisions，保证 lineage、takedown 和可重放。质量不能只靠规则或大模型打分：我会在固定模型、训练 tokens 和 compute 下用小型 proxy runs 做 source/filter/mixture ablation，再在目标能力、per-domain validation loss、memorization、安全与 bias slices 上验证。数据短缺时优先提高有效信息密度、补合法的 first-party/licensed/low-resource data、优化 mixture，再谨慎使用经过 verifier 的 synthetic data 和有限重复；不能把同一低质量网页多跑几 epoch 当作新信息。生产上用 content-addressed manifests、幂等 stage、可恢复 sharding、funnel/分布监控和数据版本锁定，确保一次昂贵训练可以被解释和复现。

15 分钟题的骨架：

```text
Requirements / rights
  → raw immutable acquisition
  → extraction + normalization
  → safety/quality/language filters
  → exact + near dedup + decontamination
  → source mixture + curriculum
  → tokenizer + packing + shards
  → proxy ablations + full-run gates
  → lineage, deletion, monitoring
```



---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/07_pretraining_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。

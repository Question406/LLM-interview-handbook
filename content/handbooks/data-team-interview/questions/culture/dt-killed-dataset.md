---
id: dt-killed-dataset
section: culture
order: 2
level: A
title: Culture：你停过哪一批数据，理由是什么？
quick: "选一个你主动停用数据源的真实例子，讲清证据：数据混入了评测题、合成样本未经验证、某个来源拖累了模型，或许可与隐私要求不合格。再说明如何隔离这批数据、能否恢复，以及停用后指标有没有改善。"
companies:
  - apple
tags:
  - Apple
  - Culture
  - Data Quality
  - Governance
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The Curse of Recursion / Model Collapse
    url: https://arxiv.org/abs/2305.17493
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
---

可以讲一次大家还想继续加数据、你却决定停用某个来源的经历。原因要具体：它混入了评测内容，合成样本没有经过验证，加入后某类能力持续下降，或许可、隐私要求不合格。即使总数据量看着不错，也该根据这些证据决定是否继续使用。

停用时要保留恢复和审计的条件。把来源标为 `deprecated`，保留样本指纹，将数据放到可审计的隔离区（quarantine），不要直接删到无法追查。

这道 Culture 题适合展示你如何判断数据风险。只说「我停过数据」还不够；从来没停过，或者只是因为磁盘满了而停，也很难说明你的判断力。`dt-see-around-corners` 问的是如何提前补上缺口，这题问的是发现风险后如何停止使用数据。两题都需要你说明问题如何一步步出现。

可以从下面几类经历中挑选：

- 数据与评测检查集的 n-gram 重叠很高，可能造成污染，见 `dt-contamination`。
- 连续多代生成合成数据却没有验证，重复出现的错误越来越多，见 `dt-when-not-synth`。
- 固定的锚点评测连续两轮下降。每次去掉一个数据来源重训或评测（leave-one-source-out）后，明确定位到这个来源，见 `dt-neg-transfer`。
- 来源不符合 robots、许可或个人信息（PII）要求，见 `dt-legal-capability`。

用户要求退出训练的 URL（opt-out URL）必须能撤回。Bloom 过滤器不能单独承担这项工作，见 `dt-exact-dedup-code`。

用 90 秒讲清你看到了什么证据、停用了什么、之后哪项固定评测恢复了。指标还没恢复，就说明还在排查。停用是否有效，要看结果。

## 追问

- 业务方仍然要更多数据怎么办？给出替代方案，例如经过验证的合成数据、许可明确的数据集，或端侧 adapter。说明这些方案能满足哪些需求；只拒绝、不提供路径，问题仍然没解决。
- 如果停错了怎么办？承认判断有误，再恢复数据源。只要保留了版本并能重放，就能检查影响、重新验证。

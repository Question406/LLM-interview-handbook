---
id: dt-killed-dataset
section: culture
order: 2
level: A
title: Culture：你停过哪一批数据，理由是什么？
quick: "讲一次大家还想继续加数据、你却主动停掉某个来源的经历。先说证据：它混入了评测题、合成样本没经过验证、加入后某类能力持续下降，或许可、隐私要求不合格。再说怎样隔离这批数据、保留恢复条件，最后报停用后哪项固定评测恢复了。"
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

这题要讲一次大家还想继续加数据、你却决定停用某个来源的经历。面试官想看你怎样判断数据风险：凭什么证据停，停的时候怎样留后路，停完之后指标有没有回来。要讲的是你凭证据做出的判断；因为磁盘满了才停的经历，说明不了判断力。

## 按什么顺序讲

用 90 秒，按「当时的情况 → 看到的证据 → 停了什么、怎么停 → 结果」来讲。

先讲情况和证据。总数据量看着不错，大家还想继续加，但你看到了具体信号。可以从下面几类经历里挑：

- 数据与评测检查集的 n-gram 重叠很高，可能造成污染，见 `dt-contamination`。
- 连续多代生成合成数据却没有验证，重复出现的错误越来越多，见 `dt-when-not-synth`。
- 固定的锚点评测连续两轮下降。每次去掉一个数据来源重训或评测（leave-one-source-out），最后明确定位到这个来源，见 `dt-neg-transfer`。
- 来源不符合 robots、许可或个人信息（PII）要求，见 `dt-legal-capability`。

再讲你怎么停。停用时要留得住追查的线索：把来源标为 `deprecated`，保留样本指纹，把数据放进可审计的隔离区（quarantine），不要删到无法追查。这样以后要恢复或复盘，都还有依据。如果涉及用户要求退出训练的 URL（opt-out URL），撤回必须真能执行，Bloom 过滤器不能单独承担这项工作，见 `dt-exact-dedup-code`。

最后讲结果：停用之后，哪项固定评测恢复了。停用有没有效要看结果；指标还没恢复，就照实说还在排查。

## 和 See Around Corners 的区别

`dt-see-around-corners` 问的是问题还没爆时怎样提前补上缺口，这题问的是发现风险后怎样停止使用数据。两题都需要讲清问题是怎样一步步出现的。

## 追问

- 业务方仍然要更多数据怎么办？给出替代方案，例如经过验证的合成数据、许可明确的数据集或端侧 adapter，并说明它们各自能满足哪些需求。只拒绝、不给路径，问题仍然没有解决。
- 如果停错了怎么办？承认判断有误，再恢复这个来源。只要保留了版本、能够重放，就能检查影响、重新验证。

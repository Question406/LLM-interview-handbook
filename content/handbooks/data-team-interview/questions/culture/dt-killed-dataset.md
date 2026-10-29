---
id: dt-killed-dataset
section: culture
order: 2
level: A
title: Culture：你停过哪一批数据，理由是什么？
quick: >-
  讲一次大家还想加数据、我却停掉某个来源的经历。先说证据，比如混进了评测题、合成样本没验证、加进去后某类能力持续下降，或者许可、隐私不合格；再说怎么隔离、留好恢复条件；最后报停掉后哪项固定评测恢复了。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: The Curse of Recursion / Model Collapse
    url: 'https://arxiv.org/abs/2305.17493'
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: 'https://arxiv.org/abs/2107.06499'
    type: primary
  - title: Applebot model training and individual privacy rights
    url: 'https://support.apple.com/en-us/120320'
    type: primary
---

我会讲一次大家还想往里加数据、我却把某个来源停掉的经历，讲清楚凭什么停、停的时候怎么留后路、停完指标有没有回来。因为磁盘满了才停的那种，说明不了判断力。

开头先交代情况：总数据量看着不错，大家想继续加，但我看到了具体的信号。〔填：你当时看到的信号。〕比如固定的 regression evaluation 连着两轮下降，我每次去掉一个数据来源重训或评测，也就是 leave-one-source-out，最后定位到就是这一个，见 `dt-neg-transfer`。整个故事九十秒左右，按情况、证据、停了什么和怎么停、结果这个顺序说下来。

停的时候要留得住追查的线索。我会把来源标成 `deprecated`，保留样本指纹，数据放进可审计的隔离区（quarantine），不删到查不回来，以后要恢复或复盘都有依据。如果涉及用户要求退出训练的 opt-out URL，撤回得真能执行，光靠 Bloom 过滤器担不起这件事，见 `dt-exact-dedup-code`。

最后报结果：停掉之后哪项固定评测恢复了。〔填：恢复了哪一项、恢复了多少。〕还没恢复就照实说还在排查，停得对不对要看结果。

这题和 `dt-see-around-corners` 容易混。那题问问题还没爆时怎么提前补缺口，这题问发现风险之后怎么停用数据，两题都要把问题怎么一步步出现的讲清楚。

## 追问

**除了 regression tasks 下降，还有什么信号够得上停一个来源？**
常见的还有三种。和评测检查集的 n-gram 重叠很高，可能是 contamination，见 `dt-contamination`；synthetic data 连续生成了几代却没验证，重复出现的错误越来越多，见 `dt-when-not-synth`；来源不符合 robots、许可或 PII 要求，见 `dt-legal-capability`。挑一种你真经历过的讲。

**业务方还是要更多数据怎么办？**
给替代方案，比如验证过的 synthetic data、许可明确的数据集或 on-device adapter，并说清各自能满足哪些需求。光拒绝不给路径，问题还在那里。

**停错了怎么办？**
承认判断有误，把这个来源恢复回来。版本留着、能重放，就能查影响、重新验证。

**为什么不直接删掉？**
删了就查不回来，以后想恢复或复盘都没有依据，所以放隔离区、留样本指纹。

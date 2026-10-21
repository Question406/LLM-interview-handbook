---
id: dt-llama-edit-pref
section: labs
order: 18
level: A
title: Llama 3：为什么偏好对要有 edited，还要丢掉「差不多」的对？
quick: "两个做法都是为了让偏好信号更干净。chosen 只是两条里较好的那条，未必达标，所以 Llama 3 让标注员再改一遍，得到 edited > chosen > rejected；差距很小的对标签噪声大，奖励模型只用清晰的偏好对，DPO 只留「明显更好」和「更好」两档。AFM 用 cohesion 优先选人评一致的 prompt，也是在减少弱信号。"
companies:
  - apple
tags:
  - Meta
  - Llama
  - Preference
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

edited 解决 chosen 本身不够好的问题，丢掉「差不多」的对解决标签噪声的问题。两件事目标相同：让模型学到的偏好信号更干净。

## 为什么要 edited

Llama 3 §4 的流程是：每个 prompt 从两个不同配方的模型各抽一条回答，标注员按四档打分（明显更好、更好、稍好、边际更好），标完还可以修改 chosen。之所以要改，是因为 chosen 只是两个回答里较好的那个，本身可能仍不符合要求。改完得到 edited > chosen > rejected 三级顺序。

修改后的回答可以作为监督微调（SFT）正例。这时要把原有的偏好顺序一起记下来，让不同训练阶段能追踪到同一组数据。

## 为什么丢「差不多」的对

两个回答太相似时，标注员的判断接近随机，偏好标签很容易受噪声影响。Llama 2 起就丢掉太像的对。Llama 3 进一步分开用：奖励模型（RM）用当时能拿到的清晰偏好对；直接偏好优化（DPO）只用各能力最新一批数据，并且只保留「明显更好」和「更好」两档。「稍好」和「边际更好」留作分析，不进 DPO。他们还去掉了 Llama 2 损失函数里的 margin 项，因为数据规模扩大后这一项的收益变小。AFM 用 cohesion 挑选标注员更容易达成一致的 prompt，也是在减少弱信号带来的噪声。

所以回答这题时，重点是解释四档标签怎样表示偏好差距，以及为什么较弱的两档不进 DPO。

如果数据不够，想把「稍好」加回来，先看人评 kappa。一致性很低时，补进来的主要是噪声，见 `dt-annotator-protocol`。

## 追问

- **edited 会不会变成标注员的文风？** 会。协议里要写明只改事实和结构、保留原回答的语气，并抽查套话密度。
- **两条候选来自同一个模型行不行？** 不太行。Llama 故意用不同配方的模型来拉开能力差；同一模型、同一设置下的两条回答容易落到「差不多」而被丢掉。所以两条候选最好来自不同配方或不同温度。
- **视觉偏好怎么做？** Llama 后面对图像也用 edited > chosen > rejected，再把图里的数字做合成扰动，作为额外的 rejected。这和 `dt-grounding-data` 讨论的问题是同一类。

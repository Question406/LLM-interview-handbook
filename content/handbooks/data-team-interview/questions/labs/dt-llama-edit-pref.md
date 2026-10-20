---
id: dt-llama-edit-pref
section: labs
order: 18
level: A
title: Llama 3：为什么偏好对要有 edited，还要丢掉「差不多」的对？
quick: "Llama 3 让标注员改进选中的回答，得到 edited > chosen > rejected。奖励模型使用清晰的偏好顺序，DPO 则只用「明显更好」和「更好」的对；差距很小的对容易放大标注噪声。这与 AFM 优先选择人评一致的问题是类似思路。"
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

两个回答太相似时，丢掉这一对。奖励模型（RM）使用当时能取得的清晰偏好对；直接偏好优化（DPO）只用各能力最新一批数据，并只保留「明显更好」和「更好」这两档。「稍好」和「边际更好」留作分析，不用于 DPO。

标注员还可以修改 chosen，形成 edited > chosen > rejected。修改后的回答可以作为监督微调（SFT）正例，原有偏好顺序也要记录下来，让不同训练阶段能追踪同一组数据。如果数据不足，想把「稍好」也加回来，先看人评 kappa；一致性很低时，补进来的主要是噪声，见 `dt-annotator-protocol`。

不能把所有偏好对都放进 DPO，也不能把人工改写当成一条无关的新样本。chosen 只是两个回答中较好的那个，可能仍不符合产品要求；两个回答差距太小时，偏好标签也更容易受噪声影响。他们还去掉了 Llama 2 损失函数中的 margin 项，因为数据规模扩大后，这一项的收益变小。回答时更应解释四档标签如何表示偏好差距，以及为什么丢弃较弱的两档。

AFM 用 cohesion 选择标注员更容易达成一致的 prompt，与丢弃差距很小的偏好对一样，都是在减少弱信号造成的噪声。人工修改要遵循研究数据的标注协议：改事实和结构，不改成自己的口头禅，抽查套话密度。两条候选来自不同配方或不同温度，同一模型两条容易落到「差不多」。视觉偏好他们后面对图也用 edited > chosen > rejected，再合成扰动图里的数字当额外 rejected，这一做法也与 `dt-grounding-data` 讨论的问题有关。用户原文不进这批对。

公开锚点：Llama 3 §4 每个 prompt 从两个不同配方的模型各抽一条，人标四档（明显更好、更好、稍好、边际更好），标完还可以改 chosen；Llama 2 起就丢掉太像的对。

## 追问

- **edited 会不会变成标注员文风？** 会。协议要写「改事实和结构，不改成自己的口头禅」，抽查套话密度。
- **两条来自同一个模型行不行？** Llama 故意用不同 mix 的模型，拉开能力差。同一模型两条容易落到「差不多」被丢掉。
- **视觉偏好？** 他们后面对图也用 edited > chosen > rejected，再合成扰动图里的数字当额外 rejected。和 `dt-grounding-data` 同构。

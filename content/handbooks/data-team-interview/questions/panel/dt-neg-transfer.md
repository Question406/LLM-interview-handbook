---
id: dt-neg-transfer
section: panel
order: 12
level: A
title: Panel：补一个能力，把另一个打掉了，如何用数据保住已有能力？
quick: >-
  训练前先列出必须保住的旧能力（英语通用、安全、格式、已经做好的核心任务），固定评测和允许波动；data mix 里给这些域设最低 token
  份额，新数据比例逐步提高。旧能力超出波动就先降新来源的比例。目标任务涨了就发版，旧能力可能已经悄悄掉了。
companies:
  - apple
tags:
  - Apple
  - Negative Transfer
  - Data Mix
  - Continual
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Data Mixing Laws
    url: 'https://arxiv.org/abs/2403.16952'
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
---

训练前先列出必须保住的旧任务，规定好允许的评测波动；这些能力没有明显下降，新能力的 $\Delta$ 才算有效改善。旧能力退步了，先降新数据的比例，再考虑要不要调模型。

举个例子，补 multilingual 数据之后 multilingual 评测涨了，团队就发版，结果英语 instruction following 悄悄掉了。multilingual、数学、视觉、工具，每补一项都会挤占别的数据的份额。所以这是带约束的优化：英语指令、已经做好的摘要等核心任务、拒答、格式，这些不许掉的 evaluation slices 每一项都有冻结集和允许的波动。Data Mixing Laws 的式子里，$t_{ij}>0$ 的项就是域 $j$ 对域 $i$ 的伤害，我会先做小 sweep 看清谁伤害谁，再放到 large model 上。

数据上保住已有能力有几种手段。regression tasks 域设一个最低的 token 份额，新来源再重要也不能把它吃光。新数据的比例逐步提高，AFM 的 multilingual 从 8% 提到 30% 走的是课程，收益接近全程 30%，英语更稳。mid 和 post 阶段混入一部分 core 的高质量有机数据做重放，AFM 的 continued 阶段也写明保留了一部分 bulk 和高质量有机数据。

阶段上，影响面大的改动放在 mid 阶段小步观察；格式类改动放在 post 阶段，尽量少动 base model 的表示。如果具体任务另用 adapter 或 LoRA fine-tuning，base model mix 伤到的能力 adapter 未必救得回来，base model 的 regression tasks 还是要守，分工见 `dt-adapter-vs-base`。

## 追问

**安全指标掉了 0.5% 算破锚吗？**
安全按事故算，不按平均值算。红队 evaluation slices 破了就回滚，哪怕 MMLU 在涨。

**视觉适配为什么要留 60% 的文本？**
AFM 公开的 mix 就是这样，目的是少伤文本能力。这部分文本是在预防 negative transfer。

**遗忘是数据问题还是优化问题？**
先看 regression tasks token 有没有被挤出去。挤出去了先改 mix；mix 对了还在掉，再谈 learning rate 和 replay。

**旧能力已经掉了，重训一遍旧数据能补回来吗？**
可以补救。前面说的配额地板和课程也是手段。

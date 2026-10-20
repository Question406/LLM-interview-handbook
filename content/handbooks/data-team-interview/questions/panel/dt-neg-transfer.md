---
id: dt-neg-transfer
section: panel
order: 12
level: A
title: Panel：补一个能力，把另一个打掉了，数据上怎么托底？
quick: "新数据配比中保留英语通用、安全、格式和已上线功能的数据，并设置最低 token 份额。训练前固定旧能力评测和允许波动，超过阈值就降低新来源比例。逐步提高新数据比例通常比一次加满更稳，不能只看到目标任务提高就发版。"
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
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Data Mixing Laws
    url: https://arxiv.org/abs/2403.16952
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
---

训练前先列出必须保住的旧任务，并规定允许的评测波动。只有这些能力没有明显下降，新能力的 $\Delta$ 才能算有效改善。旧能力退步时，先降低新数据比例，再考虑是否需要调整模型。

不这么选的理由：多语、数学、视觉、工具都会挤占。目标涨了就发版，锚点可能已经破了。再训一遍旧数据可以补，不是唯一手段。

## 给旧能力保留数据预算

不许掉的切片：英语指令、已上线摘要 / 通知、拒答、格式。每张卡有冻结集和允许的波动。这是约束优化，不是单目标。

数据上的托底：

- 配额地板。锚点域有最小 文本处理单位（token） 份额，新源再重要也不能吃光。
- 课程。AFM 多语 8%→30% 用课程，收益接近全程 30%，英语更稳。
- 重放。mid / post 混入一部分 core 高质有机数据。AFM continued 也写了留一部分 bulk / 高质有机。
- 分阶段。伤面大的放 mid 小步看；格式类放 post，底座表示少动。

Mixing law 里 $t_{ij}>0$ 的项就是伤害。小 sweep 先看谁伤害谁，再放到大模型。

产品侧 AFM 还靠 feature adapter：底座后训练抬通用，功能靠 adapter。底座 mix 伤了通知摘要，adapter 未必救得回来，所以底座锚点仍要守。adapter 和底座怎么分见 `dt-adapter-vs-base`。

## 追问

- **安全掉了 0.5% 算破锚吗？** 安全按事故，不按平均。红队切片破了就回滚，哪怕 MMLU 涨。
- **视觉适配为什么要 60% 文本？** AFM 公开 mix 就是为了少伤文本。这是负迁移预防，不是浪费。
- **遗忘是数据问题还是优化问题？** 先看锚点 token 有没有被挤出。挤出了先改 mix。mix 对了还掉，再谈学习率和 replay。

---
id: dt-synth-collapse
section: labs
order: 49
level: S
title: DeepSeek 会问的 data chemistry：合成一直回流，模型会怎么塌？
quick: "每代合成都保留真人或许可原始数据，用独立 oracle 验证，并追踪少见题和表达多样性。未经验证地把上一代输出全作为下一代预训练数据，可能逐渐丢失分布尾部。验证答案正确，也不能单独保证风格和覆盖不退化。"
companies:
  - apple
tags:
  - DeepSeek
  - Synthetic Data
  - Model Collapse
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "The Curse of Recursion: Training on Generated Data Makes Models Forget"
    url: https://arxiv.org/abs/2305.17493
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

合成数据可以补任务覆盖，但也要保留真人或许可原始数据中的少见情况。Shumailov 的研究发现，反复用模型输出训练下一代，会逐渐丢失分布尾部并退化；保留原始数据可以缓解。R1 蒸馏集的公开做法对齐这句：只留答对的、混语言丢掉、小模型只 监督微调（SFT），见 `dt-r1-distill`。AFM 口径是能验证的合成才进。

不这么选的理由：英语第三方指南把 DeepSeek 研究面写成会问 data chemistry：滤合成、避 collapse。现场背「我们用了合成」不够。要说明每一代保留多少真人来源、用什么独立 oracle 验证，以及是否禁止当前学生给自己的输出打标签。

接到苹果：数学和代码使用执行或标准答案验证，工具任务检查状态断言。开放生成不能未经独立检查就反复回流。固定教师版本，并记录已经循环生成了多少代。无验证的网页改写当预训练，等于把教师幻觉写进基座，见 `dt-when-not-synth`、`dt-self-improve`。端侧蒸馏只蒸过门的轨迹，见 `dt-ondevice-distill-data`。

公开锚点：arxiv 2305.17493（后以 Nature 发表）；DeepSeek-R1。DeepSeek 没有官方面试流程页，题型来自第三方研究面指南，`realInterview: false`。

## 追问

- **留多少真人数据？** 论文里 10% 原始点能缓。我不会把 10% 当 AFM 配方。现场说：人源比例写进 mix，低于阈值就停合成扩容，先去挖许可集。
- **通过验证器（verifier）的合成还会退化吗？** 仍可能丢失风格和覆盖多样性，少见题也越来越像教师的表达。所以要难度带和多样性门，见 `dt-s1k`、`dt-math-passk-band`。
- **网页已经充满模型输出怎么办？** Applebot / 许可集也要来源分类。像模型的页降权或隔离，不要当「自然网页」。

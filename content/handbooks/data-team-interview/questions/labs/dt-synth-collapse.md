---
id: dt-synth-collapse
section: labs
order: 49
level: S
title: DeepSeek 会问的 data chemistry：合成一直回流，模型会怎么塌？
quick: "会先丢掉分布尾部：反复用上一代输出训练下一代，少见情况越来越少，表达越来越像教师。应对是每代都保留真人或许可原始数据，只让独立 oracle 验证过的合成进训练，并追踪少见题和表达多样性。答案验证正确，也不能单独保证风格和覆盖不退化。"
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

模型会先从分布尾部开始塌：少见情况在每一代合成里被稀释，最后整体退化。所以合成可以用来补覆盖，但每一代都要保留真人或许可原始数据，只让经过独立 oracle 验证的合成回流，并持续追踪少见题和表达多样性。

## 为什么会塌

Shumailov 等人的研究（arxiv 2305.17493，后发表在 Nature）发现，反复用模型输出训练下一代，模型会逐渐丢失分布尾部并退化；保留一部分原始数据可以缓解。原因很直接：模型生成时偏向高概率区域，少见样本每代都被采得更少，下一代学到的分布就更窄。

验证只能挡住错误答案，挡不住这种收窄。通过 verifier 的合成仍可能丢失风格和覆盖多样性，少见题也越来越像教师的表达。

## 怎么控制

1. 定人源比例：每一代保留多少真人来源写进数据 mix，低于阈值就停止扩容合成，先去找许可数据。
2. 独立验证：数学和代码用执行或标准答案验证，工具任务检查状态断言。开放生成不能未经独立检查就反复回流；也不能让当前学生给自己的输出打标签。
3. 记录代际：固定教师版本，并记录已经循环生成了多少代。
4. 守多样性：设难度带和多样性门槛，防止少见题被挤掉，见 `dt-s1k`、`dt-math-passk-band`。

DeepSeek-R1 蒸馏集的公开做法和这一套一致：只留答对的，混语言的丢掉，小模型只做监督微调（SFT），见 `dt-r1-distill`。AFM 2025 报告也只让能验证的合成进训练。没有验证的网页改写拿来做预训练，等于把教师的幻觉写进基座，见 `dt-when-not-synth`、`dt-self-improve`。蒸馏同理，只蒸通过门禁的轨迹，见 `dt-ondevice-distill-data`。

这题的来源：英语第三方指南说 DeepSeek 研究面会问 data chemistry，也就是怎么过滤合成、怎么避免 collapse。DeepSeek 没有官方面试流程页，所以 `realInterview: false`。现场要讲清上面这几个控制点，光说「我们用了合成」，面试官听不出你怎么防塌。

## 追问

- **留多少真人数据？** 论文里保留 10% 原始数据就能缓解。这个数来自论文设定，我会把人源比例写进 mix 并设停止阈值，按自己的评测来调。
- **网页上已经充满模型输出怎么办？** 爬下来的网页和许可集也要做来源分类。像模型写的页面降权或隔离，别当成「自然网页」。

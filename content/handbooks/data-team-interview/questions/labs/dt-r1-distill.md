---
id: dt-r1-distill
section: labs
order: 36
level: A
title: DeepSeek-R1：800k 蒸馏集是怎么滤的，小模型为什么只做 SFT？
quick: "R1 在 RL 收敛后做拒绝采样，只留正确且可读的轨迹，再加通用任务一起做 SFT：约 600k 推理加约 200k 写作 / QA，共约 800k，不含 RL 前那几千条冷启动。小模型只做 SFT，是为了单独看这些轨迹能不能传递能力。网上爬来的长思考没经过这套验证和过滤，和这份数据是两回事。"
companies:
  - apple
tags:
  - DeepSeek
  - Distillation
  - Reasoning
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

800k 是 RL 收敛之后第二轮 SFT 的数据：约 600k 推理轨迹，加约 200k 写作和 QA。推理轨迹靠拒绝采样得到，只保留正确且可读的。小模型蒸馏只做 SFT、不额外做 RL，是为了单独观察这些轨迹本身能不能把能力传过去。

## 800k 怎么来

RL 收敛后，用当前 checkpoint 采样并验证，只保留正确的轨迹，约 600k。可执行的题以规则为准；一部分题用 DeepSeek-V3 当生成式 judge，只补规则覆盖不了的部分，并接受抽查。

接着过滤可读性：去掉混用语言的、长段难读的，以及思考过程中无序堆放代码块的。他们写过输出有时混乱难读，这是过滤的原因。代码题需要的代码要保留，所以要按题型分组检查。

再加约 200k 写作和 QA（像「hello」这类不写思考过程）。之所以要加，是因为只蒸推理会把写作和短答能力冲掉，见 `dt-neg-transfer`。合起来约 800k，对 V3-Base 训两个 epoch；同一份数据再拿去微调 Qwen2.5 和 Llama 3.1 / 3.3 时只做 SFT。

## 蒸馏时要注意的

学生跟不上的超长思考不要硬蒸，见 `dt-teacher-bias`。最终答案正确但过程编造的轨迹，交叉熵损失（CE）仍会让学生学到错误的过程，见 `dt-prm-steps`。思考标签和最终回答的正文要分开处理。

通用的原则是：能验证的先验证，合成的思考进 SFT 前要过门槛；judge 如果和被评的模型同族会有偏差。蒸馏也有别的做法，AFM 2025 报告蒸的是教师 logits 和预训练末段的 token，R1 蒸的是离散的轨迹，见 `dt-ondevice-distill-data`。

## 追问

- **冷启动那几千条算不算 800k？** 不算。冷启动是 RL 之前准备的几千条可读长推理链（CoT），量级是 thousands；800k 是 RL 之后的第二轮 SFT。网上随便爬来的 R1 长思考没经过验证和过滤，也和这份数据无关。

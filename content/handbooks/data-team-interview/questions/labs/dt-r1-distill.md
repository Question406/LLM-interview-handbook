---
id: dt-r1-distill
section: labs
order: 36
level: A
title: DeepSeek-R1：800k 蒸馏集是怎么滤的，小模型为什么只做 SFT？
quick: "R1 在 RL 后拒绝采样，保留正确且可读的轨迹，再加入通用任务做 SFT。约 800k 包括约 600k 推理和 200k 写作 / QA，不含 RL 前的几千条冷启动。小模型仅做 SFT 来验证轨迹效果；不能把网上长思考直接当这份数据。"
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

RL 收敛后，用当前 checkpoint 采样并验证，只保留正确轨迹。再过滤混用语言、难读的长段和思考中无序堆放的代码块；代码题需要的代码仍保留，按题型分别检查。可执行题以规则为准，生成式 judge 只补充规则无法覆盖的部分，并接受抽查。小模型蒸馏只做 SFT、不额外做 RL，才能单独观察这些轨迹能否传递能力。学生跟不上的超长思考不要硬蒸，见 `dt-teacher-bias`。若最终答案正确但过程编造，交叉熵损失（CE）仍会让学生学习错误过程，见 `dt-prm-steps`。思考标签不当产品正文。

不这么选的理由：把 R1 网上随便爬的长思考当 800k，或把冷启动那几千条算进 800k。冷启动是 RL 前准备的几千条可读长推理链（CoT）。800k 是 RL 之后的第二轮 SFT。只蒸推理会把写作和短答冲掉，见 `dt-neg-transfer`。

接到苹果：没有公开 R1 配方。能对上的是能验证的先验证，合成思考进 SFT 前要过门。和 `dt-ondevice-distill-data` 的差别：AFM 端侧蒸的是教师 logits 和预训练末段 token；R1 蒸的是离散轨迹。Judge 若是同族会偏。轨迹来自许可题和验证合成，不从用户会话抽思考。

公开锚点：大约 600k 推理轨迹只留对的，再加大约 200k 写作 / QA（「hello」这类不写思考），一共约 800k，对 V3-Base 训两个 epoch；同一份再微调 Qwen2.5 和 Llama 3.1 / 3.3 时只做 SFT。一部分拿 DeepSeek-V3 当生成式 judge。

## 追问

- **冷启动那几千条算不算 800k？** 不算。冷启动是 RL 前的可读长 CoT，量级是 thousands。800k 是 RL 之后的第二轮 SFT。
- **为什么滤代码块？** 他们写输出有时混乱难读。代码题该留代码；滤的是思考里乱堆的块。题型分组统计，别一把刀切。
- **只蒸 600k 推理？** 他们加了 200k 通用，就是怕推理 SFT 把写作和短答冲掉，见 `dt-neg-transfer`。

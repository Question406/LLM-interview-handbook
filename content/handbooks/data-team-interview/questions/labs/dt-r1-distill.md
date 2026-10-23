---
id: dt-r1-distill
section: labs
order: 36
level: A
title: DeepSeek-R1：800k 蒸馏集是怎么滤的，小模型为什么只做 SFT？
quick: "R1 在 RL 收敛后做拒绝采样，只留正确且可读的轨迹，再加通用任务一起做 SFT：约 600k 推理加约 200k 写作 / QA，共约 800k，不含 RL 前那几千条冷启动。小模型只做 SFT，是为了单独看这些轨迹能不能把能力传过去。网上爬来的长思考没经过这套验证和过滤，和这份数据是两回事。"
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

800k 是 RL 收敛之后第二轮 SFT 的数据，约 600k 推理轨迹加约 200k 写作和 QA。推理轨迹靠拒绝采样得到，只留正确且可读的。小模型蒸馏只做 SFT、不额外做 RL，是为了单独看这些轨迹本身能不能把能力传过去。

600k 是这么来的：RL 收敛后，用当前 checkpoint 采样再验证，只留正确的轨迹。可执行的题以规则为准；一部分题用 DeepSeek-V3 当生成式 judge，只补规则覆盖不了的部分，并接受抽查。

光对还不够，还要过可读性这一关。他们自己写过，输出有时混乱难读，所以混用语言的、长段难读的、思考过程里无序堆着代码块的都去掉。比如一条轨迹中英文来回切，中间插了几段没头没尾的代码，答案对了也不留。代码题本身需要的代码要保留，所以按题型分组检查。

然后再加约 200k 写作和 QA，像「hello」这类不写思考过程。只蒸推理会把写作和短答能力冲掉，见 `dt-neg-transfer`。合起来约 800k，对 V3-Base 训两个 epoch；同一份数据拿去微调 Qwen2.5 和 Llama 3.1 / 3.3 时，只做 SFT。

自己做蒸馏时，学生跟不上的超长思考别硬蒸，见 `dt-teacher-bias`。最终答案对、过程却是编造的轨迹，交叉熵损失（CE）照样会让学生学到错误的过程，见 `dt-prm-steps`。思考标签和最终回答的正文也要分开处理。原则就是能验证的先验证，合成的思考进 SFT 前要过门槛。

## 追问

**冷启动那几千条算不算在 800k 里？**
不算。冷启动是 RL 之前准备的几千条可读长推理链（CoT），量级是 thousands；800k 是 RL 之后的第二轮 SFT。

**网上爬来的 R1 长思考能当这份数据用吗？**
不能。那些轨迹没经过验证和可读性过滤，和这份数据无关。

**用 DeepSeek-V3 当 judge，同族不会有偏差吗？**
会有，judge 和被评的模型同族就会偏。所以 V3 只补规则覆盖不了的那部分，并且要接受抽查。

**蒸馏还有别的做法吗？**
有。AFM 2025 报告蒸的是教师 logits 和预训练末段的 token，R1 蒸的是离散的轨迹，见 `dt-ondevice-distill-data`。

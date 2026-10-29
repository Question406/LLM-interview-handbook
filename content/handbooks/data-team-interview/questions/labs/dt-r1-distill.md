---
id: dt-r1-distill
section: labs
order: 36
level: A
title: DeepSeek-R1：800k distillation 集是怎么滤的，small model 为什么只做 SFT？
quick: >-
  R1 在 RL 收敛后做 rejection sampling，只留正确且可读的 trajectories，再加通用任务一起做 SFT：约 600k
  推理加约 200k 写作 / QA，共约 800k，不含 RL 前那几千条冷启动。small model 只做 SFT，是为了单独看这些
  trajectories 能不能把能力传过去。网上爬来的长思考没经过这套验证和过滤，和这份数据是两回事。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

800k 是 RL 收敛之后第二轮 SFT 的数据，约 600k reasoning trajectories 加约 200k 写作和 QA。reasoning trajectories 靠 rejection sampling 得到，只留正确且可读的。small model distillation 只做 SFT、不额外做 RL，是为了单独看这些 trajectories 本身能不能把能力传过去。

600k 是这么来的：RL 收敛后，用当前 checkpoint sampling 再验证，只留正确的 trajectories。可执行的题以规则为准；一部分题用 DeepSeek-V3 当生成式 judge，只补规则覆盖不了的部分，并接受抽查。

光对还不够，还要过可读性这一关。他们自己写过，输出有时混乱难读，所以混用语言的、长段难读的、思考过程里无序堆着代码块的都去掉。比如一条 trajectories 中英文来回切，中间插了几段没头没尾的代码，答案对了也不留。代码题本身需要的代码要保留，所以按题型分组检查。

然后再加约 200k 写作和 QA，像「hello」这类不写思考过程。只蒸推理会把写作和短答能力冲掉，见 `dt-neg-transfer`。合起来约 800k，对 V3-Base 训两个 epoch；同一份数据拿去 fine-tuning Qwen2.5 和 Llama 3.1 / 3.3 时，只做 SFT。

自己做 distillation 时，student 跟不上的超长思考别硬蒸，见 `dt-teacher-bias`。最终答案对、过程却是编造的 trajectories，cross-entropy 损失（CE）照样会让 student 学到错误的过程，见 `dt-prm-steps`。思考标签和最终回答的正文也要分开处理。原则就是能验证的先验证，合成的思考进 SFT 前要达到 threshold。

## 追问

**冷启动那几千条算不算在 800k 里？**
不算。冷启动是 RL 之前准备的几千条可读长 chain-of-thought (CoT)，量级是 thousands；800k 是 RL 之后的第二轮 SFT。

**网上爬来的 R1 长思考能当这份数据用吗？**
不能。那些 trajectories 没经过验证和可读性过滤，和这份数据无关。

**用 DeepSeek-V3 当 judge，同族不会有偏差吗？**
会有，judge 和被评的模型同族就会偏。所以 V3 只补规则覆盖不了的那部分，并且要接受抽查。

**distillation 还有别的做法吗？**
有。AFM 2025 报告蒸的是 teacher logits 和 pre-training 末段的 token，R1 蒸的是离散的 trajectories，见 `dt-ondevice-distill-data`。

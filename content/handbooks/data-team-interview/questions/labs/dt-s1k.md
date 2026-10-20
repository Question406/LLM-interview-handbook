---
id: dt-s1k
section: labs
order: 40
level: A
title: s1：1000 条推理 SFT 为什么够用，多堆 59k 为什么未必更好？
quick: "1000 条能否有效，取决于学生模型已经会多少，以及示范是否兼顾难度、多样性和质量。直接加入 59k 条不一定更好。Budget forcing 是推理时控制思考时长的方法，不是增加训练数据。学生学不会的超长推理应过滤，少量 SFT 也不能替代 RLVR。"
companies:
  - apple
tags:
  - Reasoning
  - Distillation
  - Sample Efficiency
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "s1: Simple test-time scaling"
    url: https://arxiv.org/abs/2501.19393
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先确认学生模型的起点，再决定需要多少条合格的推理示范。挑选时同时看难度、多样性和质量：题目要补当前模型的不足，不能全挤在一种竞赛题型里，推理要可读、答案要能验证。题目如果难到学生无法通过交叉熵训练学会，就只会增加噪声。Budget forcing 在推理时插入 Wait 延长思考，或强制结束思考；它属于解码控制，不是新增训练数据。数据卡上仍是题 + 思考 + 可核答案。思考过长、答案错，丢掉，见 `dt-prm-steps`。竞赛题和 AIME / MATH 训练集去重，见 `dt-llama-anneal`、`dt-contamination`。1k 不能代替 基于可验证奖励的强化学习（RLVR）：监督微调（SFT） 模仿过门轨迹，分布一偏还得在线采样加规则奖励，见 `dt-rlvr-data`。

不这么选的理由：把「1k 就够」听成不用验证，或把 59k 消融池整锅端进 SFT。`dt-r1-distill` 的 800k 是大模型自己的第二轮 SFT，还要补写作。s1K 是已经指令对齐的 32B 再点一点推理。起点不同，条数不可横比。教师错，1k 会把错法刻死，比 59k 更狠。

接到苹果：没有公开 s1 配方。能对上的是 AFM「能验证的先验证」，以及端侧不该蒸学生复现不了的超很长的推理过程，见 `dt-ondevice-distill-data`。过门轨迹来自许可竞赛和验证合成，不从用户会话抽思考。

公开锚点：Muennighoff 等人按难度、多样、质量三道门从更大池子收到 s1K，再 SFT Qwen2.5-32B-Instruct；AIME24 他们报过从 50% 到 57%。

## 追问

- **质量门谁来打？** 他们用更强模型的轨迹，再人工 / 自动核答案。教师错，1k 会把错法刻死，比 59k 更狠。
- **只要难的？** 消融是三道一起。全是超难、学生 CE 学不动，等于噪声。
- **1k 能代替 RLVR 吗？** 不能。SFT 模仿过门轨迹；分布一偏还得在线采样加规则奖励，见 `dt-rlvr-data`。

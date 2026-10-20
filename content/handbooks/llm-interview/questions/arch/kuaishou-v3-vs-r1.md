---
id: kuaishou-v3-vs-r1
section: arch
order: 160
level: A
title: 快手 26 校招：DeepSeek-V3 和 R1 在架构或训练上差在哪？
quick: "V3 是使用 MLA 和专家路由的 MoE 基座，经过大规模预训练和后训练。R1 在强基座上先用长推理过程做监督微调（SFT）冷启动，再用可验证奖励做强化学习（RL），训练推理行为。两者的差异主要在训练目标与数据。"
tags:
  - Kuaishou
  - DeepSeek
  - R1
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 快手26校招大模型算法一面
    url: https://www.nowcoder.com/feed/main/detail/b1da5731c34e4a3d99becef4f0a0c169
    type: candidate-first-hand
  - title: DeepSeek-V3
    url: https://arxiv.org/abs/2412.19437
    type: primary-paper
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary-paper
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型算法
- 届别 / 流程：26 校招；一面
- 面试时间：原帖未披露；帖子发布于 2025-12-30
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“请分别说说你对 DeepSeek-V3 和 DeepSeek-R1 的理解，它们在架构或训练策略上有何关键差异？”**

常见误区是：把 R1 说成「换了一套全新骨架」或把 V3 说成「没有后训练」。V3 侧重训练通用能力强、推理成本较低的基座；R1 则在强基座上训练可验证的长推理过程。骨架同属 MoE / MLA 家族，差异主要在训练目标与数据。

## V3：基座在省 KV、稳路由、把规模做上去

架构上，MLA 把 KV 压缩成低维潜在表示，并把 RoPE 所需的部分拆成较短的 $k^R$。DeepSeekMoE 使用细粒度专家和共享专家，路由后的输出为

$$
y=\sum_{i\in\mathrm{top}k} g_i(x)\,E_i(x),
$$

负载均衡主要用专家偏置 expert bias，避免依赖较大的辅助损失 aux（见 `arch-moe-noaux`）。FFN 专家内部仍是 SwiGLU。训练侧是大规模稳定预训练，再用监督微调（SFT）和强化学习（RL）做后训练；MTP 多头预测是训练信号，也可作 speculative draft。这些设计让模型在相同算力下容纳更多总参数，同时控制 decode 阶段的缓存成本。

## R1：后训练把推理行为训出来

公开路线侧重推理能力的后训练：先用包含长思维链（CoT，即分步推理过程）的数据做 SFT 冷启动，再对同一题采样多个回答，用规则可验证的奖励做 RL（GRPO 一族），训练自我验证和长推理。R1-Zero 甚至走「少 SFT、直接 RL」对照。数学和代码的结果可以检查，因此能给出明确的奖励；开放域任务不能直接照搬这种奖励。长思考是奖励与采样的产物，不是 MLA 公式变了。

我会把两套技巧分开：V3 报告里的训练稳定、无辅助均衡、MTP；R1 的冷启动、组相对优势、惩罚格式。不要用「R1 更聪明所以架构更复杂」带过。细节导航见 `company-deepseek`、`pt-r1zero`。

## 追问

- **R1 能离开 V3 级基座吗？** 公开路线建立在同类强 MoE 基座上；弱基座若只增加 RL 训练，长 CoT 很容易产生编造的步骤。
- **架构一点没变吗？** 推理时可能加思考格式、更长生成；层数 / 专家数不是 R1 的卖点。
- **和普通 SFT 聊天模型差在哪？** 训练目标更强调步骤可验证、结果正确，因此 KL 约束和长度控制也需要重新调整。

---
id: kuaishou-v3-vs-r1
section: arch
order: 160
level: A
title: 快手 26 校招：DeepSeek-V3 和 R1 在架构或训练上差在哪？
quick: >-
  V3 是用 MLA 和专家路由的 MoE 基座，经过大规模预训练，也做了后训练。R1 在这类强基座上先用长推理过程做 SFT 冷启动，再用可验证奖励做
  RL，把推理行为训出来。两者骨架同属一个家族，差异主要在训练目标和数据。
tags:
  - Kuaishou
  - DeepSeek
  - R1
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 快手26校招大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/b1da5731c34e4a3d99becef4f0a0c169'
    type: candidate-first-hand
  - title: DeepSeek-V3
    url: 'https://arxiv.org/abs/2412.19437'
    type: primary-paper
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary-paper
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型算法
- 届别 / 流程：26 校招；一面
- 面试时间：原帖未披露；帖子发布于 2025-12-30
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“请分别说说你对 DeepSeek-V3 和 DeepSeek-R1 的理解，它们在架构或训练策略上有何关键差异？”**

V3 和 R1 的骨架同属 MoE / MLA 家族，差异主要在训练目标和数据。V3 要的是通用能力强、推理成本较低的基座；R1 在强基座上专门训练可验证的长推理过程。所以别把 R1 说成换了一套全新骨架，也别说 V3 没做后训练。

## V3：省 KV、稳路由、把规模做上去

架构上，MLA 把 KV 压缩成低维的潜在表示，并把 RoPE 需要的部分拆成较短的 $k^R$。DeepSeekMoE 用细粒度专家加共享专家，路由后的输出是

$$
y=\sum_{i\in\mathrm{top}k} g_i(x)\,E_i(x),
$$

负载均衡主要靠专家偏置 expert bias，避免依赖较大的辅助损失 aux（见 `arch-moe-noaux`）。FFN 专家内部仍然是 SwiGLU。训练上是大规模的稳定预训练，再用 SFT 和 RL 做后训练；MTP 多头预测是一个训练信号，也可以拿来做 speculative draft。这些设计让模型在相同算力下装下更多的总参数，同时控制住 decode 阶段的缓存成本。

## R1：后训练把推理行为训出来

R1 的公开路线重点在推理能力的后训练。先用含长 chain of thought（CoT，即分步推理过程）的数据做 SFT 冷启动；再对同一道题 sampling 多个回答，用规则可验证的奖励做 RL（GRPO 一族），训练自我验证和长推理。R1-Zero 甚至走了「少 SFT、直接 RL」的对照路线。比如一道数学题，最后的答案对不对可以直接检查，奖励就很明确；开放域任务没有这样的检查，不能直接照搬这种奖励。长思考是奖励和 sampling 训出来的，和 MLA 的公式无关。

所以我会把两边的技巧分开讲：V3 报告里的训练稳定、无辅助损失的均衡、MTP；R1 的冷启动、组相对优势、格式惩罚。别用「R1 更聪明，所以架构更复杂」一句带过。细节导航见 `company-deepseek`、`pt-r1zero`。

## 追问

**R1 能离开 V3 这一级的基座吗？**
公开路线是建立在同类强 MoE 基座上的。弱基座只加 RL 训练，长 CoT 很容易出现编造的步骤。

**架构一点都没变吗？**
推理时可能加了思考格式、生成更长；层数、专家数不是 R1 的卖点。

**和普通 SFT 出来的聊天模型差在哪？**
训练目标更强调步骤可验证、结果正确，所以 KL 约束和长度控制也要重新调。

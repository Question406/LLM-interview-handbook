---
id: kuaishou-v3-vs-r1
section: arch
order: 160
level: A
title: 快手 26 校招：DeepSeek-V3 和 R1 在架构或训练上差在哪？
quick: >-
  V3 是 MoE 基座（MLA、专家路由、大规模预训练 + 后训练）；R1 是在强基座上用长链推理 SFT 冷启动和可验证 RL
  堆推理行为。不要把 R1 说成换了一套全新骨架。
tags:
  - Kuaishou
  - DeepSeek
  - R1
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
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

陷阱是把 R1 说成「换了一套全新骨架」或把 V3 说成「没有后训练」。V3 解决的是强通用基座 + 经济推理；R1 解决的是在强基座上堆可验证的长思考。骨架同属 MoE / MLA 家族，差异主要在训练目标与数据。

## V3：基座在省 KV、稳路由、把规模做上去

架构侧：MLA 把 KV 压进低维 latent，RoPE 拆短段 $k^R$；DeepSeekMoE 细粒度专家 + 共享专家，路由

$$
y=\sum_{i\in\mathrm{top}k} g_i(x)\,E_i(x),
$$

均衡多用 expert bias 而不是大 aux（见 `arch-moe-noaux`）。FFN 专家内部仍是 SwiGLU。训练侧是大规模稳定预训练，再加 SFT / RL 后训练；MTP 多头预测是训练信号，也可作 speculative draft。它回答的是「同样算力怎么把总参数做大、decode 还不被 cache 打死」。

## R1：后训练把推理行为训出来

公开叙事强调推理向后训练：冷启动长 CoT SFT，再用规则可验证奖励做组采样 RL（GRPO 一族），突出自我验证和长思考。R1-Zero 甚至走「少 SFT、直接 RL」对照。奖励在可检查的数学 / 代码上硬核，开放域则另当别论。长思考是奖励与采样的产物，不是 MLA 公式变了。

面试把两套技巧分开：V3 报告里的训练稳定、无辅助均衡、MTP；R1 的冷启动、组相对优势、惩罚格式。不要用「R1 更聪明所以架构更复杂」这种空句子。细节导航见 `company-deepseek`、`pt-r1zero`。

## 追问

- **R1 能离开 V3 级基座吗？** 公开路线建立在同类强 MoE 基座上；弱基座上只堆 RL，长 CoT 很容易胡编。
- **架构一点没变吗？** 推理时可能加思考格式、更长生成；层数 / 专家数不是 R1 的卖点。
- **和普通 SFT 聊天模型差在哪？** 目标从「像人回话」变成「可验证步骤 + 结果对」，KL / 长度控制要另调。

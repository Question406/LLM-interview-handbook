---
id: company-deepseek
section: companies
order: 17
level: A
title: DeepSeek：25/26 算法岗应重点准备什么？
quick: "DeepSeek 重点是 MLA、MoE、MTP，以及从 DeepSeekMath 到 R1 的基于可验证奖励的强化学习（RLVR）路线，包括 GRPO、规则奖励和长推理过程。手写题准备 MHA 与 DPO 推导，系统题准备 PagedAttention 和推测解码。数字和机制以论文及可复现实验为准，二手完整答案帖只当练习。"
tags:
  - DeepSeek
  - 真题导航
  - 2025-2026
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: DeepSeekMath (GRPO)
    url: https://arxiv.org/abs/2402.03300
    type: primary
  - title: DeepSeek-V3
    url: https://arxiv.org/abs/2412.19437
    type: primary
---

DeepSeek 相关面试会追到框架背后的机制，光背 MLA、MoE、R1 这些名词，过不了第二层追问。面试官会问 V3 原文里 KV 怎么压、无辅助均衡靠什么、R1 为什么先用规则奖励再谈奖励模型（RM）。

公开的「含完整答案」类帖子我当练习用，不标成真题；数字和机制都以 R1、V3、DeepSeekMath 原文为准。Post-Training、Architecture、Systems 三章我会按下面三条线串起来，不按论文发布时间背摘要。

## 准备主线

1. 架构要讲清 MLA 怎么把 KV 压到 latent（`arch-mla`），MoE 的无辅助均衡和 expert bias（`arch-moe-noaux`），EP / all-to-all（`sys-expert-parallel`），MTP 的多 token 预测（`arch-mtp`），以及和 Dense 在训练上的差异（`arch-moe`）。
2. 后训练要讲 GRPO 为什么能省掉 PPO 的价值评估模型（critic）（`pt-grpo`、`fund-pg-ppo-grpo-index`），规则奖励和 RM 怎么取舍、模型怎么钻奖励规则的空子，以及 R1 各阶段的目标。手写直接偏好优化（DPO）的推导见 `code-dpo` / `pt-dpo-derive`。
3. 系统和手撕看推理显存和 PagedAttention（`sys-pagedattention`）、连续 batch、投机解码（`sys-specdecode`）。手写完整 MHA（形状与 mask）见 `deepseek-mha-handwrite`。

## 本手册练习卡

下面每条点进去就能跳到对应题。

- `deepseek-mha-handwrite`：手写完整 Multi-Head Attention（含形状与 Mask）
- `arch-mla`：MLA 如何压 KV
- `arch-moe-noaux`：MoE 无辅助负载均衡 / expert bias
- `arch-mtp`：MTP
- `sys-expert-parallel`：Expert Parallel 与 all-to-all
- `pt-grpo`：GRPO 目标与组内优势
- `pt-deepseek-rl-lineage`：R1 到 V3.2 公开的强化学习（RL）改动、MoE Keep Routing；不要编 V4
- `pt-r3-routing-replay`：Keep Routing / R2 / R3 和 GSPO 各修哪一层
- `sys-pagedattention` / `sys-specdecode`：推理显存与投机解码
- `code-dpo`：DPO 手撕

## 追问

**MLA 和 GQA 差在哪？**
GQA 是减少 KV 头；MLA 把 KV 压到低维 latent，cache 按 latent 存。别把 MLA 说成「就是 GQA」。

**为什么可以弱化辅助均衡损失？**
因为可以用 expert bias 这类可学习偏置来调路由，见 `arch-moe-noaux`，答的时候对照 V3 原文。

**R1 为什么先用规则奖励？**
在可验证的任务上，RM 可能引入噪声，还要处理模型利用奖励漏洞的问题，规则奖励更容易复现。RM 用来补规则覆盖不了的偏好。具体以论文为准。

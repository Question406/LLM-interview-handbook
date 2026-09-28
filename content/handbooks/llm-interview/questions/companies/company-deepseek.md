---
id: company-deepseek
section: companies
order: 17
level: A
title: DeepSeek：25/26 算法岗应重点准备什么？
quick: >-
  我会深挖 MLA、MoE、MTP，以及 DeepSeekMath 到 R1 的 RLVR 主线：GRPO、规则奖励、长链推理。手撕准备
  MHA、DPO 推导，还有推理系统里的 PagedAttention 和投机解码。以论文和可复现实验为准，二手「笔试完整答案」帖慎用。
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

DeepSeek 向面试很少只问框架名。错法：背 MLA、MoE、R1 口号，却对不上 V3 原文里 KV 怎么压、无辅助均衡靠什么、R1 为何先规则奖励再谈 RM。公开「含完整答案」类帖当练习准备，不标真题。数字和机制以 R1、V3、DeepSeekMath 原文为准。

## 准备主线

1. **架构**：MLA 怎么把 KV 压到 latent（`arch-mla`）；MoE 无辅助均衡和 expert bias（`arch-moe-noaux`）；EP / all-to-all（`sys-expert-parallel`）；MTP 多 token 预测（`arch-mtp`）；和 Dense 的训练差异（`arch-moe`）。
2. **后训练**：为什么用 GRPO 而不是 PPO critic（`pt-grpo`、`fund-pg-ppo-grpo-index`）；规则奖励 vs RM、reward hacking；R1 阶段目标。手撕 DPO 推导见 `code-dpo` / `pt-dpo-derive`。
3. **系统与手撕**：推理显存和 PagedAttention（`sys-pagedattention`）、连续 batch、投机解码（`sys-specdecode`）。手写完整 MHA（形状与 mask）见 `deepseek-mha-handwrite`。

Post-Training、Architecture、Systems 三章我会按这三条串，不会按论文发布时间背摘要。

## 本手册练习卡

点击下面每条即可跳到对应题。

- `deepseek-mha-handwrite`：手写完整 Multi-Head Attention（含形状与 Mask）
- `arch-mla`：MLA 如何压 KV
- `arch-moe-noaux`：MoE 无辅助负载均衡 / expert bias
- `arch-mtp`：MTP
- `sys-expert-parallel`：Expert Parallel 与 all-to-all
- `pt-grpo`：GRPO 目标与组内优势
- `pt-deepseek-rl-lineage`：R1 到 V3.2 公开 RL 改动、MoE Keep Routing；不要编 V4
- `pt-r3-routing-replay`：Keep Routing / R2 / R3 和 GSPO 各修哪一层
- `sys-pagedattention` / `sys-specdecode`：推理显存与投机解码
- `code-dpo`：DPO 手撕

## 追问

- **MLA 和 GQA 差在哪？** GQA 少 KV 头；MLA 把 KV 压到低维 latent，cache 按 latent 存。不要说成「就是 GQA」。
- **为什么可以弱化辅助均衡损失？** 用 expert bias 等可学习偏置调路由，见 `arch-moe-noaux`，对照 V3。
- **R1 为什么先规则奖励？** 可验证域上 RM 噪声和 hacking 成本更高，规则可复现。RM 只补规则盖不住的偏好。以论文为准。

---
id: company-baidu
section: companies
order: 4
level: A
title: 百度 AIDU：大模型与 Agent 岗该怎么定向准备？
quick: "百度后训练方向会把监督微调（SFT）、RLHF、DPO 的训练行为、GRPO、SimPO 一路追下去，再加上推理能力、MoE、Latent Attention、推测解码和分布式训练。Agent 岗还要覆盖工具与 API、记忆、RAG 与 Agent 的结合、多 Agent 和评测。"
tags:
  - Baidu
  - AIDU
  - 真题导航
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 百度 2027 AIDU 招聘
    url: 'https://talent.baidu.com/jobs/list?projectType=3&recruitType=GRADUATE'
    type: legacy-reference
  - title: ↗ 腾讯/百度/MiniMax 公开面经汇总
    url: 'https://www.nowcoder.com/feed/main/detail/8cab51ef9458459595cf81fda43da279'
    type: legacy-reference
---

百度公开面经很少停在「DPO 是什么」，会一路追到训练行为上：chosen 概率是不是一定升，length issue 怎么来的，SimPO 相对直接偏好优化（DPO）改了哪一项，Base 模型怎么增强 reasoning。只背公式，这几层多半答不上来。

所以我准备时按追问链来串：推导 → $\beta$ → chosen/rejected likelihood → 长度偏置 → hard negatives → SimPO/KTO → 离线与在线强化学习（RL）。Agent 岗另外加上指令冲突和代码验证器（verifier），不拿「会调工具」收尾。

## 准备主线

1. DPO 动力学的重点是 chosen 概率不必单调上升。要能画出对齐曲线，并解释 reference 和 $\beta$ 的作用，见 `baidu-dpo-chosen-curve`、`pt-dpo-derive`、`pt-dpo-chosen`、`pt-dpo-beta`。
2. 长度和 SimPO 这块，要解释模型怎么利用隐式奖励里的长度偏置提高得分；SimPO 则去掉 reference，并做长度归一化，见 `baidu-simpo-vs-dpo-length`。
3. PPO / GAE / GRPO 要讲清 clip 在 $A\gt 0$ / $A\lt 0$ 时各限制哪一侧（`baidu-ppo-clip-sign`、`code-ppo-clip`），$\lambda$ 怎么影响偏差和方差（`baidu-gae-lambda`、`code-gae`），组内优势和损失怎么聚合（`baidu-grpo-loss-agg`、`pt-grpo`），off-policy 里各策略的角色（`baidu-grpo-policy-roles-offpolicy`），以及样本量和收敛（`baidu-rl-sample-size-convergence`）。
4. 系统和推理看 MoE / Latent Attention（`arch-moe`、`arch-mla`）、投机解码（`sys-specdecode`）和 Qwen2 监督微调（SFT）的实现（`baidu-qwen2-sft-implementation`）。
5. Agent 方向看指令冲突（`baidu-agent-instruction-conflict`）和代码 Agent 的 verifier（`baidu-code-agent-verifier`）。

## 本手册真题卡

下面每条点进去就能跳到对应题。

- `baidu-dpo-chosen-curve`：DPO 对齐曲线与正例概率是否上升
- `baidu-simpo-vs-dpo-length`：SimPO 如何缓解过长
- `baidu-gae-lambda`：GAE 中 $\lambda$ 的偏差 / 方差
- `baidu-ppo-clip-sign`：PPO clip 在优势正/负时限制哪一侧
- `baidu-grpo-loss-agg`：GRPO loss 如何聚合
- `baidu-grpo-policy-roles-offpolicy`：GRPO 里各策略角色与 off-policy
- `baidu-rl-sample-size-convergence`：RL 样本量与收敛
- `baidu-agent-instruction-conflict`：Agent 指令冲突
- `baidu-code-agent-verifier`：代码 Agent 如何用 verifier
- `baidu-qwen2-sft-implementation`：Qwen2 SFT 实现细节

## 追问

**chosen 概率一定会升吗？**
不一定。相对 rejected 的间隔可以升，绝对的 $p(y_w)$ 仍可能降，面试时把曲线画出来最清楚。

**有了 DPO 为什么还要 SimPO？**
DPO 的隐式奖励分数如果和长度高度相关，模型就会靠写长回答提高得分。SimPO 用长度归一和目标间隔来处理，见 `baidu-simpo-vs-dpo-length`。

**Agent 岗少准备什么最容易挂？**
只背 post-training，说不清冲突指令和可执行校验。按上面的 id 把相关追问逐题过一遍。

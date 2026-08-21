---
id: company-baidu
section: companies
order: 4
level: A
title: 百度 AIDU：大模型与 Agent 岗该怎么定向准备？
quick: >-
  Post-training 重点准备 SFT/RLHF、DPO dynamics、GRPO/SimPO、Reasoning、MoE/Latent
  Attention、speculative decoding 与分布式训练；Agent 岗额外覆盖
  Tool/API、Memory、RAG+Agent、Multi-Agent 与 Eval。
tags:
  - Baidu
  - AIDU
  - 真题导航
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ 百度 2027 AIDU 招聘
    url: 'https://talent.baidu.com/jobs/list?projectType=3&recruitType=GRADUATE'
    type: legacy-reference
  - title: ↗ 腾讯/百度/MiniMax 公开面经汇总
    url: 'https://www.nowcoder.com/feed/main/detail/8cab51ef9458459595cf81fda43da279'
    type: legacy-reference
---

百度公开面经很少停在「DPO 是什么」。陷阱是只背公式，却答不出 chosen 概率是否一定上升、length issue、SimPO 相对 DPO 改了哪一项、以及 Base 模型如何增强 reasoning。准备单位应是**追问树**，不是词条：推导 → $\beta$ → chosen/rejected likelihood → 长度偏置 → hard negatives → SimPO/KTO → offline vs online RL。Agent 岗另加指令冲突、代码 verifier，不要用「会调工具」收束。

## 准备主线

1. **DPO 动力学**：chosen 概率不必单调上升；要能画对齐曲线并解释 reference 与 $\beta$。见 `baidu-dpo-chosen-curve`、`pt-dpo-derive`、`pt-dpo-chosen`、`pt-dpo-beta`。
2. **长度与 SimPO**：隐式奖励含长度项时如何 hack；SimPO 去掉 reference、用长度归一。见 `baidu-simpo-vs-dpo-length`。
3. **PPO / GAE / GRPO**：clip 在 $A\gt 0$ / $A\lt 0$ 各限制哪一侧（`baidu-ppo-clip-sign`、`code-ppo-clip`）；$\lambda$ 的偏差/方差（`baidu-gae-lambda`、`code-gae`）；组内优势与 loss 聚合（`baidu-grpo-loss-agg`、`pt-grpo`）；off-policy 角色（`baidu-grpo-policy-roles-offpolicy`）；样本量与收敛（`baidu-rl-sample-size-convergence`）。
4. **系统与推理**：MoE / Latent Attention（`arch-moe`、`arch-mla`）、投机解码（`sys-specdecode`）、Qwen2 SFT 实现（`baidu-qwen2-sft-implementation`）。
5. **Agent**：指令冲突（`baidu-agent-instruction-conflict`）、代码 Agent 的 verifier（`baidu-code-agent-verifier`）。

## 本手册真题卡

点击下面每条即可跳到对应题。

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

- **chosen 概率一定升吗？** 不一定。相对 rejected 的间隔可以升，绝对 $p(y_w)$ 仍可能降。把曲线画出来。
- **为什么还要 SimPO？** DPO 的 implicit reward 与长度共线时会写长；SimPO 用长度归一和目标间隔，见对应卡。
- **Agent 岗少准备什么会挂？** 只背 post-training、说不清冲突指令与可执行校验。按上面 id 刷追问树，不要背招聘 JD。

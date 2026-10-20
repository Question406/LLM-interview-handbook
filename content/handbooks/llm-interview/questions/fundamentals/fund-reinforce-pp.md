---
id: fund-reinforce-pp
section: fundamentals
order: 153
level: A
title: REINFORCE++ 怎么降方差？和 GRPO / PPO 的无偏性差在哪？
quick: "不用 critic，在全局 batch 上对 advantage 减均值、除标准差，而不是在 prompt 组内除 $\\sigma$。偏差随 batch 变大而消失，也避开了 GRPO 小 $G$ 时按题重加权的问题。"
tags:
  - REINFORCE++
  - GRPO
  - PPO
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: REINFORCE++ — Stabilizing Critic-Free Policy Optimization with Global Advantage Normalization
    url: https://arxiv.org/abs/2501.03262
    type: primary
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: secondary
---

常见误区是：「PPO 去掉 critic」或「GRPO 换个名字」。三者差在 baseline 的作用域，以及还要不要组。PPO 用 learned $V$ + GAE，有 bootstrap 偏差，见 `fund-optimal-baseline`。GRPO / RLOO 用同一输入提示 的 $G$ 条当 $b(s)$，小 $G$ 除 $\sigma$ 有题目级偏，见 `fund-finite-sample-baseline`、`pt-drgrpo`。REINFORCE++ 的主张：输入提示（prompt） 级局部标准化是有偏且易过拟合单题的，改成全局 batch 标准化，batch 大时接近无偏。

## 怎么降方差：全局标准化，而不是组 $\sigma$

实现骨架仍是带 clip 的 REINFORCE / PPO surrogate，没有 value 网络。奖励侧常把 token 级 KL 写进 $r$（类似 PPO 的 $k_1$ 写入 reward，stop-gradient），再

$$
\hat A=\frac{r-\mathrm{mean}_{\mathrm{batch}}(r)}{\mathrm{std}_{\mathrm{batch}}(r)+\varepsilon}.
$$

均值是常数 baseline，无偏族；除的是 全局 $\sigma$，不按题放大「大家都差不多对」的微小分差。论文称这是 effective unbiased：偏差 $O(1/N_{\mathrm{batch}})$，随 batch 消失。对比 GRPO 的 $O(1/G)$ 且 $G$ 常为 8。$k=1$（每题一条）时 GRPO 的相对优势没有定义，REINFORCE++ 仍能更新，用的是跨题对照，不是组内对照。代价是：不同难度的题被装进同一个 $\sigma$，batch 配方变了，同一条轨迹的 $A$ 含义就变；也抹不掉「这题绝对该不该加强」，只是抹的粒度从组改成了 batch。

仍用 PPO clip，所以越界 token 的梯度照样可以为 0。无偏讨论的是 advantage 估计；clip 是另一轴，见 `fund-pg-unbiased-ops`。slime / veRL 里对应 `--advantage-estimator reinforce_plus_plus`，和 `grpo` 同一层开关，见 `slime-advantage-estimator`。

## Baseline 变体：组减均值 + 全局 $\sigma$

推理 / 可验证奖励上，同题多条仍然有用。REINFORCE++-baseline（$k\gt 1$）先

$$
\tilde r_i=r_i-\frac1k\sum_{j=1}^k r_j,
$$

再对 $\tilde r$ 做全局标准化。组减均值提供 prompt 内 control variate（含自身则仍有 $1/k$ 收缩）；全局 $\sigma$ 避免小 $G$ 的噪尺度。全对组减完仍是 0，这一步同样没信号，动态采样照样要，见 `pt-grpo-variance`。不要说「上了 REINFORCE++ 就不用管零方差组」。

和 RLOO 比：RLOO 强调 leave-one-out、通常不除 $\sigma$，尺度是原始 reward。REINFORCE++ 更强调全局 whitening 与 PPO 工程件（clip、token KL）。现场按任务选：一般 基于人类反馈的强化学习（RLHF）、要 prompt 覆盖，$k=1$ 的全局标准化省生成；数学推理要组内正负样本，用 baseline 变体或 GRPO，并想清楚要不要除组 $\sigma$。

## 追问

- **比 PPO 更无偏吗？** Advantage 一侧：不 bootstrap，大 batch 时比 GAE 更接近 MC+常数 baseline。Clip、KL in reward 仍偏。没有 Critic，也难以对逐步状态做细致的奖励归因，长程过程奖可能还是要回 PPO。
- **比 GRPO 更无偏吗？** 相对「组内除 $\sigma$」这一层，是的，这是论文主打的 bias。相对「减均值含自身」，两者有限样本都有收缩；RLOO 更干净。
- **全局 $\sigma$ 会不会让难题没梯度？** 会。高方差难题的 $A$ 被压扁，和组内除 $\sigma$ 方向不同但同类。盯各难度桶的平均 $|A|$，不要只看均值 reward。
- **$k=1$ 还要 clip 吗？** 要。没有组相对，单条噪声更大，更依赖 clip 和 KL，而不是更不需要。

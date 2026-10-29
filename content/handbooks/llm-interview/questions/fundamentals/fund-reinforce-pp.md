---
id: fund-reinforce-pp
section: fundamentals
order: 153
level: A
title: REINFORCE++ 怎么降方差？和 GRPO / PPO 的无偏性差在哪？
quick: "REINFORCE++ 不用 critic，在全局 batch 上对 advantage 减均值、除标准差，不在 prompt 组内除 $\\sigma$。偏差随 batch 变大而消失，也避开了 GRPO 小 $G$ 时按题重加权的问题。"
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

REINFORCE++ 降方差靠的是全局 batch standardization：不用 critic，把 advantage 在整个 batch 上减均值、除标准差。它和 PPO、GRPO 的差别在 baseline 的作用域，以及还要不要组。PPO 用学出来的 $V$ 加 GAE，有 bootstrap 偏差，见 `fund-optimal-baseline`；GRPO / RLOO 拿同一 prompt 的 $G$ 条回答当 $b(s)$，小 $G$ 时再除 $\sigma$ 有题目级偏差，见 `fund-finite-sample-baseline`、`pt-drgrpo`；REINFORCE++ 认为 prompt 级的局部 standardization 有偏、还容易 overfitting 单题，改成全局 batch standardization，batch 大时接近无偏。所以把它说成「PPO 去掉 critic」或「GRPO 换个名字」都不准确。

## 全局 standardization 怎么做

实现骨架仍是带 clip 的 REINFORCE / PPO surrogate，没有 value 网络。奖励一侧常把 token 级 KL 写进 $r$（类似 PPO 把 $k_1$ 写入 reward，stop-gradient），然后

$$
\hat A=\frac{r-\mathrm{mean}_{\mathrm{batch}}(r)}{\mathrm{std}_{\mathrm{batch}}(r)+\varepsilon}.
$$

减均值相当于常数 baseline，还在无偏族里；除的是全局 $\sigma$，不会按题放大「大家都差不多对」时的微小分差。论文称之为 effective unbiased：偏差是 $O(1/N_{\mathrm{batch}})$，随 batch 变大而消失；对比 GRPO 的 $O(1/G)$，而 $G$ 常常只有 8。每题只采一条（$k=1$）时，GRPO 的相对优势没有定义，REINFORCE++ 还能更新，它用的是跨题对照。

代价也有。不同难度的题被装进同一个 $\sigma$，batch 配方一变，同一条轨迹的 $A$ 含义就变了；「这道题绝对该不该加强」它也抹不掉，只是抹的粒度从组换成了 batch。它仍然用 PPO clip，越界 token 的梯度照样可以为 0。无偏讨论的是 advantage 估计，clip 是另一条轴，见 `fund-pg-unbiased-ops`。在 slime / veRL 里，它对应 `--advantage-estimator reinforce_plus_plus`，和 `grpo` 是同一层开关，见 `slime-advantage-estimator`。

## Baseline 变体：组内减均值，再全局除 $\sigma$

推理和可验证奖励任务里，同一道题采多条还是有用的。REINFORCE++-baseline（$k\gt 1$）先做

$$
\tilde r_i=r_i-\frac1k\sum_{j=1}^k r_j,
$$

再对 $\tilde r$ 做全局 standardization。组内减均值提供 prompt 内的 control variate（均值含自身，所以仍有 $1/k$ 的收缩）；全局 $\sigma$ 避开了小 $G$ 的噪声尺度。全对的组减完还是 0，这一步一样没信号，动态 sampling 照样要做，见 `pt-grpo-variance`。所以别说「上了 REINFORCE++ 就不用管零方差组」。

和 RLOO 比，RLOO 强调 leave-one-out，通常不除 $\sigma$，用的是原始 reward 的尺度；REINFORCE++ 更强调全局 whitening 和 PPO 的工程组件（clip、token KL）。现场按任务选：一般的 RLHF 要的是 prompt 覆盖，$k=1$ 加全局 standardization 能省生成；数学推理需要组内有正有负，就用 baseline 变体或 GRPO，同时想清楚要不要除组内 $\sigma$。

## 追问

**它比 PPO 更无偏吗？**
在 advantage 这一侧是的：不做 bootstrap，batch 大时比 GAE 更接近 MC 加常数 baseline。Clip、KL in reward 照样有偏。没有 Critic，也很难对逐步状态做细致的奖励归因，长程过程奖励可能还是要回到 PPO。

**它比 GRPO 更无偏吗？**
相对「组内除 $\sigma$」这一层，是的，这正是论文主打的那个 bias。相对「减均值含自身」，两者在有限样本下都有收缩，RLOO 更干净。

**全局 $\sigma$ 会不会让难题没梯度？**
会。高方差难题的 $A$ 会被压扁，方向和组内除 $\sigma$ 不同，但属于同一类问题。要盯各难度桶的平均 $|A|$，光看平均 reward 看不出来。

**$k=1$ 还要 clip 吗？**
要，而且更依赖。没有组相对，单条样本的噪声更大，更需要 clip 和 KL 兜着。

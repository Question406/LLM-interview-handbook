---
id: fund-pg-unbiased-ops
section: fundamentals
order: 146
level: S
title: 策略梯度里哪些操作仍无偏？哪些会引入偏差？
quick: >-
  相对 $\nabla J=\mathbb{E}_{\pi}[\nabla\log\pi\cdot G]$：reward-to-go、只依赖 $s$ 的
  baseline、普通 IS 仍无偏。用 $V$ bootstrap、clip / 截断权重、除组标准差、自归一化 IS、对当前样本自己当
  baseline，都会偏。无偏但方差炸掉，工程上并不更优。
tags:
  - RL
  - Policy Gradient
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Simple Statistical Gradient-Following Algorithms for Connectionist Reinforcement Learning (REINFORCE)
    url: https://link.springer.com/article/10.1007/BF00992696
    type: primary
  - title: Policy Gradient Methods for Reinforcement Learning with Function Approximation
    url: https://proceedings.neurips.cc/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html
    type: primary
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: https://arxiv.org/abs/1506.02438
    type: primary
---

常见误区是：把「无偏」当成道德词，好像 MC 一定比 GAE 高级、clip 一定是作弊。先说清无偏是相对于哪条期望，再把操作分成两类。相对的是 on-policy 策略梯度

$$
\nabla_\theta J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}\Big[\sum_t\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\Big],
$$

不是「reward 曲线好看」或「advantage 均值为 0」。推导见 `fund-pg-theorem`。无偏但方差高到梯度是噪声，工程上没有决策价值；有偏但能训，要能说出偏了哪一块目标。总览见 `fund-biasvariance`。

## 仍无偏：只改方差，不改期望

下面这些操作，期望梯度与上式相同，只改变方差。

- Reward-to-go：把整段 $R$ 换成从 $t$ 起的 $G_t$。$t$ 之前的奖励不依赖 $a_t$，乘进去仍无偏，但多乘了一截噪声。
- 只依赖 state（或常数）的 baseline。$\mathbb{E}_{a\sim\pi}[\nabla\log\pi(a\mid s)b(s)]=0$，所以 $G_t-b(s_t)$ 不改期望。$V$ 再不准，只要它不是当前 sampled action 的函数、也不拿去替换未来回报，MC 优势 $G_t-V(s_t)$ 仍然无偏。见 `fund-pg-baseline`、`fund-optimal-baseline`。
- 普通重要性采样：数据来自 $\mu$，乘 $\rho=\pi/\mu$，在 support 覆盖时 $\mathbb{E}_\mu[\rho f]=\mathbb{E}_\pi[f]$。无偏，方差随 $\rho$ 尾部爆炸。见 `fund-is`。

这三步是「先会无偏梯度，再谈降方差」的全部合法手段。现场应能默写为什么 baseline 那条期望是 0，而不是只说「减个均值更稳」。

## 会引入偏差：用 $V$ 替未来、截断、改权重

这些操作让估计的期望不再等于原来的 $\nabla J$，换的是可训练性。

| 操作 | 偏在哪 | 换来什么 |
| --- | --- | --- |
| TD / GAE $\lambda\lt 1$ | 用 $V(s')$ bootstrap 截断回报 | 低方差；依赖 Critic 的估计质量 |
| PPO / GRPO clip surrogate | 越界 token 的梯度变为 0 | 近似 trust-region |
| 截断 IS、V-trace、CISPO 封顶 $\rho$ | $\mathbb{E}[\mathrm{clip}(\rho)f]\neq\mathbb{E}_\pi[f]$ | 挡住爆炸权重 |
| Self-normalized IS | 分母是随机的，有限样本有偏 | 更稳、ESS 可读 |
| 组 / batch 除 $\sigma$ | 题目、batch 被重新加权 | 尺度统一，改 calibration |
| 按长度平均 loss | 每条回复等权，不是每 token 等权 | 压长尾或反过来 |
| 组均值含当前样本 | 有限样本下自己抵消自己 | $G$ 大时接近无偏 |

GAE 的偏差来自 bootstrap，不是来自「减了 $V$」。把 $G_t-V$ 和 $\sum(\gamma\lambda)^l\delta_{t+l}$ 说成同一件事，下一问会拆穿。clip 也不是无偏的方差公式，见 `pt-cispo`、`fund-vtrace`。除标准差、长度归约是在定义隐式目标，见 `fund-adv-norm-bias`、`pt-drgrpo`。

## 怎么收

先写目标 $\nabla J$，再指着配方说：哪几步还在无偏族，哪几步已经换目标。可验证短答案可以偏左（MC、大 $\lambda$、少 clip）；开放生成且奖励模型（RM）噪声较大时 必须偏右，再用金标看有没有优化到长度或套话。不要声称某一个 $\lambda$ 或 $\varepsilon$ 普遍最优。

## 追问

- **Unbiased 是否总更好？** 否。方差过大时有效更新接近噪声。先问能不能训，再问偏了什么。
- **减错的 $V$ 还无偏吗？** MC 减任意 $b(s)$ 仍无偏；用错的 $V$ 去 bootstrap 就偏。见 `fund-optimal-baseline`。
- **GRPO 减组均值无偏吗？** $G\to\infty$ 时接近；有限 $G$ 且含自身、再除 $\sigma$，两层偏。见 `fund-finite-sample-baseline`。
- **Clip 是 variance reduction 吗？** 主要是限制危险更新并改目标。不要说成无偏的控制变量。

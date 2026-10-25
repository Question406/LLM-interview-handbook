---
id: fund-pg-unbiased-ops
section: fundamentals
order: 146
level: S
title: 策略梯度里哪些操作仍无偏？哪些会引入偏差？
quick: "以 $\\nabla J=\\mathbb{E}_{\\pi}[\\nabla\\log\\pi\\cdot G]$ 为准，reward-to-go、只依赖 $s$ 的 baseline、普通 IS 仍然无偏。用 $V$ bootstrap、clip 或截断权重、除组标准差、自归一化 IS、拿当前样本给自己当 baseline，都会引入偏差。无偏但方差炸掉，工程上并不更好。"
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

仍然无偏的只有三类：reward-to-go、只依赖状态的 baseline、普通重要性采样，它们只改方差；用 $V$ bootstrap、各种 clip 和截断、改样本权重，都会引入偏差。这里的无偏是相对 on-policy 策略梯度说的：

$$
\nabla_\theta J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}\Big[\sum_t\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\Big],
$$

跟 reward 曲线好不好看、advantage 均值是不是 0 都没关系，推导见 `fund-pg-theorem`。无偏也不代表更高级，MC 不一定比 GAE 好，clip 也不算作弊。方差高到梯度全是噪声，工程上没有决策价值；有偏但能训，只要说得出偏了哪一块目标就行。总览见 `fund-biasvariance`。

## 仍无偏的操作：只改方差

Reward-to-go 把整段 $R$ 换成从 $t$ 起的 $G_t$。$t$ 之前的奖励不依赖 $a_t$，乘进去也无偏，只是多乘了一截噪声，去掉它只影响方差。

只依赖 state（或常数）的 baseline 也一样。$\mathbb{E}_{a\sim\pi}[\nabla\log\pi(a\mid s)b(s)]=0$，所以 $G_t-b(s_t)$ 不改期望。$V$ 再不准，只要它不是当前采样动作的函数，也不拿去替换未来回报，MC 优势 $G_t-V(s_t)$ 就仍然无偏，见 `fund-pg-baseline`、`fund-optimal-baseline`。

普通重要性采样的数据来自 $\mu$，乘上 $\rho=\pi/\mu$，在 support 覆盖时 $\mathbb{E}_\mu[\rho f]=\mathbb{E}_\pi[f]$，所以无偏，代价是方差随 $\rho$ 的尾部爆炸，见 `fund-is`。

这三步就是「先会无偏梯度，再谈降方差」的全部合法手段。现场最好能当场写出 baseline 那条期望为什么是 0，光说「减个均值更稳」不够。

## 会引入偏差的操作：用 $V$ 替未来、截断、改权重

这些操作让估计的期望不再等于原来的 $\nabla J$，换来的是可训练性。

| 操作 | 偏在哪 | 换来什么 |
| --- | --- | --- |
| TD / GAE $\lambda\lt 1$ | 用 $V(s')$ bootstrap 截断回报 | 低方差；依赖 Critic 的估计质量 |
| PPO / GRPO clip surrogate | 越界 token 的梯度变为 0 | 近似 trust-region |
| 截断 IS、V-trace、CISPO 封顶 $\rho$ | $\mathbb{E}[\mathrm{clip}(\rho)f]\neq\mathbb{E}_\pi[f]$ | 挡住爆炸权重 |
| Self-normalized IS | 分母是随机的，有限样本有偏 | 更稳、ESS 可读 |
| 组 / batch 除 $\sigma$ | 题目、batch 被重新加权 | 尺度统一，改 calibration |
| 按长度平均 loss | 每条回复等权，不是每 token 等权 | 压长尾或反过来 |
| 组均值含当前样本 | 有限样本下自己抵消自己 | $G$ 大时接近无偏 |

GAE 的偏差来自 bootstrap，减 $V$ 本身不带来偏差。把 $G_t-V$ 和 $\sum(\gamma\lambda)^l\delta_{t+l}$ 说成同一件事，下一问就会被拆穿。Clip 也算不上无偏的降方差公式，见 `pt-cispo`、`fund-vtrace`。除标准差、按长度归约，其实是在定义一个隐式目标，见 `fund-adv-norm-bias`、`pt-drgrpo`。

## 面试时怎么收

先写出目标 $\nabla J$，再对着自己的训练配方说：哪几步还在无偏族里，哪几步已经换了目标。比如可验证的短答案任务，可以靠无偏那一侧走（MC、大 $\lambda$、少 clip）；开放生成且奖励模型（RM）噪声较大时，就得往有偏那一侧走，再用金标看模型有没有在优化长度或套话。别声称某一个 $\lambda$ 或 $\varepsilon$ 普遍最优。

## 追问

**无偏是不是总更好？**
不是。方差过大时，有效更新接近噪声。先问能不能训，再问偏了什么。

**减一个估错的 $V$ 还无偏吗？**
无偏。MC 减任意 $b(s)$ 都无偏，用错的 $V$ 去 bootstrap 才偏，见 `fund-optimal-baseline`。

**GRPO 减组均值无偏吗？**
$G\to\infty$ 时接近无偏。有限 $G$、均值含自身，再除 $\sigma$，就是两层偏差，见 `fund-finite-sample-baseline`。

**Clip 算 variance reduction 吗？**
主要算限制危险更新，同时改了目标。别把它说成无偏的控制变量。

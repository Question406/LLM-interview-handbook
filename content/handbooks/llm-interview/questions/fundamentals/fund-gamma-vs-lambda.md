---
id: fund-gamma-vs-lambda
section: fundamentals
order: 157
level: S
title: $\gamma$ 和 $\lambda$ 为什么不能合成一个乘积？谁改目标、谁改估计器？
quick: >-
  $\gamma$ 写在 $J(\theta)=\mathbb{E}[\sum_t\gamma^t r_t]$ 里，改的是任务：多远的奖励还算数。$\lambda$
  只出现在 GAE 的 $(\gamma\lambda)^l$，改的是估计器：多信 bootstrap、多信轨迹。GAE 权重里确实出现乘积，但把
  $\gamma\lambda$ 当成一个超参，等于偷偷改了你在优化的东西。
tags:
  - GAE
  - Discount
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: https://arxiv.org/abs/1506.02438
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: secondary
---

这块容易看见 GAE 的 $(\gamma\lambda)^l$ 就说「两个数一个意思，设成 0.99 就行」。百度真题原话要的是 $\lambda$ 与偏差/方差，见 `baidu-gae-lambda`；本题把 **目标 vs 估计器** 拆开。公式：

$$
J(\theta)=\mathbb{E}_{\pi_\theta}\Big[\sum_{t\ge 0}\gamma^t r_t\Big],\qquad
\hat A_t^{\mathrm{GAE}}=\sum_{l\ge 0}(\gamma\lambda)^l\delta_{t+l}.
$$

$\gamma$ 出现在两处，语义不同。第一处定义 $V^\pi,Q^\pi,A^\pi$ 是对哪个折扣任务说的；第二处只是估计器把 $\gamma$ 和 $\lambda$ 乘在一起衰减残差。

## $\gamma$：改 $J$，不是「更有偏的估计」

把 $\gamma$ 从 $0.99$ 拧到 $0.9$，最优策略可以变：远期正确、近期啰嗦的思维链会变亏。这不是估计器偏差 $\mathbb{E}[\hat A]-A^\pi$，因为 $A^\pi$ 本身已经换成新 $\gamma$ 下的优势。把小 $\gamma$ 说成「有偏」，是把监督学习的 bias 套错了地方。

LLM 里常取 $\gamma=1$（有限长度、终局 $0/1$），等于不打折。这时早期 token 的 $G_t$ 仍是完整 $r_T$，方差见 `fund-pg-horizon-var`。若因为「太吵」就偷偷把 $\gamma$ 降到 $0.95$，你优化的已经是短视任务：长推理的后期正确被打折，模型更爱早停。那是改题，不是降方差。

## $\lambda$：只改 $\hat A$ 相对当前 $A^\pi$ 的偏差-方差

$\lambda=0$：$\hat A_t=\delta_t$，完全信 $V$，高偏低方。$\lambda=1$：回到 MC 优势，低偏高方。中间值在 **同一个 $J$、同一套 $\gamma$** 下滑动估计器。$V$ 准可以更小 $\lambda$；$V$ 滞后或长 CoT 拟合差，把 $\lambda$ 推向 1，而不是去动 $\gamma$。推导见 `pt-gae`。

实现上权重是 $(\gamma\lambda)^l$，所以 $\gamma=1,\lambda=0.95$ 与 $\gamma=0.95,\lambda=1$ 的递推系数碰巧接近，**优化的 $J$ 完全不同**。前者仍在最大化未折扣回报，只是估计更平滑；后者已经不在乎很远的 $r$。白板要写两行定义，不能只写一个乘积。

GRPO 没有 $\lambda$：没有逐步 $V$，也就没有这根估计器旋钮。组大小 $G$ 承担的是 baseline 方差，不是折扣。不要把「加大 $G$」说成「相当于加大 $\lambda$」，一个不改目标，一个 GAE 里也不该去改 $\gamma$。

## 追问

- **$\gamma=1$ 会不会不收敛？** 有限回合、有终局奖时 $J$ 有界。无限 horizon 且回报不衰减才需要 $\gamma\lt 1$ 保证 $V$ 存在。
- **PPO 论文默认 $\gamma=0.99,\lambda=0.95$ 能直接搬到 LLM 吗？** 控制任务的有效 horizon 和 CoT token 数不是一个量级。LLM 更常见 $\gamma=1$，用 $\lambda$ 或组相对管方差。
- **过程奖励还要 $\gamma$ 吗？** 要，它仍定义「多远的过程分算进回报」。过程分已经密时，$\lambda$ 可以更小，因为不需要把终局奖传很远。
- **和 KL 系数 $\beta$ 像吗？** 都不改变「无偏 PG」本身：$\beta$ 改的是加了 KL 之后的目标，$\gamma$ 改折扣目标，$\lambda$ 才是纯估计器。

---
id: fund-gamma-vs-lambda
section: fundamentals
order: 157
level: S
title: $\gamma$ 和 $\lambda$ 为什么不能合成一个乘积？谁改目标、谁改估计器？
quick: >-
  $\gamma$ 写在 $J(\theta)=\mathbb{E}[\sum_t\gamma^t r_t]$ 里，改的是任务：多远的奖励还算数；$\lambda$ 只出现在 GAE 的 $(\gamma\lambda)^l$ 里，改的是估计器：多信 bootstrap、多信轨迹。GAE 权重里确实是乘积，但把 $\gamma\lambda$ 当成一个超参去调，等于偷偷改了你在优化的东西。
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
因为 $\gamma$ 改的是目标，$\lambda$ 改的是估计器，乘在一起只是 GAE 递推里碰巧的写法。$\gamma$ 决定多远的奖励还算数，换了 $\gamma$，最优策略都可能变；$\lambda$ 只决定估计优势时多信 $V$、多信真实轨迹，目标不动。看见 $(\gamma\lambda)^l$ 就说「两个数一个意思，设成 0.99 就行」，会被追问卡住。百度真题原话问的是 $\lambda$ 与偏差 / 方差，见 `baidu-gae-lambda`，这张卡把目标和估计器拆开讲。

先写公式：

$$
J(\theta)=\mathbb{E}_{\pi_\theta}\Big[\sum_{t\ge 0}\gamma^t r_t\Big],\qquad
\hat A_t^{\mathrm{GAE}}=\sum_{l\ge 0}(\gamma\lambda)^l\delta_{t+l}.
$$

$\gamma$ 在两处都出现，含义不同。第一处定义了 $V^\pi,Q^\pi,A^\pi$ 是针对哪个折扣任务说的；第二处只是估计器把 $\gamma$ 和 $\lambda$ 乘在一起去衰减残差。

## $\gamma$：改的是 $J$

把 $\gamma$ 从 $0.99$ 拧到 $0.9$，最优策略可能就变了：远期才做对、近期啰嗦的 chain of thought 会变得不划算。这跟估计器偏差 $\mathbb{E}[\hat A]-A^\pi$ 是两回事，因为 $A^\pi$ 本身已经换成新 $\gamma$ 下的优势了。把小 $\gamma$ 说成「有偏」，是把监督学习里的 bias 套错了地方。

LLM 里常取 $\gamma=1$（长度有限、终局给 $0/1$），也就是不打折。这时早期 token 的 $G_t$ 仍是完整的 $r_T$，方差问题见 `fund-pg-horizon-var`。如果因为估计噪声大就把 $\gamma$ 降到 $0.95$，优化的已经是一个短视的任务：长推理后期的正确被打了折，模型更爱早停。这改变的是优化任务本身，影响不止估计方差。

## $\lambda$：只改 $\hat A$ 相对当前 $A^\pi$ 的偏差和方差

$\lambda=0$ 时 $\hat A_t=\delta_t$，完全信 $V$，偏差较高、方差较低；$\lambda=1$ 时回到 MC 优势，偏差较低、方差较高。中间的值是在同一个 $J$、同一套 $\gamma$ 下滑动估计器。$V$ 准就可以用小一点的 $\lambda$；$V$ 滞后或者长 CoT 拟合得差，该把 $\lambda$ 推向 1，别去动 $\gamma$。推导见 `pt-gae`。

举个例子，$\gamma=1,\lambda=0.95$ 和 $\gamma=0.95,\lambda=1$，因为实现上权重是 $(\gamma\lambda)^l$，两者的递推系数碰巧很接近，优化的 $J$ 却完全不同。前者仍在最大化未折扣的回报，只是估计更平滑；后者已经不在乎很远的 $r$ 了。所以白板上要写两行定义，别只写一个乘积。

GRPO 里没有 $\lambda$：没有逐步的 $V$，也就没有这根估计器旋钮。组大小 $G$ 管的是 baseline 方差，跟折扣无关。别把「加大 $G$」说成「相当于加大 $\lambda$」，前者不改目标，GAE 里也不该靠改 $\gamma$ 去调方差。

## 追问

**$\gamma=1$ 会不会不收敛？**
有限回合、有终局奖励时 $J$ 是有界的。只有无限 horizon 且回报不衰减时，才需要 $\gamma\lt 1$ 来保证 $V$ 存在。

**PPO 论文默认的 $\gamma=0.99,\lambda=0.95$ 能直接搬到 LLM 吗？**
不能直接搬。控制任务的有效 horizon 和 CoT 的 token 数不在一个量级，LLM 更常见的是 $\gamma=1$，用 $\lambda$ 或组相对来管方差。

**有过程奖励时还要 $\gamma$ 吗？**
要，它仍然定义了多远的过程分要算进回报。过程分已经很密时，$\lambda$ 可以更小，因为不需要把终局奖励传得很远。

**和 KL 系数 $\beta$ 像吗？**
在「不改无偏 PG 本身」这点上像：$\beta$ 改的是加了 KL 之后的目标，$\gamma$ 改的是折扣目标，只有 $\lambda$ 是纯粹的估计器旋钮。

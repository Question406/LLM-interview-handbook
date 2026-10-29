---
id: fund-kl-k1-k2-k3
section: fundamentals
order: 144
level: S
title: Schulman 的 $k_1/k_2/k_3$ 各估什么？数值无偏和梯度正确是一回事吗？
quick: >-
  三个都估同一条 reverse KL。$r=p/q$ 时，$k_1=-\log r$ 无偏但方差大，$k_2=\frac12(\log r)^2$
  有偏但平滑，$k_3=r-1-\log r$ 无偏且非负。数值无偏不等于梯度对：$k_3$ 直接当 loss backpropagation，得到的梯度不是
  reverse KL 的梯度。
tags:
  - KL
  - GRPO
  - PPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Approximating KL Divergence
    url: 'http://joschu.net/blog/kl-approx.html'
    type: primary
  - title: 蚂蚁大模型一面（被问懵版）
    url: 'https://www.nowcoder.com/feed/main/detail/1a1a229b1d9f4a5bbfcb6ea6c9857339'
    type: candidate-first-hand
  - title: RL 中的 KL 估计器选型
    url: >-
      https://xihuai18.github.io/reinforcement-learning/2025/12/01/kl-estimators-zh.html
    type: secondary
---
$k_1/k_2/k_3$ 是 Schulman 给同一条 reverse KL 设计的三个单样本估计，不是三种散度：$k_1$ 无偏但方差大，$k_2$ 有偏但平滑，$k_3$ 既无偏又非负。数值无偏和梯度正确是两回事，「$k_3$ 无偏，所以拿它当 loss backpropagation 一定对」这一步是错的。蚂蚁一面原话是「GRPO 的 KL 和 PPO 的 KL 区别？K1 K2 K3 估计区别？」，答的时候先把符号固定下来，再把「无偏」两个字拆开。

要估的是 reverse KL

$$
D_{\mathrm{KL}}(q\|p)=\mathbb{E}_{x\sim q}\Big[\log\frac{q(x)}{p(x)}\Big],
$$

样本来自 $q$（当前策略 $\pi_\theta$），$p$ 是冻结的参考 $\pi_{\mathrm{ref}}$，比率记作

$$
r=\frac{p}{q}=\frac{\pi_{\mathrm{ref}}}{\pi_\theta}.
$$

于是 $\log(q/p)=-\log r$。三个估计是

$$
k_1=-\log r,\qquad k_2=\tfrac12(\log r)^2,\qquad k_3=(r-1)-\log r.
$$

## 三个估计分别有什么性质

$k_1$ 满足 $\mathbb{E}_q[k_1]=D_{\mathrm{KL}}(q\|p)$，是朴素的 unbiased estimate。$r\gt 1$ 时它是负的，单次 sampling 可能报出「负 KL」，方差大、日志难看，但作为随机量期望是对的。

$k_2$ 来自 $x\mapsto\frac12(\log x)^2$，是 $r\approx 1$ 附近 KL 的二阶近似。它恒非负、平滑、方差小，但期望一般不等于 KL（有偏），适合画曲线，不适合当无偏目标。

$k_3$ 是对 $k_1$ 加了控制变量 $r-1$：$\mathbb{E}_q[r-1]=0$，所以 $\mathbb{E}_q[k_3]$ 仍是 KL。又因为 $x\gt 0$ 时 $x-\ln x-1\ge 0$，样本几乎总是非负，方差通常也比 $k_1$ 小。它同时做到了单个样本非负、期望等于 KL。白板上可以补一句：$f(x)=x-1-\log x$ 在 $x=1$ 取 $0$，二阶导是 $1/x^2$，和 KL 在 $r=1$ 处的曲率一致，所以 $k_3$ 既无偏又比 $k_1$ 稳。

## PPO 扣在奖励分数（reward）里，GRPO 挂在损失（loss）上，梯度不是同一条

蚂蚁要的是实现上的这层分叉。PPO 的典型做法是把 $k_1$ 放进 reward：算出 $\hat{k}_1$ 以后 stop-gradient，写进

$$
r_t\leftarrow r_\phi-\beta\,\mathrm{sg}(\hat{k}_1),
$$

再走 score function $\nabla\log\pi_\theta\cdot(\cdots)$。对期望回报减 $\beta\,\mathrm{KL}(q\|p)$ 求导，得到的就是 reverse KL 对 $\theta$ 的 policy gradient（mode-seeking 的 drift）。这里无偏的是奖励里的那个标量，梯度之所以正确，是因为没有对 $r(\theta)$ backpropagation，只用了 $\nabla\log\pi$。

GRPO 论文把 $\beta k_3$ 当成 loss 的一项，加 on-policy 目标上。$k_3$ 作为标量仍然无偏，日志也比 $k_1$ 稳。但 $r=\pi_{\mathrm{ref}}/\pi_\theta$ 依赖 $\theta$，直接对 $k_3(\theta)$ backpropagation，链式法则会多出 $\partial k_3/\partial r\cdot\partial r/\partial\theta$，这条梯度一般不是 $\nabla_\theta D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 的 score-function 形式。Off-policy 复用旧轨迹时，如果再不乘 $\pi_\theta/\pi_{\mathrm{old}}$，连期望都是偏的。

所以说「$k_3$ 无偏所以一定对」会被追问：无偏的是标量估计，参数梯度另算。想让梯度对齐 reverse KL，就把估计量 stop-grad、当 reward shaping 用，或者显式写出 $\mathbb{E}_q[\nabla\log\pi\,(\log q-\log p)]$ 并配上 IS。如果只要一个稳定的监控数字，用 $k_3$ 或 $k_2$ 记录就行，不用 backpropagation。

## 别和「两种 KL」搅在一起

PPO clip / TRPO 管的是相对 $\pi_{\mathrm{old}}$ 的信任域，这里的 $k_1/k_2/k_3$ 估的是相对 $\pi_{\mathrm{ref}}$ 的 drift。估计器选错了，不会把 trust-region 变成 drift，只影响惩罚是否无偏、能不能 backpropagation。

## 追问

**为什么 $k_1$ 会是负的？**
单个样本的 $-\log(\pi_{\mathrm{ref}}/\pi_\theta)$ 可以是负的，KL 非负说的是期望。看到负样本就以为「KL 坏了」是误读。

**GRPO 把 $k_3$ 当 loss 是错的吗？**
作为正则启发式、为了数值稳定，工程上很常见；但如果声称「因此我们在优化无偏的 reverse KL 梯度」，那就是把标量的性质安到了梯度上。

**$k_2$ 能当 loss 吗？**
能当平滑惩罚，但它是有偏近似，对 $\theta$ backpropagation 同样不是标准的 KL 梯度。更常见的用法是只拿来 logging。

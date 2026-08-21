---
id: fund-shannon-entropy
section: fundamentals
order: 0
level: S
title: Shannon 熵是什么？为什么是 $-p\log p$？最大最小分别在哪？
quick: >-
  $H(p)=-\sum_x p(x)\log p(x)$ 是「按 $p$ 编码 $p$」的期望码长。确定事件 $H=0$；均匀分布取最大
  $\log|\mathcal{X}|$。约定 $0\log 0:=0$。LLM 里它就是 next-token 分布有多尖。
tags:
  - Math
  - Entropy
  - Probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: A Mathematical Theory of Communication (Shannon, 1948)
    url: https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf
    type: primary
  - title: Entropy (information theory)
    url: https://en.wikipedia.org/wiki/Entropy_(information_theory)
    type: reference
---

离散分布 $p$ 的 Shannon 熵

$$
H(p)=-\sum_x p(x)\log p(x)=\mathbb{E}_{x\sim p}[-\log p(x)].
$$

$-\log p(x)$ 是「看到 $x$ 有多意外」：概率越接近 $0$，码长越长。对 $p$ 自己取期望，就是平均意外程度。约定 $0\log 0:=0$（几乎不发生的点不贡献）。底数为 $2$ 时单位是 bit，自然对数是 nat；PyTorch 的 `log` / `cross_entropy` 默认 nat。

## 最小、最大

**最小。** $p$ 是 one-hot，$p(x^\star)=1$，其余为 $0$。则 $H= -1\cdot\log 1=0$。没有不确定性。

**最大。** 在 $|\mathcal{X}|=V$ 的单纯形上，$H$ 在均匀分布 $u(x)=1/V$ 处最大，值为 $\log V$。证明写进下一张「CE / KL」卡：把 $H(p)$ 改写成 $\log V-D_{\mathrm{KL}}(p\|u)$，KL 非负立刻给出上界。直觉：每个 token 机会均等，最难压。

二值情况 $p=\mathrm{Bernoulli}(\theta)$：

$$
H(\theta)=-\theta\log\theta-(1-\theta)\log(1-\theta),
$$

在 $\theta=1/2$ 取 $\log 2$，两端 $\theta\to 0$ 或 $1$ 时掉到 $0$。

## 接到 LLM

词表大小 $V$ 时，完全瞎猜的 next-token 分布接近均匀，$H\approx\log V$。训练把质量堆到正确答案上，熵下降。RL 里监控的 policy entropy 是同一条定义，只是 $p=\pi_\theta(\cdot\mid s)$。熵到 $0$ 就是 collapse：每个 state 几乎只输出一个 token。

## 白板别漏

1. 先写定义，再声明 $0\log 0$。
2. 问清 bit 还是 nat。
3. 条件熵 $H(Y\mid X)=\mathbb{E}_x[H(Y\mid X=x)]$，不是 $H(Y\mid X=x)$ 本身；联合 $H(X,Y)=H(X)+H(Y\mid X)$。
4. 连续变量的微分熵可以是负数，面试默认先答离散。

---
id: fund-shannon-entropy
section: fundamentals
order: 0
level: S
title: Shannon 熵是什么？为什么是 $-p\log p$？最大最小分别在哪？
quick: "$H(p)=-\\sum_x p(x)\\log p(x)$ 是平均的意外程度，也就是「按 $p$ 编码 $p$」的期望码长。确定事件时 $H=0$ 最小，均匀分布时取最大值 $\\log|\\mathcal{X}|$，约定 $0\\log 0:=0$。LLM 里它衡量 next-token 分布有多尖。"
tags:
  - Math
  - Entropy
  - Probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: A Mathematical Theory of Communication (Shannon, 1948)
    url: https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf
    type: primary
  - title: Entropy (information theory)
    url: https://en.wikipedia.org/wiki/Entropy_(information_theory)
    type: reference
---

Shannon 熵是平均的「意外程度」：$-\log p(x)$ 衡量看到 $x$ 有多意外，按 $p$ 自己取期望就是熵。最小值 0 出现在确定事件，最大值出现在均匀分布。离散分布 $p$ 的 Shannon 熵是

$$
H(p)=-\sum_x p(x)\log p(x)=\mathbb{E}_{x\sim p}[-\log p(x)].
$$

用 $-\log p$，是因为概率越接近 $0$，看到它越意外，编码时需要的码长也越长。比如抛一枚公平硬币，两面同样难猜，熵是 $\log 2$；一枚两面都是正面的硬币，结果毫无悬念，熵就是 0。约定 $0\log 0:=0$，几乎不发生的点不贡献。底数为 $2$ 时单位是 bit，自然对数时是 nat；PyTorch 的 `log` / `cross_entropy` 默认用 nat。

## 最小和最大

最小在 $p$ 是 one-hot 时：$p(x^\star)=1$，其余为 $0$，则 $H= -1\cdot\log 1=0$，没有任何不确定性。

最大在均匀分布：在 $|\mathcal{X}|=V$ 的单纯形上，$H$ 在 $u(x)=1/V$ 处最大，值为 $\log V$。证明写在下一张「CE / KL」卡里：把 $H(p)$ 改写成 $\log V-D_{\mathrm{KL}}(p\|u)$，KL 非负，上界立刻出来。直觉是每个 token 概率都相同，最难压缩编码。

二值情况 $p=\mathrm{Bernoulli}(\theta)$：

$$
H(\theta)=-\theta\log\theta-(1-\theta)\log(1-\theta),
$$

在 $\theta=1/2$ 时取 $\log 2$，$\theta\to 0$ 或 $1$ 时掉到 $0$。

## 放到 LLM 里

词表大小为 $V$ 时，完全瞎猜的 next-token 分布接近均匀，$H\approx\log V$。训练把更多概率集中到正确答案上，熵随之下降。强化学习（RL）里监控的 policy entropy 是同一个定义，只是 $p=\pi_\theta(\cdot\mid s)$。熵掉到 $0$ 就是 collapse：每个 state 几乎只输出一个 token。

白板上先写定义，再声明 $0\log 0$，并问清用 bit 还是 nat。

## 追问

**条件熵怎么写？**
$H(Y\mid X)=\mathbb{E}_x[H(Y\mid X=x)]$，它对 $x$ 取了期望，和 $H(Y\mid X=x)$ 本身不是一回事。联合熵 $H(X,Y)=H(X)+H(Y\mid X)$。

**连续变量的熵也一定非负吗？**
不一定，连续变量的微分熵可以是负数。面试默认先答离散情况。

---
id: arch-moe-z-loss
section: arch
order: 24
level: A
title: Router z-loss 惩罚的是什么？和 aux load-balance 为什么不是同一个旋钮？
quick: "Z-loss 惩罚每个 token 的 router logits 的 log-sum-exp 平方，压住分数幅度，防止 softmax 塌成 one-hot 和半精度溢出。Aux loss 管的是专家之间的流量是否均匀。一个控数值幅度，一个控负载，监控和系数都要分开。"
tags:
  - MoE
  - Router
  - Z-loss
  - ST-MoE
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: ST-MoE
    url: https://arxiv.org/abs/2202.08906
    type: primary
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

Router z-loss 惩罚的是 logits 的幅度：对每个 token 的 router logits 算 log-sum-exp 再平方，分数整体越大罚得越重。Aux load-balance 管的是各专家之间的流量。两者看的统计量不同，失败的样子也不同，所以是两个旋钮。

ST-MoE 单独把 logits 幅度正则掉，是因为 MoE 训练到后期 router 分数容易涨得极大，softmax 变成 one-hot，FP16 下还会溢出。被追问「那和 $N\sum_i f_i P_i$ 有什么不同」时，答成同一件事就漏了。

## 公式

对 token $t$ 的 router logits $z_t\in\mathbb{R}^{N}$：

$$
\mathcal{L}_z=\frac1T\sum_{t=1}^{T}\Bigl(\log\sum_{i=1}^{N}e^{z_{t,i}}\Bigr)^2
=\frac1T\sum_{t=1}^{T}\mathrm{LSE}(z_t)^2.
$$

$\mathrm{LSE}$ 就是 softmax 分母取对数。它大，说明这一行 logits 整体偏大或极度尖锐；平方之后，对已经很大的 token 罚得更重。实现时用 `logsumexp`，别先 `exp` 再 `sum` 再 `log`。系数 $\alpha_z$ 通常远小于 aux（ST-MoE 量级 $10^{-3}$ 到 $10^{-2}$ 量级，以论文为准），加在主交叉熵损失（CE）上：

$$
\mathcal{L}=\mathcal{L}_{\mathrm{LM}}+\lambda\mathcal{L}_{\mathrm{aux}}+\alpha_z\mathcal{L}_z.
$$

Sigmoid 门控没有单一的 $N$ 类分母，但仍可以对 affinity logits 做幅度惩罚，或者直接罚 $\|z\|_2^2$。V3 的无辅助方案管的是谁进 Top-$k$，替代不了 z-loss 的数值动机。两者也都可以不开，Mixtral 粗粒度时两样都没用。

## 和 aux 拆开看

| | Aux / bias | Z-loss |
| --- | --- | --- |
| 看什么 | 各专家的 $f_i$、$P_i$ | 每个 token 的 $\mathrm{LSE}(z)$ |
| 想阻止 | 热点 / 死专家 | 分数爆炸、softmax 塌成 one-hot、溢出 |
| 失败样子 | 直方图歪、all-to-all 拖尾 | NaN、门控全 $0/1$、训练后半段突然不稳 |
| 调太大 | 路由为了平均牺牲语义 | 路由器不敢自信，专家区分度掉 |

举两个反方向的例子。Switch 形式的 aux 在负载均匀时取最小值 $1$，和 logits 幅度无关：把分数乘 $100$ 再减一个常数，softmax 不变，$f_i$ 不变，aux 一动不动，z-loss 却会爆。反过来，所有专家流量已经均匀，logits 却涨到了 $60$，aux 看着很健康，半精度前向已经在 overflow 边缘。所以监控要两套：专家份额的 CV，以及 `router_logits.abs().max()` / `lse.mean()`。

## 实现要点

z-loss 要对 softmax 之前的 logits 算。概率已经在单纯形上，LSE 的信息没了。

它和 jitter / 噪声各管各的。Switch 训练时在 logits 上加噪声，是为了让冷专家有机会被探索；z-loss 是压幅度。两个同时开时，是先加噪声再算 LSE，还是对干净 logits 算 LSE，要在代码里写死，训推保持一致。

推理时关掉。它只是训练期的正则，导出的 router 权重已经学完了。

## 追问

**为什么要平方，直接用 LSE 不行吗？**
平方在 logits 大时罚得更狠，在 logits 小时几乎不干扰早期学习。这没有唯一的定理，是 ST-MoE 的经验选择。

**FP8 router 还要不要 z-loss？**
更要。FP8 动态范围更窄，幅度不压的话量化先崩，轮不到谈均衡。

**DeepSeek 无 aux，是不是也就没有 z-loss？**
两码事。无 aux 只说明均衡改走 bias，幅度可能仍要管。V3 主报告没把它当卖点，面试别编「V3 用了 z-loss」。

**手写的话测什么？**
把一行 logits 设成全 $50$，z-loss 应该明显大于全 $0$ 的基线；logits 均匀且小时，这一项接近 $0$。

---
id: arch-moe-z-loss
section: arch
order: 24
level: A
title: Router z-loss 惩罚的是什么？和 aux load-balance 为什么不是同一个旋钮？
quick: >-
  Z-loss 惩罚每个 token 上 router logits 的 log-sum-exp 平方，把分数压在不大的范围，避免 softmax/sigmoid
  溢出和「自信到只认一个专家」。Aux 惩罚的是专家之间的流量不均。一个管数值幅度，一个管负载直方图，系数要分开扫。
tags:
  - MoE
  - Router
  - Z-loss
  - ST-MoE
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-20
sources:
  - title: ST-MoE
    url: https://arxiv.org/abs/2202.08906
    type: primary
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

陷阱是把 z-loss 说成「又一种负载均衡」。面试官若追问「那和 $N\sum_i f_i P_i$ 有何不同」，答成同一件事就漏了。ST-MoE 把 **logits 幅度** 单独正则掉，因为 MoE 训练后期 router 分数容易涨到极大，softmax 变成 one-hot，FP16 下还溢出。

## 公式

对 token $t$ 的 router logits $z_t\in\mathbb{R}^{N}$：

$$
\mathcal{L}_z=\frac1T\sum_{t=1}^{T}\Bigl(\log\sum_{i=1}^{N}e^{z_{t,i}}\Bigr)^2
=\frac1T\sum_{t=1}^{T}\mathrm{LSE}(z_t)^2.
$$

$\mathrm{LSE}$ 就是 softmax 的分母的对数。它大，说明这一行 logits 整体偏大或极度尖锐。平方后对「已经很大」的 token 惩罚更重。实现用 `logsumexp`，不要先 `exp` 再 `sum` 再 `log`。系数 $\alpha_z$ 通常远小于 aux（ST-MoE 量级 $10^{-3}$ 到 $10^{-2}$ 量级，以论文为准），加在主 CE 上：

$$
\mathcal{L}=\mathcal{L}_{\mathrm{LM}}+\lambda\mathcal{L}_{\mathrm{aux}}+\alpha_z\mathcal{L}_z.
$$

Sigmoid 门控没有单一的 $N$ 类分母，但仍可对 affinity logits 做幅度惩罚，或直接惩罚 $\|z\|_2^2$。V3 的无辅助方案管的是 **谁进 Top-$k$**，不替代 z-loss 的数值动机；两条可以同时不存在——Mixtral 粗粒度时两者都不开。

## 和 aux 拆开

| | Aux / bias | Z-loss |
| --- | --- | --- |
| 看什么 | 各专家的 $f_i$、$P_i$ | 每个 token 的 $\mathrm{LSE}(z)$ |
| 想阻止 | 热点 / 死专家 | 分数爆炸、softmax 塌成 one-hot、溢出 |
| 失败样子 | 直方图歪、all-to-all 拖尾 | NaN、门控全 $0/1$、训练后半段突然不稳 |
| 调太大 | 路由为了平均牺牲语义 | 路由器不敢自信，专家区分度掉 |

Aux 在均匀负载时取最小值 $1$（Switch 形式），和 logits 幅度无关：可以把分数乘 $100$ 再减一个常数，softmax 不变，$f_i$ 也不变，aux 不动，z-loss 会爆。反向：所有专家流量已经均匀，但 logits 到了 $60$，aux 看起来健康，半精度前向已经在 overflow 边缘。所以监控要两套：专家份额 CV，以及 `router_logits.abs().max()` / `lse.mean()`。

## 实现要点

- **不要对 softmax 之后的概率做 z-loss。** 概率已经在单纯形上，LSE 信息没了。
- **和 jitter / 噪声正交。** Switch 训练时在 logits 上加噪声是为了探索冷专家；z-loss 是压幅度。同时开时先加噪声再算 LSE，或对「干净 logits」算 LSE，要在代码里写死，训推一致。
- **推理关掉。** 它只是训练正则。导出的 router 权重已经学完。

## 追问

- **为什么是平方而不是 LSE 本身？** 大 logits 时二次更狠，小 logits 时几乎不打扰早期学习。没有唯一定理，ST-MoE 的经验选择。
- **FP8 router 还要不要？** 更要。动态范围更窄，幅度不压就先量化崩，再谈均衡。
- **DeepSeek 无 aux 是否等于无 z-loss？** 不是。无 aux 只说明均衡改走 bias；幅度仍可能要管。V3 主报告没把它当卖点，面试不要编「V3 用了 z-loss」。
- **手写测什么？** 把一行 logits 设成全 $50$，z-loss 应明显大于全 $0$ 的基线；均匀小 logits 时该项接近 $0$。

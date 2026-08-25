---
id: sys-moe-capacity-token-drop
section: systems
order: 34
level: S
title: Capacity Factor 与 Token Drop 如何影响质量与吞吐？怎么选型？
quick: >-
  每个 expert 每步最多接 $\mathrm{CF}\cdot T/N$ 量级的 token（再乘 top-$k$）。CF 过大浪费显存和算力，过小则
  drop / 溢出，被丢掉的 token 等于这一层没走 MoE。我会用丢弃率、负载直方图和下游损失一起选，不会只看吞吐。
tags:
  - MoE
  - Capacity Factor
  - Token Drop
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

Router 可以让所有 token 都想进同一个 expert，但那张卡的 buffer 和 GEMM 形状必须事先定。Capacity 就是这个硬上限。

## 公式

$T$ 个 token、$N$ 个 expert、top-$k$ 时，均匀负载下每个 expert 期望 $kT/N$ 个 token。Capacity 写成

$$
C=\mathrm{CF}\cdot\frac{kT}{N}.
$$

$\mathrm{CF}=1$ 是「刚好均匀」；$\mathrm{CF}=1.25$ 留 25% 余量给抖动。超出的 token 可以 **drop**（这一层退回 residual / 跳过 expert）、重路由到次优 expert，或进溢出 buffer。Drop 的 token 对这一层 MoE 没有专家计算，等价于局部变成 dense skip。

## 质量和吞吐

- **CF 大**：drop $\approx 0$，质量接近「路由想去哪就去哪」，但每卡要按最坏容量分配 activation，显存和 padding 变多，all-to-all 也按上限备缓冲。
- **CF 小**：吞吐好看、形状更紧，热点 expert 开始丢 token。训练 drop 率应接近 0；验证集 PPL 对 drop 很敏感。推理可以更激进，但要有质量门禁，不能把「吞吐涨了」当成成功。

Aux loss / expert bias 把负载推均匀，才能把 CF 降下来。均衡没做好就硬降 CF，只是把质量问题从「热点排队」换成「静默丢 token」。

## 选型

我先盯 **dropped token rate**（按层、按 expert），目标训练期 $\lt 1\%$。再看 expert 频率的 CV、以及 drop 开关对 held-out loss 的敏感性。推理单独设 CF，并在金标集上回归。

## 追问

- **Drop 的梯度？** 被丢的 token 通常不经过该 expert，路由器可能仍收到「你选了过载专家」的信号，取决于实现是否对 overflow 反传。
- **和 EP 的关系？** Capacity 是每个 expert 副本上的本地上限；EP 把 expert 拆到多卡，不自动提高 $C$。热点仍会在持有该 expert 的卡上打满。
- **面试别说成「drop 等于 dropout」。** Dropout 是正则；token drop 是容量溢出，分布随负载变，不是固定噪声。

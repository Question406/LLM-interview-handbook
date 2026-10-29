---
id: sys-moe-capacity-token-drop
section: systems
order: 34
level: S
title: Capacity Factor 与 Token Drop 如何影响质量与 throughput？怎么选型？
quick: >-
  Capacity Factor 决定每个 expert 每步能接多少 token，容量约为 $\mathrm{CF}\cdot T/N$ 再乘
  top-$k$。CF 大时少丢 token，但缓冲和 padding 更贵；CF 小时热点专家会溢出，被 drop 的 token
  这一层跳过专家计算。选择时要一起看丢弃率、负载直方图和下游损失。
tags:
  - MoE
  - Capacity Factor
  - Token Drop
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Switch Transformers
    url: 'https://arxiv.org/abs/2101.03961'
    type: primary
---

Capacity Factor 是给每个 expert 留多少容量余量的系数，决定质量和 throughput 怎样取舍。比如 router 把很多 token 都送给同一个专家，这张卡的 buffer 和 GEMM 形状有上限，超出的 token 只能丢弃、重路由或暂存；CF 越小，热点专家越容易先碰到这个上限。

## 从平均负载算容量

$T$ 个 token、$N$ 个 expert、top-$k$ 时，均匀负载下每个 expert 期望 $kT/N$ 个 token。Capacity 写成

$$
C=\mathrm{CF}\cdot\frac{kT}{N}.
$$

$\mathrm{CF}=1$ 是「刚好均匀」；$\mathrm{CF}=1.25$ 留 25% 余量给抖动。超出的 token 可以 **drop**（这一层退回 residual / 跳过 expert）、重路由到次优 expert，或进溢出 buffer。Drop 的 token 对这一层 MoE 没有专家计算，等价于局部变成 dense skip。

容量如何影响质量和 throughput，可以从两个方向看。

- **CF 大**：drop $\approx 0$，质量接近「路由想去哪就去哪」，但每卡要按最坏容量分配 activation，显存和 padding 变多，all-to-all 也按上限备缓冲。
- **CF 小**：throughput 好看、形状更紧，热点 expert 开始丢 token。训练 drop 率应接近 0；验证集 PPL 对 drop 很敏感。推理可以更激进，但要有质量检查，不能把「throughput 涨了」当成成功。

辅助损失（Aux loss）或 expert bias 让专家之间的负载更均匀，才能把 CF 降下来。如果负载还不均匀就降低 CF，热门专家会从排队变成直接丢弃 token，质量问题仍然存在。

实际选择时，我会先看质量再看节省了多少资源。

我先按层、按 expert 看 dropped token rate，目标训练期 $\lt 1\%$，再看 expert 频率的 CV，判断负载是否集中。然后对比开启和关闭 drop 时的 held-out loss，确认省下的资源有没有损害质量。推理单独设 CF，在金标集上做回归。

## 追问

**Drop 的梯度？**
被丢的 token 通常不经过该 expert，路由器可能仍收到「你选了过载专家」的信号，取决于实现是否对 overflow backpropagation。
**和 EP 的关系？**
Capacity 是每个 expert 副本上的本地上限；EP 把 expert 拆到多卡，不自动提高 $C$。热点仍会在持有该 expert 的卡上打满。
- 面试别把 token drop 说成 dropout。Dropout 是正则；token drop 是容量溢出，分布随负载变，不是固定噪声。

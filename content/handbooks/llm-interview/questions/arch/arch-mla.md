---
id: arch-mla
section: arch
order: 10
level: S
title: MLA 主要解决什么？和 GQA 有什么本质差别？
quick: "MLA 解决的是 decode 时 KV Cache 的存储和带宽：它把每个 token 的 K/V 压进低维 latent，再把 RoPE 拆成一小段单独存，推理时靠矩阵吸收直接在 latent 上算。GQA 是让多个查询头共享较少的 KV 头。两者都省 KV，一个压表示维，一个压头数。"
tags:
  - MLA
  - DeepSeek
  - KV Cache
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ DeepSeek-V3
    url: 'https://arxiv.org/abs/2412.19437'
    type: legacy-reference
---

MLA 和 GQA 都是为逐 token 生成（decode）时的 KV 带宽服务的，差别在压缩的轴不同：GQA 减少独立 KV 头的个数；MLA 把每个 token 的 K/V 内容压进一个低维 latent，再配合 RoPE 拆分和矩阵吸收，让推理时不必还原出完整的头向量。

所以 MLA 不能说成「另一种 GQA」，也不能说成「把 K/V 随便压成一个小向量」。拿 $n_h=32,d_h=128$ 来算，MHA 每个 token 要存约 $8\mathrm{k}$ 维，MLA 的 $512+64$ 是另一个量级。

## GQA：沿头数共享

MHA 给每个 query head 存一对 $k,v$，每个 token 的 cache 约为 $2 n_h d_h$。GQA 令 $n_{\mathrm{kv}}\lt n_h$，几个 query 头共用同一个 KV 头；MQA 是 $n_{\mathrm{kv}}=1$ 的极端情况。

Cache 因此从 $O(n_h d_h)$ 降到 $O(n_{\mathrm{kv}} d_h)$。实现简单，和标准 RoPE 兼容，旋转照样作用在完整的头维上。代价是头之间的独立性变弱，压过头（直接用 MQA）质量往往掉一截。GQA 没有在头内部做低秩分解，只是少存了几份头。

## MLA：沿表示维压缩，再把 RoPE 拆出来

DeepSeek 的 Multi-head Latent Attention 先把隐状态投到低维：

$$
c_t^{KV}=W^{DKV}h_t\in\mathbb{R}^{d_c},\qquad d_c\ll n_h d_h.
$$

训练时再上投影得到内容部分 $k^C,v^C$。如果对整段 $k$ 做低秩、又直接套 RoPE，旋转和低秩基对不齐，位置旋转会挡住后面的矩阵吸收。所以 MLA 把 RoPE 拆了出去：另存一小段解耦的 $k_t^R=\mathrm{RoPE}(W^{KR}h_t)$，维度 $d_h^R$ 往往只有几十，query 侧也有对应的 $q^R$。Cache 里每个 token 主要就是 $c_t^{KV}$ 加这一小段 $k^R$，用不着存 $n_h$ 份全长 K/V。

压缩也有限度，attention score 和 value 聚合仍要保留足够的 query-dependent 结构。$d_c$ 太小就成了信息瓶颈，论文里的 $d_c$（如 $512$）是质量和流量的折中，越小越好并不成立。

量级上，MHA 每个 token 存 $2 n_h d_h$；GQA-8 大约是它除以 $n_h/8$；MLA 是 $d_c+d_h^R$（是否再乘 K 或 K+V 看实现细节）。面试报数量级就行，不必背某一版的超参。

## Absorption：推理时不用先解压回全长 K/V

内容路径上 $q^C=W^{UQ}c^Q$，$k^C=W^{UK}c^{KV}$，点积是

$$
(q^C)^\top k^C=(c^Q)^\top(W^{UQ})^\top W^{UK}c^{KV}.
$$

把 $(W^{UQ})^\top W^{UK}$ 吸进 query 侧，推理时直接拿 $c^{KV}$ 做等价的点积；value 侧则把 $W^{UV}$ 吸进输出投影。这样 decode 每步不用显式恢复大的 $k,v$，计算和读取都围绕低维潜在表示进行。和「先低秩压缩、用的时候解压再 attention」相比，这是 MLA 最关键的工程差别。

| | GQA | MLA |
| --- | --- | --- |
| 压缩轴 | 头个数 $n_{\mathrm{kv}}\downarrow$ | 表示维 $d_c\downarrow$ + 短 RoPE |
| RoPE | 直接转头向量 | 必须拆开，避免破坏低秩 |
| 推理技巧 | 共享 KV 头 | 矩阵吸收，不物化全长 K/V |
| 与对方组合 | 不同轴，可设计组合，但不能当两个开关乱开 | 同左 |

## 追问

**MLA 和 low-rank KV compression 是一回事吗？**
思路相通，都假设 K/V 落在低维结构上。区别是 MLA 把 latent 写进了注意力的参数化，并用吸收保证推理计算和训练目标一致；训练后再套一层量化或 SVD，就和梯度脱节了。

**GQA 和 MLA 能同时用吗？**
概念上能组合，一个切头数，一个切表示。但 head、latent、RoPE 的维度都要重新定义，没法当成两个 flag 随手打开。

**吸收之后，训练和推理还是同一个函数吗？**
是。线性吸收在数学上等价，实现上要对齐精度和融合 kernel。面试时强调这是等价重排，没有引入另一套近似。

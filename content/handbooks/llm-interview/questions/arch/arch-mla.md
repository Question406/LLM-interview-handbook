---
id: arch-mla
section: arch
order: 10
level: S
title: MLA 主要解决什么？和 GQA 有什么本质差别？
quick: "MLA 把 K/V 相关信息压缩到低维潜在表示中，减少 KV Cache；GQA 则让多个查询头共享较少的 KV 头。两者都降低逐 token 生成（decode）时的存储和带宽开销，但压缩的是不同维度。"
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

常见误区是：把 MLA 说成「另一种 GQA」，或「把 K/V 随便压成一个小向量」。两者都为 逐 token 生成（decode） 的 KV 带宽服务，压缩轴不同：GQA 减少独立 KV 头的个数；MLA 把每个 token 的 K/V 内容压进低维 latent，再用 RoPE 拆分和矩阵吸收，让推理不必还原完整头向量。

## 1. GQA：沿 head 数共享

MHA 对每个 query head 存一对 $k,v$，每 token cache 约为 $2 n_h d_h$。GQA 令 $n_{\mathrm{kv}}\lt n_h$，若干 query 头共用同一 KV 头。MQA 是 $n_{\mathrm{kv}}=1$ 的极端。

Cache 从 $O(n_h d_h)$ 降到 $O(n_{\mathrm{kv}} d_h)$。实现简单，和标准 RoPE 兼容：旋转仍作用在完整头维上。代价是头之间的独立性变弱；压过头（直接 MQA）质量往往掉一截。GQA 没有在头内部做低秩分解，只是少存几份头。

## 2. MLA：沿表示维压缩，再拆 RoPE

DeepSeek 的 Multi-head Latent Attention 把隐状态投到低维

$$
c_t^{KV}=W^{DKV}h_t\in\mathbb{R}^{d_c},\qquad d_c\ll n_h d_h.
$$

训练时再上投影得到内容部分 $k^C,v^C$。若对整段 $k$ 做低秩又直接套 RoPE，旋转与低秩基不对齐，位置旋转会妨碍直接进行矩阵吸收。MLA 因此把 RoPE 拆出去：另存一小段解耦的 $k_t^R=\mathrm{RoPE}(W^{KR}h_t)$（维 $d_h^R$ 往往只有几十），query 侧同样有 $q^R$。Cache 里每 token 主要是 $c_t^{KV}$ 加这段短 $k^R$，而不是 $n_h$ 份全长 K/V。

不能「随便压成一个小向量」：attention score 与 value 聚合仍要保留足够的 query-dependent 结构。$d_c$ 太小就是信息瓶颈；论文里的 $d_c$（如 $512$）是质量和流量的折中，不是越小越好。

量级对照：MHA 每 token 存 $2 n_h d_h$；GQA-8 大约除以 $n_h/8$；MLA 则是 $d_c+d_h^R$（再乘 K 或 K+V 的实现细节）。$n_h=32,d_h=128$ 时 MHA 约 $8\mathrm{k}$ 维，MLA 的 $512+64$ 是另一量级。面试报数量级即可，不必背某一版超参。

## 3. Absorption：推理时不要先 decode 回全长 K/V

内容路径上 $q^C=W^{UQ}c^Q$，$k^C=W^{UK}c^{KV}$，点积

$$
(q^C)^\top k^C=(c^Q)^\top(W^{UQ})^\top W^{UK}c^{KV}.
$$

把 $(W^{UQ})^\top W^{UK}$ 吸进 query 侧，推理只需拿 $c^{KV}$ 做等价点积。Value 侧把 $W^{UV}$ 吸进输出投影。于是 decode 不必每步显式恢复大 $k,v$，计算和读取可以围绕低维潜在表示进行。这是 MLA 相对「先低秩压缩、再解压再 attention」的关键工程差。

| | GQA | MLA |
| --- | --- | --- |
| 压缩轴 | 头个数 $n_{\mathrm{kv}}\downarrow$ | 表示维 $d_c\downarrow$ + 短 RoPE |
| RoPE | 直接转头向量 | 必须拆开，避免破坏低秩 |
| 推理技巧 | 共享 KV 头 | 矩阵吸收，不物化全长 K/V |
| 与对方组合 | 不同轴，可设计组合，但不能当两个开关乱开 | 同左 |

## 追问

- **MLA 与 low-rank KV compression 是一回事吗？** 都利用 K/V 可能落在低维结构上。MLA 把 latent 写进注意力参数化，并用吸收保证推理计算与训练目标一致，而不是训练后再套一层与梯度脱节的量化 / SVD。
- **GQA 和 MLA 可以同时有吗？** 概念上一个切头数、一个切表示，能组合，但 head、latent、RoPE 维必须重新定义，不是两个 flag。
- **吸收后训练和推理是否同一函数？** 线性吸收在数学上等价；实现要对齐精度与融合 kernel。面试强调「等价重排，不是另一套近似」。

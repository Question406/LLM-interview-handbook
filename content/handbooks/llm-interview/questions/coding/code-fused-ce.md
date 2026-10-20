---
id: code-fused-ce
section: coding
order: 58
level: S
title: 手写融合 Linear + Cross Entropy：不要物化 $[N,V]$ logits
quick: "$\\ell_i=-h_i^\\top W_{y_i}+\\mathrm{logsumexp}_v(h_i^\\top W_v)$：第一项只 gather 一行，第二项把词表分块做 GEMM 并维护 online logsumexp，显存从 $O(NV)$ 降到 $O(N\\cdot\\mathrm{chunk})$。"
tags:
  - CrossEntropy
  - Fusion
  - Memory
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Efficient Cross-Entropy (Megatron / Apex style)
    url: https://github.com/NVIDIA/apex/tree/master/apex/contrib/xentropy
    type: primary
---

$V=128\mathrm{k}$、$N=B T=8\mathrm{k}$、$d=4096$ 时，logits 是 $NV$ 个 fp32，几个 GB。融合之后只保留 hidden 和一小段词表。常见误区是：`logits = h @ W.T` 再 `cross_entropy`，形状对了但过不了显存追问。

## 分块 logsumexp

$$
m\leftarrow\max(m,\;\mathrm{rowmax}(z_{\mathrm{blk}})),\quad
s\leftarrow s\,e^{m_{\mathrm{old}}-m}+\sum e^{z_{\mathrm{blk}}-m}.
$$

最后 $\mathrm{lse}=m+\log s$。$nll=-h\cdot W_y+\mathrm{lse}$。

```python
import torch

def fused_linear_ce(h, weight, target, chunk=128):
    # h: [N,D], weight: [V,D], target: [N]
    nll = -(h * weight[target]).sum(-1)
    m = h.new_full((h.size(0),), -float("inf"))
    s = h.new_zeros(h.size(0))
    for v0 in range(0, weight.size(0), chunk):
        z = h @ weight[v0:v0 + chunk].T          # [N, chunk]
        bm = z.amax(-1)
        nm = torch.maximum(m, bm)
        s = s * (m - nm).exp() + (z - nm[:, None]).exp().sum(-1)
        m = nm
    return nll + m + s.log()
```

`chunk` 取 1024 / 4096 看显存。和 FlashAttention 的 online softmax 是同一递推，只是 reduction 维从 $S$ 换成 $V$。`ignore_index`：那几行的 $nll$ 乘 0，计算 mean 时只除以有效 token 数。

## 追问

- **和 `F.cross_entropy` 对得上吗？** 必须对上，这是默写完的检查。chunk 大小只影响显存，不影响值。
- **TP 下词表切分？** 每张卡一块 $V/P$，本地 lse 再 all-gather 做一次 logsumexp。手写单卡即可。
- **label smoothing？** 目标不再是单点，$nll$ 变成对所有 $v$ 的加权和，融合还是能做，公式更长。

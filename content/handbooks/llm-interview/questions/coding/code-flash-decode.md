---
id: code-flash-decode
section: coding
order: 52
level: S
title: 手写 FlashDecoding 的 split-K：各片本地 softmax，再用 lse 合并
quick: "decode 时只有 1 个 query，把长 KV 沿 $S$ 切片，各片算本地 softmax 输出 $O_g$ 和 $\\mathrm{lse}_g$。合并时按 $e^{\\mathrm{lse}_g}$ 加权（先减最大 lse），不能直接平均。"
tags:
  - FlashDecoding
  - Online Softmax
  - Decode
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Flash-Decoding for long-context inference
    url: https://crfm.stanford.edu/2023/10/12/flashdecoding.html
    type: primary
---

普通 decode 每步用 $q$ 与整段 cache 计算注意力，见 `code-kv-cache-step`。$S$ 很大时单个 query 吃不满 GPU，$S$ 维没有并行。FlashDecoding 把 KV 切开，多 CTA 各算一片再归约。训练用的 tiled FA 见 `code-flash-attn-fwd`，本题只写 decode 的合并。

## 两片合并

片 $g$ 已经得到归一化输出 $O_g$ 和 $\mathrm{lse}_g=\log\sum_j e^{s_{gj}}$。

$$
m=\max(\mathrm{lse}_1,\mathrm{lse}_2),\quad
O=\frac{O_1 e^{\mathrm{lse}_1-m}+O_2 e^{\mathrm{lse}_2-m}}{e^{\mathrm{lse}_1-m}+e^{\mathrm{lse}_2-m}}.
$$

$$
\mathrm{lse}\leftarrow m+\log\big(e^{\mathrm{lse}_1-m}+e^{\mathrm{lse}_2-m}\big).
$$

多片从左到右 fold 即可。不要把各片 $O_g$ 直接平均，权重必须是 $e^{\mathrm{lse}_g}$。

```python
import math
import torch

def softmax_stable(x, dim=-1):
    z = x.float() - x.float().amax(dim=dim, keepdim=True)
    p = torch.exp(z)
    return (p / p.sum(dim=dim, keepdim=True)).to(x.dtype)

def online_merge(o1, lse1, o2, lse2):
    m = torch.maximum(lse1, lse2)
    a1, a2 = (lse1 - m).exp(), (lse2 - m).exp()
    o = (o1 * a1.unsqueeze(-1) + o2 * a2.unsqueeze(-1)) / (a1 + a2).unsqueeze(-1)
    return o, m + (a1 + a2).log()

def splitk_attn(q, k, v, n_split):
    # q: [B,H,1,D]；沿 S 切开
    S, scale = k.size(2), 1.0 / math.sqrt(q.size(-1))
    width = (S + n_split - 1) // n_split
    o = lse = None
    for i in range(n_split):
        sl = slice(i * width, min((i + 1) * width, S))
        if sl.start >= S:
            break
        scores = (q @ k[:, :, sl].transpose(-1, -2)) * scale
        block_lse = torch.logsumexp(scores.float(), dim=-1)
        block_o = softmax_stable(scores, dim=-1) @ v[:, :, sl]
        o, lse = (block_o, block_lse) if o is None else online_merge(o, lse, block_o, block_lse)
    return o
```

$G$ 片的结果必须和一次打完整 $S$ 一致，这是默写完之后的自检。空片（$S$ 不能整除）直接跳过。

## 追问

- **为什么 decode 才需要 split-K？** prefill 处理整段输入时，$T$ 足够大，切 $Q$ 行就已经吃满 SM。decode $T=1$，只能切 $S$。
- **lse 为什么保留？** backward 和跨片合并都要用。只存 $O$ 合并不了。
- **和 paged KV？** 每个 physical block 就是一片，gather 后再 merge。手写用连续 slice 即可。

---
id: code-kv-cache-step
section: coding
order: 15
level: A
title: 手写一步 decode：用 KV cache 算当前 token 的 attention
quick: >-
  Prefill 把整段 $K,V$ 写入 cache。Decode 只算当前 token 的 $q_t,k_t,v_t$，把 $k_t,v_t$
  concat 到 cache，再 $q_t$ 对全部过去 key 做点积。复杂度从 $O(t^2 d)$ 的完整自注意力变成 $O(t d)$ 的一步。
tags:
  - KV Cache
  - Decode
  - Attention
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: GQA
    url: https://arxiv.org/abs/2305.13245
    type: primary
---

`arch-kv-cache` 讲显存公式；本题要能写出 **一步** 的张量变化。面试官常画：「已经有 $t-1$ 个 token 的 cache，来了第 $t$ 个」。

## 形状

设 $B$ batch、$H$ head、$S$ 已缓存长度、$D$ head dim：

- cache_k / cache_v：`[B, H, S, D]`
- 当前 hidden：`[B, 1, d_model]` → $q,k,v$ 各 `[B, H, 1, D]`

一步：

$$
K\leftarrow [K;k_t],\quad V\leftarrow [V;v_t],\quad
\mathrm{Attn}(q_t,K,V)=\mathrm{softmax}\Big(\frac{q_t K^\top}{\sqrt{D}}\Big)V.
$$

$q_t K^\top$ 的形状是 `[B, H, 1, S+1]`。不要再对过去 token 算 $Q$。Causal mask 在 decode 一步里通常不需要：当前 query 只看 $\le t$ 的 key，而 cache 里本来就是过去。

Prefill：一次算完整 $Q,K,V$，写满 cache，复杂度 $O(S^2)$。之后每步 $O(S)$。

```python
import torch
import torch.nn.functional as F

def decode_step(q, k, v, cache_k, cache_v):
    # q,k,v: [B, H, 1, D]
    cache_k = torch.cat([cache_k, k], dim=2)
    cache_v = torch.cat([cache_v, v], dim=2)
    att = (q @ cache_k.transpose(-2, -1)) / (q.shape[-1] ** 0.5)
    out = F.softmax(att, dim=-1) @ cache_v
    return out, cache_k, cache_v
```

## 追问

- **显存？** 每层每 token 存 $K,V$：$2\cdot L\cdot H\cdot D\cdot \mathrm{bytes}$（再乘 batch）。GQA 把 $H$ 换成 $H_{\mathrm{kv}}$。
- **PagedAttention？** 物理上 cache 不连续 concat，逻辑仍是「当前 $q$ 打全部过去 $k$」。手写用 `cat` 即可。
- **多 query 的 prefill chunk？** 那是 chunked prefill，要对新 chunk 内部做因果，并对 cache 做 cross-attn；不要和纯 decode 一步混。

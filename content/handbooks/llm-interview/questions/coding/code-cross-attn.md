---
id: code-cross-attn
section: coding
order: 53
level: A
title: 手写 Cross-Attention：decoder $Q$ 打 encoder 的 $K,V$，cache 缓的是 encoder
quick: "$Q$ 来自 decoder，$K,V$ 来自 encoder，scores 形状为 $[B,H,T_q,T_k]$。这层不加因果 mask，只 mask encoder padding；encoder 的 $K,V$ 算一次就缓存，decode 全程不变。"
tags:
  - CrossAttention
  - EncoderDecoder
  - KV Cache
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

和自注意力的差别：K/V 的长度、来源都不是当前序列。decoder 自注意力仍要因果，见 `code-attention`；cross-attn 这一层不用上三角因果掩码。

## 形状

- encoder 一次：$X_{\mathrm{enc}}\to K,V$，缓存 `[B, H, Tk, Dh]`
- decoder 每步：$X_{\mathrm{dec}}\to Q$ `[B, H, Tq, Dh]`（输入预填充（prefill，即处理输入并建立缓存） $T_q$ 是目标长度，逐 token 生成（decode） $T_q=1$）
- $QK^\top$：`[B, H, Tq, Tk]`

$$
\mathrm{Cross}(Q,K,V)=\mathrm{softmax}\Big(\frac{QK^\top}{\sqrt{d_h}}+\mathrm{mask}_{\mathrm{enc}}\Big)V.
$$

```python
import math
import torch

def softmax_stable(x, dim=-1):
    z = x.float() - x.float().amax(dim=dim, keepdim=True)
    p = torch.exp(z)
    return (p / p.sum(dim=dim, keepdim=True)).nan_to_num(0.0).to(x.dtype)

def cross_attn(q, k, v, key_valid=None):
    # q: [B,H,Tq,D]；k,v: [B,H,Tk,D]；key_valid: [B,Tk], True=有效 encoder token
    scores = q @ k.transpose(-1, -2) / math.sqrt(q.size(-1))
    if key_valid is not None:
        scores = scores.masked_fill(~key_valid[:, None, None, :], float("-inf"))
    return softmax_stable(scores, dim=-1) @ v
```

encoder padding 在左边还是右边都靠 `key_valid`。GQA 时 encoder 侧 $H_{\mathrm{kv}}$ 可以更少，`repeat_kv` 后再打，见 `code-gqa`。多模态：vision encoder 输出的 token 数就是 $T_k$，decode 图像那侧 cache 全程不变。

## 追问

- **encoder 要 RoPE 吗？** 自注意力那层要。cross-attn 的 $Q$ 用 decoder 位置，$K$ 用 encoder 位置，两边的 position 空间不同，有的实现 cross 不加 RoPE。
- **cache 随 decode 变吗？** encoder KV 不变。变的是 decoder 自注意力的 cache。
- **和 prefix LM？** prefix LM 是同一条序列前半双向、后半因果，mask 不同，不是两条序列。

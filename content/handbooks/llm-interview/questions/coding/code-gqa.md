---
id: code-gqa
section: coding
order: 16
level: A
title: 手写 GQA：`repeat_kv` 让多组 Q head 共享 KV
quick: >-
  $Q$ 有 $H_q$ 个头，$K,V$ 只有 $H_{\mathrm{kv}}$ 头，且 $H_q=g\cdot H_{\mathrm{kv}}$。每个 KV
  head 重复 $g$ 次（或按组索引）对齐后再做标准 attention。显存和 KV cache 按 $H_{\mathrm{kv}}$ 计，不是 $H_q$。
tags:
  - GQA
  - Attention
  - KV Cache
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: GQA
    url: https://arxiv.org/abs/2305.13245
    type: primary
---

MHA：$H_q=H_{\mathrm{kv}}$。MQA：$H_{\mathrm{kv}}=1$。GQA 取中间：若干 Q head 共享一个 KV head，质量接近 MHA，cache 接近 MQA。

## 对齐方式

$g=H_q/H_{\mathrm{kv}}$ 必须整除。`repeat_kv` 把 `[B, H_kv, S, D]` 沿 head 维每个头复制 $g$ 次，得到 `[B, H_q, S, D]`，然后当普通 MHA：

$$
\mathrm{Attn}(Q,\;\mathrm{repeat}(K),\;\mathrm{repeat}(V)).
$$

等价实现是 `einsum` / gather：第 $i$ 个 Q head 用第 $\lfloor i/g\rfloor$ 个 KV head，避免真的把显存放大 $g$ 倍。手写面试复制即可，但要说生产实现按组索引，不物理 repeat。

```python
import torch
import torch.nn.functional as F

def repeat_kv(x, n_rep):
    # x: [B, H_kv, S, D]
    if n_rep == 1:
        return x
    b, h, s, d = x.shape
    return (
        x[:, :, None, :, :]
        .expand(b, h, n_rep, s, d)
        .reshape(b, h * n_rep, s, d)
    )

def gqa_attn(q, k, v):
    # q: [B, H_q, S, D], k,v: [B, H_kv, S, D]
    n_rep = q.shape[1] // k.shape[1]
    k, v = repeat_kv(k, n_rep), repeat_kv(v, n_rep)
    att = (q @ k.transpose(-2, -1)) / (q.shape[-1] ** 0.5)
    return F.softmax(att, dim=-1) @ v
```

Decode 一步：只 repeat 当前和新 concat 后的 cache KV，Q 仍是 $H_q$ 个。

## 追问

- **Cache 公式？** 把 `arch-kv-cache` 里的 $n_{\mathrm{heads}}$ 换成 $n_{\mathrm{kv}}$。
- **$H_q$ 不能整除 $H_{\mathrm{kv}}$？** 非法配置；Llama-3 8B 是 32 Q / 8 KV。
- **和 MLA？** MLA 压的是 KV 的低秩潜变量，不是简单 repeat；GQA 不是 DeepSeek MLA。

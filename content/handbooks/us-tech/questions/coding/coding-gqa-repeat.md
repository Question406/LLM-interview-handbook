---
id: coding-gqa-repeat
section: coding
order: 16
level: A
title: 白板：GQA 把 KV head repeat 成 query heads，shape 怎么断言
quick: >-
  $H_q$ 整除 $H_{\mathrm{kv}}$，$n_{\mathrm{rep}}=H_q/H_{\mathrm{kv}}$。Cache 里 $K,V$ 仍是
  `[B, H_kv, S, D]`，算分数前 `repeat_interleave` 成 `[B, H_q, S, D]`。`repeat` 沿 head
  轴会打乱分组。不要把 cache 存成 $H_q$ 份。
tags:
  - Coding
  - GQA
  - Llama
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: GQA — Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
    url: https://arxiv.org/abs/2305.13245
    type: primary
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
---

## 题怎么来的

Llama 2 70B 公开配置是 $64$ 个 query head、$8$ 个 KV head、头维 $128$（$8192/64$）。Meta 白板会让你把 `repeat_kv` 写出来，并说清 cache 存几组、算的时候 repeat 几次。选型见 `meta-llama-gqa`、`google-gqa-mqa`。MQA 是 $H_{\mathrm{kv}}=1$ 的端点，实现见 `coding-mq-attn`。shape assert 要写上，别口头「广播一下」。

## 分组和 repeat 的轴

$Q$ 是 `[B, H_q, T, D]`，$K,V$ 是 `[B, H_kv, S, D]`。不变量：

$$
H_q \bmod H_{\mathrm{kv}}=0,\quad n_{\mathrm{rep}}=H_q/H_{\mathrm{kv}}.
$$

70B：$n_{\mathrm{rep}}=8$，每组 $8$ 个 query head 共享一组 $K,V$。Repeat 发生在算 $QK^\top$ 之前，cache 仍写 $8$ 组。把 cache 存成 $64$ 组，等于把 GQA 的带宽又吐回去。

正确的 head 排布是「相邻 $n_{\mathrm{rep}}$ 个 $Q$ head 共用同一个 KV head」：

$$
\text{kv index}=\lfloor h_q / n_{\mathrm{rep}}\rfloor.
$$

`unsqueeze` + `expand` + `reshape`，或 `repeat_interleave` 沿 head 维，都是这个顺序。`tensor.repeat(1, n_rep, 1, 1)` 会变成整段 KV 头列表复制，分组对不上训练时的投影。

```python
import torch

def repeat_kv(x, n_rep):
    # x: [B, H_kv, S, D] -> [B, H_q, S, D]
    if n_rep == 1:
        return x
    b, h, s, d = x.shape
    return (
        x[:, :, None, :, :]
        .expand(b, h, n_rep, s, d)
        .reshape(b, h * n_rep, s, d)
    )

def gqa_attn(q, k, v):
    # q: [B, H_q, T, D]; k,v: [B, H_kv, S, D]
    b, hq, t, d = q.shape
    hk = k.shape[1]
    assert k.shape == v.shape
    assert k.shape[0] == b and k.shape[-1] == d
    assert hq % hk == 0, (hq, hk)
    n_rep = hq // hk
    k_r, v_r = repeat_kv(k, n_rep), repeat_kv(v, n_rep)
    assert k_r.shape[:2] == (b, hq)
    scale = d ** -0.5
    scores = torch.matmul(q, k_r.transpose(-2, -1)) * scale
    p = torch.softmax(scores.float(), dim=-1).to(q.dtype)
    return torch.matmul(p, v_r)
```

$H_q=H_{\mathrm{kv}}$ 时 $n_{\mathrm{rep}}=1$，函数直接返回，这就是 MHA。不要为了对称硬 repeat。

## 投影层的 shape

$W_Q$ 出 `H_q * D`，$W_K,W_V$ 出 `H_kv * D`。`view` 成 `[B, T, H, D]` 再 `transpose` 成 `[B, H, T, D]` 时，$H$ 分别是 $H_q$ 和 $H_{\mathrm{kv}}$，两套不能共用一个 `n_heads`。RoPE 按头维转，和 $H_{\mathrm{kv}}$ 无关，见 `coding-rope`。GQA kernel（不物化 repeat）和显式 repeat 数值应当一致；白板先写显式，再提 fused 路径 cache 仍是 $H_{\mathrm{kv}}$。

## 追问

- **`repeat` 和 `repeat_interleave` 差在哪？** 后者（以及 expand+reshape）是 `[k0,k0,...,k1,k1,...]`；`repeat` 沿 head 是 `[k0,k1,...,k0,k1,...]`。和 $W_Q$ 的分组对不上就是 silent 错。
- **decode 每步都要 repeat 吗？** 当前 $K_t,V_t$ 仍按 $H_{\mathrm{kv}}$ 写入 cache。算注意力时对已缓存的 $K,V$ repeat，或走 GQA kernel 在寄存器里广播。
- **能 $H_q$ 不整除 $H_{\mathrm{kv}}$ 吗？** 标准 GQA 不行。面试直接 assert。
- **和 MQA 比？** $H_{\mathrm{kv}}=1$、$n_{\mathrm{rep}}=H_q$，见 `coding-mq-attn`。70B 不用 MQA 是质量，不是实现写不出。

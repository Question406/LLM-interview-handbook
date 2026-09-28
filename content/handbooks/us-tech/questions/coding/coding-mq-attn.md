---
id: coding-mq-attn
section: coding
order: 22
level: A
title: 白板：MQA 单 KV head，怎么对 query heads broadcast
quick: >-
  $K,V$ 只有 $H_{\mathrm{kv}}=1$，形状 `[B, 1, S, D]` 或 `[B, S, D]`。$Q$ 仍是 `[B, H, T, D]`。
  分数 `matmul` 让 $K$ 沿 head 广播，不要先 repeat 成 $H$ 再写入 cache。Cache 按 $1$ 组算。
tags:
  - Coding
  - MQA
  - Attention
  - Google
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Fast Transformer Decoding — One Write-Head is All You Need
    url: https://arxiv.org/abs/1911.02150
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
    url: https://arxiv.org/abs/2305.13245
    type: primary
---

## 题怎么来的

Shazeer 2019 的 Multi-Query Attention：很多 query head，一组 $K,V$。Google 推理岗和 Apple 端侧都会问，因为 decode 带宽跟 $H_{\mathrm{kv}}$ 走，MQA 把 cache 降到 MHA 的 $1/H$。和 GQA 的谱系见 `google-gqa-mqa`。白板写 broadcast，别把 MQA 讲成「少几个 head 的 MHA」。GQA 的 repeat 实现见 `coding-gqa-repeat`。

## 形状：一头 KV，多头 Q

$Q$：`[B, H, T, D]`。$K,V$：`[B, 1, S, D]`（或省掉 head 维 `[B, S, D]`，matmul 前 `unsqueeze(1)`）。

$$
S_{\mathrm{scores}}[b,h,t,s]=\frac{Q[b,h,t,:]\cdot K[b,0,s,:]}{\sqrt{D}}.
$$

$K$ 没有 $h$ 下标，所有 query head 点同一组 key。softmax 仍沿 $s$（key 长）。再和同一组 $V$ 乘：`[B, H, T, S] @ [B, 1, S, D] -> [B, H, T, D]`。广播发生在计算，cache 只存 `[B, 1, S, D]`。`repeat` 成 `[B, H, S, D]` 再缓存，MQA 的省显存就没了。

$W_Q$ 出 `H * D`，$W_K,W_V$ 出 `D`（再 view 成一个 head）。RoPE 对这一个 KV head 转一次，对 $H$ 个 $Q$ 各转；不要给 $K$ 伪造 $H$ 套角度。

```python
import torch

def mqa(q, k, v, attn_bias=None):
    # q: [B, H, T, D]; k,v: [B, 1, S, D] 或 [B, S, D]
    if k.dim() == 3:
        k, v = k.unsqueeze(1), v.unsqueeze(1)
    assert k.shape[1] == 1 and v.shape[1] == 1
    assert q.shape[0] == k.shape[0] and q.shape[-1] == k.shape[-1]
    scale = q.size(-1) ** -0.5
    attn = torch.matmul(q, k.transpose(-2, -1)) * scale  # [B, H, T, S]
    if attn_bias is not None:
        attn = attn + attn_bias
    p = torch.softmax(attn.float(), dim=-1).to(q.dtype)
    return torch.matmul(p, v)

def mqa_projections(x, wq, wk, wv, n_heads):
    # x: [B, T, D]; wk,wv: [D, D]
    b, t, d = x.shape
    assert d % n_heads == 0
    dh = d // n_heads
    q = (x @ wq).view(b, t, n_heads, dh).transpose(1, 2)
    k = (x @ wk).view(b, t, 1, dh).transpose(1, 2)
    v = (x @ wv).view(b, t, 1, dh).transpose(1, 2)
    return q, k, v
```

`einsum('bhtd,bsd->bhts', q, k.squeeze(1))` 等价。不要 `expand` 出 $H$ 份再 `contiguous`，那会真的分配 cache 大小的内存。

## 和 GQA / MHA 的连续谱

$H_{\mathrm{kv}}=H$ 是 MHA；$1 \lt H_{\mathrm{kv}} \lt H$ 是 GQA；$H_{\mathrm{kv}}=1$ 是 MQA。质量上 MQA 最省也最容易伤长上下文和难任务，所以 Llama 70B 停在 GQA 8 组。训练必须就是 MQA：用 MHA 权重推理时乱共享 $K$ 对不上。GQA 论文给了从 MHA checkpoint mean-pool 初始化的办法，那是转换，不是免费的。

Decode 一步 $T=1$，GEMM 很小，时间在读历史 KV。MQA 读带宽约 $\times 1/H$。Prefill 仍是 $T^2$ 注意力，MQA 对 prefill 的加速远小于 decode。Apple 端侧爱听这句。

## 追问

- **broadcast 和 repeat 哪个对？** 数值都能对，若 repeat 只发生在算子里。Cache 布局必须以 $H_{\mathrm{kv}}=1$ 为准。
- **head dim 还是 $D/H$ 吗？** 是。$Q$ 仍按 $H$ 个头切；$K$ 只有一个头，维同样是 $d_h$，不是整条 $D$。
- **能 $K$ 用 $d_h$、$V$ 用别的宽吗？** 标准 MQA 不这样。GQA/MQA 改的是头数，不是头维。
- **softmax 轴？** 仍是 key 长。沿 $H$ 做 softmax 是 `openai-transformer-debug` 那类轴错误，MQA 里更隐蔽，因为 $K$ 没有 $H$。

---
id: coding-decode-step
section: coding
order: 33
level: S
title: 白板：一步 decode，取 q、concat KV、GQA repeat、出 logits
quick: >-
  当前 token 的 $q,k,v$ 形状 `[B, H, 1, D]`。RoPE 用 `cache_len`。$k,v$ 沿序列维接到 cache。算分数前把
  KV repeat 成 $H_q$，cache 里仍是 $H_{\mathrm{kv}}$。输出 logits `[B, 1, V]`。位置写 $0$ 是 silent 错。
tags:
  - Coding
  - Decode
  - GQA
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
    url: https://arxiv.org/abs/2305.13245
    type: primary
  - title: Fast Transformer Decoding — One Write-Head is All You Need
    url: https://arxiv.org/abs/1911.02150
    type: primary
---

## 题怎么来的

Apple / Meta 手写 Transformer 的收口：把 RoPE、KV cache、GQA、lm_head 串成 **一步生成**。OpenAI
debug 卷里最常见的植入是 decode 当 prefill 写：`arange(q_len)` 得到位置 $0$，或把 KV repeat 进
cache。分件见
`coding-rope-cache`、`coding-gqa-repeat`、`coding-mq-attn`。本题要求形状断言能过，并且逐步
greedy 与一次满量 forward 的下一 token 相同。

## 数据沿哪一维长

进入一步时 cache 里 $K,V$ 是 `[B, H_{\mathrm{kv}}, S, D]`，$S$ 是已生成（含 prompt）长度。当前隐状态
`[B, 1, D_{\mathrm{model}}]` 投影得

$$
q\in\mathbb{R}^{B\times H_q\times 1\times D},\quad
k,v\in\mathbb{R}^{B\times H_{\mathrm{kv}}\times 1\times D}.
$$

RoPE 只旋这一步的 $q,k$，下标 $t=S$（若 $S$ 是旧长度，$t$ 就是即将 append 的位置）。历史 $K$ 写入时已经旋过。然后

$$
K\leftarrow\mathrm{cat}(K,k),\quad V\leftarrow\mathrm{cat}(V,v)
$$

沿序列维（shape 里的 $2$）。此时 $S\leftarrow S+1$。**Cache 不 repeat。** 算 $QK^\top$ 前
`repeat_interleave` 成 `[B, H_q, S, D]`，或 fused GQA kernel 在寄存器里广播。分数是 `[B, H_q, 1, S]`，softmax 沿最后一维，把 $V$ 加权成 `[B, H_q, 1, D]`，再 merge heads、输出投影。最终 lm_head 把 `[B, 1, D_model]` 映到 `[B, 1, V]`。

因果在 $T=1$ 时退化成「看全部已缓存 key」，不要再造一份 `[1, S, S]` 下三角。滑窗 / ALiBi / padding 用 `[1,
1, 1, S]` 的 bias，见 `coding-swa-mask`、`coding-alibi`、`coding-attn-mask`。

```python
import torch

def repeat_kv(x, n_rep):
    if n_rep == 1:
        return x
    b, h, s, d = x.shape
    return x[:, :, None].expand(b, h, n_rep, s, d).reshape(b, h * n_rep, s, d)


def decode_step(q, k_t, v_t, cache_k, cache_v, w_o, w_head, n_rep):
    # q: [B, H_q, 1, D] 已 RoPE；k_t,v_t: [B, H_kv, 1, D] 已 RoPE
    cache_k = torch.cat([cache_k, k_t], dim=2)
    cache_v = torch.cat([cache_v, v_t], dim=2)
    k, v = repeat_kv(cache_k, n_rep), repeat_kv(cache_v, n_rep)
    scale = q.size(-1) ** -0.5
    scores = torch.matmul(q, k.transpose(-2, -1)) * scale  # [B, H_q, 1, S]
    p = torch.softmax(scores.float(), dim=-1).to(q.dtype)
    h = torch.matmul(p, v)  # [B, H_q, 1, D]
    h = h.transpose(1, 2).reshape(q.size(0), 1, -1)
    h = h @ w_o.T
    logits = h @ w_head.T  # [B, 1, V]
    return logits, cache_k, cache_v
```

调用方负责：用 `position_ids = cache_len` 做 RoPE，assert `H_q % H_kv == 0`，softmax 前加 mask。Paged 布局把 `cat` 换成 `append_token`，见 `coding-paged-table`。长 $S$ 的注意力本身可走 split-K，见 `coding-flash-decode`。

## 不变量和常见轴错误

不变量：同一前缀 greedy，一步 decode 的 $\arg\max$ logits 等于把该 token 接在 prompt 后做一次因果
prefill、读最后一个位置。对不齐先打印 $S$ 和 `position_ids`，再查是否对 cache 里的 $K$ 又 RoPE 了一次，再查
`repeat` 还是 `repeat_interleave`。

Softmax 轴必须是 key 长。`dim=0` 或沿 head 是 `openai-transformer-debug` 那类 bug；$T=1$
时沿 $T$ 做 softmax 会变成恒等，更隐蔽。MLP / RMSNorm 沿 $D_{\mathrm{model}}$，与 $S$
无关，逐步生成不会因为「统计量沿序列」而漂。

`cat` 每步复制整段 KV 是教学实现。生产用预分配或分页 append。正确性先于原地缓冲。logits 是 `[B, 1, V]` 不是 `[B, S, V]`：一步只需要当前 token 的分类头。

## 追问

- **为什么 logits 是 `[B, 1, V]` 不是 `[B, S, V]`？** 一步只需要当前 token 的分类头。算整段浪费，还会在 shift 上把自己绕进去。
- **先 repeat 再写入 cache？** 带宽和显存都乘 $n_{\mathrm{rep}}$，GQA 白做。Repeat 只发生在算分数时。
- **`cat` 每步复制整段 KV？** 教学实现可以。生产用预分配或分页 append。正确性先于原地缓冲。
- **MQA 怎么收？** $H_{\mathrm{kv}}=1$，$n_{\mathrm{rep}}=H_q$，函数仍成立，见 `coding-mq-attn`。

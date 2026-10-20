---
id: code-swa-mask
section: coding
order: 44
level: A
title: 手写 Sliding Window Attention：prefill 的带状 mask 和 decode 怎么切 cache
quick: "query $i$ 只看 $[i-w+1,\\,i]$：prefill 用带状下三角 mask，decode 只保留窗口内的 key。窗口外的旧 KV 可以丢掉，cache 从 $O(S)$ 降到 $O(w)$。"
tags:
  - SlidingWindow
  - Attention
  - KV Cache
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Mistral 7B
    url: https://arxiv.org/abs/2310.06825
    type: primary
---

和 `code-attention` 的全因果比，只是 keep 集合多了一个下界。常见误区是：窗口写成 $|i-j|\lt w$ 却忘了因果，使未来 token 进入可见范围；或逐 token 生成（decode）时仍用 `triu(T,T)`，$T=1$ 对不上 cache 长度。

## keep 条件

$$
\mathrm{keep}(q,k)=(k\le q)\land(k>q-w).
$$

$w=4096$ 时，位置 $10000$ 只看 $5905..10000$。Gemma-2 每隔几层插一层全因果，local 层用 SWA；手写先把 local 写对。

```python
import torch

def swa_causal_keep(q_pos, k_pos, window):
    return (k_pos <= q_pos) & (k_pos > q_pos - window)

def swa_prefill_mask(T, window, device=None):
    q = torch.arange(T, device=device)[:, None]
    k = torch.arange(T, device=device)[None, :]
    return swa_causal_keep(q, k, window)          # [T,T], True=keep

def swa_decode_mask(past, window, device=None):
    # query 绝对位置 = past，keys 长度 S = past+1
    k = torch.arange(past + 1, device=device)
    return swa_causal_keep(past, k, window)       # [S]
```

decode 实现可以只在 cache 里留最近 $w$ 个 K/V，mask 就全是 True。前缀复用时要注意：fork 得到的 cache 如果已经按窗口裁剪，就无法再访问更早的 token。和 sink 一起用见 `code-attn-sink`。

## 追问

- **复杂度？** 预填充（prefill）仍需处理全部 $T$ 个位置，但每个 query 只与 $w$ 个 key 计算注意力，attention 从 $O(T^2)$ 降到 $O(Tw)$。
- **窗口外的 token 还有用吗？** 信息只能一层一层往前传，和 CNN 的感受野一样。所以 Mistral 靠深度把远处信号递过来。
- **GQA + SWA？** repeat KV 之后再 mask。cache 按 $H_{\mathrm{kv}}\times w$ 计。

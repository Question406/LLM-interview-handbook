---
id: code-chunked-prefill
section: coding
order: 51
level: S
title: 手写 chunked prefill：块内因果，块对 cache 做 cross-attn
quick: "把 prompt 切成长 $C$ 的块，每块把 $K,V$ 追加进 cache，再用带 offset 的因果 mask：块内第 $i$ 个 query 能看到 $j\\le \\mathrm{past}+i$ 的位置。结果应与整段 prefill 一致。"
tags:
  - ChunkedPrefill
  - KV Cache
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "Sarathi: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills"
    url: https://arxiv.org/abs/2308.16369
    type: primary
---

`code-attention` 的 KV cache 实现在一次预填充（prefill）中处理整段输入，因此 $T=S$。分块预填充沿用相同的注意力计算，只把每次处理的长度改为 $T=C$。常见误区是：每块内部用 `triu(C,C)` 却把 cache 里的历史 key 也当成「未来」；或 offset 从 0 算，第二块能看见自己后面、看不见第一块。

## 带 offset 的 causal

已缓存长度 $\mathrm{past}$，当前块长 $T$：

$$
\mathrm{keep}(i,j)=\big[j\le \mathrm{past}+i\big],\quad i\in[0,T),\; j\in[0,\mathrm{past}+T).
$$

第一块 $\mathrm{past}=0$，退回普通 triu。逐 token 生成（decode） 是 $T=1$ 的特例。

```python
import math
import torch

class KVBuf:
    def __init__(self, B, H, max_len, dh):
        self.k = torch.zeros(B, H, max_len, dh)
        self.v = torch.zeros_like(self.k)
        self.len = 0

    def append(self, k, v):
        t = k.size(2)
        self.k[:, :, self.len:self.len + t] = k
        self.v[:, :, self.len:self.len + t] = v
        self.len += t
        return self.k[:, :, :self.len], self.v[:, :, :self.len]

def attn_with_offset(q, k, v, past):
    scores = q @ k.transpose(-1, -2) / math.sqrt(q.size(-1))
    q_pos = torch.arange(past, past + q.size(2), device=q.device)[:, None]
    k_pos = torch.arange(k.size(2), device=q.device)[None, :]
    scores = scores.masked_fill(k_pos > q_pos, float("-inf"))
    return torch.softmax(scores.float(), dim=-1).to(q.dtype) @ v

def chunked_prefill(q, k, v, chunk):
    B, H, T, D = q.shape
    buf = KVBuf(B, H, T, D)
    outs = []
    for s in range(0, T, chunk):
        e = min(s + chunk, T)
        past = buf.len
        kk, vv = buf.append(k[:, :, s:e], v[:, :, s:e])
        outs.append(attn_with_offset(q[:, :, s:e], kk, vv, past))
    return torch.cat(outs, dim=2)
```

调度时，一次迭代可以同时安排若干 decode 步和一块 prefill，使计算负载更均匀。这就是 Sarathi / vLLM 的 chunked prefill。RoPE 用绝对位置 `past+i`。

## 追问

- **和 decode 的差别？** decode $T=1$ 且通常不再对块内做 triu。chunked 的块内仍要因果。
- **块越大越好吗？** 大块更容易充分利用算力，但可能增加首个 token 的等待时间（TTFT）；小块更方便穿插在 decode 请求之间，但会增加 kernel 启动次数。
- **和 prefix cache？** 公共前缀可以整块复用，见 `code-attention` 的 `fork`。chunked 解决的是单条超长输入提示（prompt）。

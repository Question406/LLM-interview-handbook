---
id: code-attn-sink
section: coding
order: 50
level: A
title: 手写 Attention Sink：固定留下开头几个 token，再加滑动窗口
quick: "因果前提下只保留前 $s$ 个 sink 和最近 $w$ 个 token。开头几个 token 吸收了大量注意力，纯滑窗把它们丢掉会打乱注意力分布，所以 decode 时 sink 的 K/V 一直留着。"
tags:
  - AttentionSink
  - StreamingLLM
  - KV Cache
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Efficient Streaming Language Models with Attention Sinks
    url: https://arxiv.org/abs/2309.17453
    type: primary
---

纯 SWA（`code-swa-mask`）把位置 0 切掉之后，很多头的注意力分布失去原先的高权重位置，转而集中到窗口左沿。StreamingLLM 把最初 $s$ 个（常见 $s=4$）当成 sink，和窗口一起保留。

## keep

$$
\mathrm{keep}(q,k)=(k\le q)\land\big[(k\lt s)\lor(k>q-w)\big].
$$

位置 $10$、$s=2$、$w=4$：能看 $0,1$ 以及 $7,8,9,10$。中间 $2..6$ 被丢掉。

```python
import torch

def sink_window_keep(T, sink, window, device=None):
    q = torch.arange(T, device=device)[:, None]
    k = torch.arange(T, device=device)[None, :]
    causal = k <= q
    local = k > q - window
    sinks = k < sink
    return causal & (local | sinks)
```

逐 token 生成（decode） cache 的布局是 `[sink | last w-1 | new]`。新 token 进来时，若超过 $s+w$，丢掉 sink 后面那一个最老的窗口 token，sink 不动。RoPE 要用 token 的**原**绝对位置，不能因为 cache 里下标变了就从 0 重数，否则 sink 的旋转是错的。

## 追问

- **sink 一定是 BOS 吗？** 论文观察是最初几个位置，不必须是特殊 token。有的实现会学一个 sink 占位。
- **和 SWA 训练过的模型？** Mistral 训练就是窗口，推理再加 sink 是补丁。从零训可以显式加 sink。
- **显存？** cache 从 $O(S)$ 收到 $O(s+w)$。$s$ 很小，主要省在 $w$。

---
id: coding-swa-mask
section: coding
order: 27
level: A
title: 白板：sliding window 和因果 mask 合成，prefill 与 decode 的 shape
quick: >-
  位置 $i$ 只看 $j$，满足 $i-W \lt j \le i$。Prefill 加性 mask 形状 `[1, 1, T, S]`；decode 是
  `[1, 1, 1, S]`，query 下标是 cache 长度不是 $0$。窗口外打 $-\infty$，不要打 $0$。
tags:
  - Coding
  - Sliding Window
  - Attention Mask
  - Mistral
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Mistral 7B
    url: https://arxiv.org/abs/2310.06825
    type: primary
  - title: Longformer — The Long-Document Transformer
    url: https://arxiv.org/abs/2004.05150
    type: primary
  - title: Efficient Streaming Language Models with Attention Sinks
    url: https://arxiv.org/abs/2309.17453
    type: primary
---

## 题怎么来的

Mistral 7B 公开用滑动窗口注意力，窗口 $4096$。Apple 端侧和 NVIDIA kernel
白板都爱问：「因果已经下三角了，窗口怎么叠上去，decode 的 mask 长什么样」。系统侧还有 rolling buffer KV，本题先把 **加性
mask 的布尔条件与 shape** 写对。和 padding、文档边界合在一起见 `coding-attn-mask`。Streaming 时窗口把开头
token 一并丢掉会碰到 sink，见 `openai-attention-sink`。

## 两个条件同时成立

Query 下标 $i$、key 下标 $j$，窗口宽 $W$（token 数）。允许看见当且仅当

$$
i-W \lt j \le i.
$$

$j\le i$ 是因果；$j \gt i-W$ 是窗口。两边都是开/闭要说清：常见实现是「最近 $W$ 个，含自己」，即最多看 $W$ 个
key。$W=1$ 只剩当前位置。$W\ge S$ 退化成普通因果。

Mask 是加到 scores `[B, H, T, S]` 上的 bias：keep 的位置是 $0$，其余 $-\infty$。**不要打 $0$
再乘**：softmax 仍会给它正质量。Shape 必须能广播：

- Prefill：$T=S$，bias `[1, 1, T, S]`（或 `[B, 1, T, S]` 若每条窗口不同，通常没有）。
- Decode：当前一步 $T=1$，$S$ 是已缓存长度（含刚 append 的位置），bias `[1, 1, 1, S]`。

Decode 的 $i$ 是 **绝对位置** `cache_len`（0-index 下即将写入 / 刚写入的下标），不是 $0$。写成
`arange(1)` 会让窗口和因果都错：你会以为只看位置 $0$。RoPE 同一处坑，见 `coding-rope-cache`。

```python
import torch

def swa_causal_bias(q_pos, s_len, window):
    # q_pos: [T] 绝对下标；返回 [1, 1, T, S]
    k_pos = torch.arange(s_len)
    q = q_pos[:, None]
    k = k_pos[None, :]
    keep = (k <= q) & (k > q - window)
    bias = torch.zeros(q_pos.numel(), s_len)
    return bias.masked_fill(~keep, float("-inf")).view(1, 1, q_pos.numel(), s_len)


def prefill_swa_bias(seq_len, window):
    return swa_causal_bias(torch.arange(seq_len), seq_len, window)


def decode_swa_bias(cache_len, window):
    # 新 token 下标 = cache_len；key 长 S = cache_len + 1
    s = cache_len + 1
    return swa_causal_bias(torch.tensor([cache_len]), s, window)
```

`k > q - window` 在整数下标上就是 $j \ge i-W+1$。不要用 Python 的 `x < t` 去写 markdown 公式里的
token 下标，比较请留在 $\lt$ 和代码的 `<=`。

## 实现上不必物化 `[T, S]`

训练 / prefill 的 $T$ 大时，`[T, S]` 的 bool mask 本身就是 $O(T^2)$。FlashAttention / SDPA
吃 `window_size` 或 block-sparse 参数，在 tile 里打 $-\infty$，不写回 HBM。白板仍先写稠密 bias，再提
fused。Decode $T=1$ 时 `[1, S]` 很小，物化无所谓；真正省的是 **KV 只保留窗口**（rolling
cache），那是另一题：cache 形状变成 `[B, H, W, D]`，下标取模。Mask 题不要偷偷改 cache 布局，除非评委问。

左 padding：有效 token 的绝对 $i$ 从 pad 长度起算，窗口按 `position_ids` 走，不要按「当前 tensor 里的列号」。多文档 packing 还要再交文档边界，见 `coding-packed-lm`。

$W=1$ 只剩自己；$W\ge S$ 退化成普通因果。整数下标上 $j \gt i-W$ 就是 $j \ge i-W+1$。和训练契约对齐，单测用小 $W$ 数 keep 的个数。不要在 markdown 公式里写尖括号包住下标字母。

## 追问

- **窗口外打 $0$ 行不行？** 不行。$0$ 仍进 softmax。必须是 $-\infty$（或 fused kernel 里的 skip）。
- **decode 为什么是 `[1, 1, 1, S]`？** 这一步只有一个 query；head、batch 靠广播。写成 `[1, 1, S, S]` 是把 prefill 形状抄过来。
- **和 attention sink 一起？** 滑窗丢掉远历史时，保留开头几个 sink token 另开一列 keep，否则质量被重写，见 `openai-attention-sink`。
- **$j=i-W$ 含不含？** 和训练契约一致即可。Mistral 风格是长度 $W$ 的闭窗口；单测用小 $W$ 数 keep 的个数。

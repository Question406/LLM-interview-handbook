---
id: coding-swa-mask
section: coding
order: 27
level: A
title: 白板：sliding window 和因果 mask 合成，prefill 与 decode 的 shape
quick: "位置 $i$ 只看满足 $i-W \\lt j \\le i$ 的 key，窗口外打 $-\\infty$；prefill 偏置是 `[1, 1, T, S]`，decode 是 `[1, 1, 1, S]`，query 下标是 cache 长度。"
tags:
  - 完整编程练习
  - Coding
  - Sliding Window
  - Attention Mask
  - Mistral
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
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

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `swa_causal_bias(q_pos, s_len, window) -> Tensor[1, 1, T, S]`：`q_pos` 是 `[T]` 的 query 绝对下标，key 下标是 `0..s_len-1`。可见位置为 0，其余为 $-\infty$。窗口包含当前 token，每个 query 最多看 `window` 个 key。
- `prefill_swa_bias(seq_len, window)`：prefill 用，`T = S = seq_len`。
- `decode_swa_bias(cache_len, window)`：单步 decode 用，新 token 的绝对下标是 `cache_len`，key 长度是 `cache_len + 1`。
- 两个入口用同一套绝对位置语义；`window` 必须是正整数，否则抛 `ValueError`。

### 输入输出示例

```text
window = 2，query 位置 3   -> 可见 key {2, 3}，key 1 不可见
decode_swa_bias(4, 2)      -> 可见性 [F, F, F, T, T]，等于 prefill_swa_bias(5, 2) 的最后一行
window = 1                 -> 只看自己，可见性矩阵是单位阵
```

### 解题思路与正确性

可见条件是 $q - W \lt k \le q$。右边 $k \le q$ 是因果，左边 $k \gt q - W$ 是窗口。左端必须是严格不等号：在整数下标上它等价于 $k \ge q - W + 1$，从 $q-W+1$ 到 $q$ 正好 $W$ 个 key；写成 $\ge q - W$ 会多看一个。

decode 时把 query 位置设成 `cache_len`，key 长度设成 `cache_len + 1`，算出来的就是 prefill 偏置的最后一行。两条路径共用 `swa_causal_bias`，语义自然一致。

### 完整参考实现（Python 3）

```python
import torch


def swa_causal_bias(q_pos, s_len, window):
    """滑动窗口 + 因果的加性偏置 [1, 1, T, S]：q - window < k <= q 处为 0，其余为 -inf。"""
    if type(window) is not int or window < 1:
        raise ValueError(f"window must be a positive int, got {window!r}")
    query = q_pos[:, None]               # [T, 1]，绝对下标
    key = torch.arange(s_len)[None, :]   # [1, S]
    visible = (key <= query) & (key > query - window)
    bias = torch.zeros(q_pos.numel(), s_len).masked_fill(~visible, float("-inf"))
    return bias.view(1, 1, q_pos.numel(), s_len)


def prefill_swa_bias(seq_len, window):
    """prefill：T = S = seq_len。"""
    return swa_causal_bias(torch.arange(seq_len), seq_len, window)


def decode_swa_bias(cache_len, window):
    """单步 decode：新 token 的下标是 cache_len，key 长度是 cache_len + 1。"""
    return swa_causal_bias(torch.tensor([cache_len]), cache_len + 1, window)
```

### 可执行测试

```python
def visible(bias):
    return torch.isfinite(bias)


# decode 的偏置等于 prefill 的最后一行
prefill = prefill_swa_bias(5, 2)
last = decode_swa_bias(4, 2)
assert prefill.shape == (1, 1, 5, 5)
assert last.shape == (1, 1, 1, 5)
assert torch.equal(visible(prefill[:, :, -1:]), visible(last))

# window=2、query 位置 4：只看 key 3 和 4
assert torch.equal(visible(last[0, 0, 0]), torch.tensor([0, 0, 0, 1, 1], dtype=torch.bool))

# window=1：只看自己
assert torch.equal(visible(prefill_swa_bias(3, 1)[0, 0]), torch.eye(3, dtype=torch.bool))

# 窗口不小于序列长度时退化成普通因果
causal = torch.ones(4, 4, dtype=torch.bool).tril()
assert torch.equal(visible(prefill_swa_bias(4, 10)[0, 0]), causal)

# 每行可见的 key 数是 min(i + 1, window)
counts = visible(prefill_swa_bias(6, 3)[0, 0]).sum(-1)
assert counts.tolist() == [1, 2, 3, 3, 3, 3]

# 可见位置是 0，不是别的值
assert torch.all(last[visible(last)] == 0)

# window 必须为正
try:
    prefill_swa_bias(3, 0)
except ValueError:
    pass
else:
    raise AssertionError("window=0 accepted")
```

### 复杂度与追问

设 query 长度 T、key 长度 S。时间和输出空间都是 O(TS)。

- 追问「真实 kernel 也要物化这张矩阵吗」：不用。这里只是参考 mask，FlashAttention / SDPA 这类滑窗 kernel 在 tile 里直接跳过窗口外的块，见下文。

## 题怎么来的

Mistral 7B 公开使用滑动窗口注意力，窗口是 $4096$。Apple 端侧和 NVIDIA kernel 的白板都爱问：「因果已经是下三角了，窗口怎么叠上去，decode 的 mask 长什么样」。系统侧还有 rolling buffer KV，这题先把加性 mask 的布尔条件和 shape 写对。和 padding、文档边界合在一起的写法见 `coding-attn-mask`。Streaming 时如果窗口把开头的 token 也丢了，会碰到 attention sink 的问题，见 `openai-attention-sink`。

## 两个条件同时成立

Query 下标 $i$、key 下标 $j$，窗口宽 $W$（token 数）。当且仅当

$$
i-W \lt j \le i
$$

时可见。$j\le i$ 是因果，$j \gt i-W$ 是窗口。两端的开闭要说清楚：常见实现是「最近 $W$ 个、包括自己」，也就是最多看 $W$ 个 key。$W=1$ 时只剩当前位置，$W\ge S$ 时退化成普通因果。

mask 是加到 scores `[B, H, T, S]` 上的偏置：可见位置为 $0$，其余为 $-\infty$。不能把窗口外的分数设成 $0$，因为 softmax 仍会给它正的权重。shape 要能广播：

- Prefill：$T=S$，偏置 `[1, 1, T, S]`；如果每条样本的窗口不同就用 `[B, 1, T, S]`，但通常不会这样。
- Decode：这一步 $T=1$，$S$ 是已缓存长度（包括刚 append 的位置），偏置 `[1, 1, 1, S]`。

decode 的 $i$ 是绝对位置 `cache_len`（0-index 下就是即将写入或刚写入的下标），不是 $0$。如果写成 `arange(1)`，窗口和因果都会错，你会以为它只能看位置 $0$。RoPE 在同一个地方有同样的坑，见 `coding-rope-cache`。

## 实现上不必物化 `[T, S]`

训练或输入预填充（prefill，即处理输入并建立缓存）时 $T$ 很大，`[T, S]` 的 bool mask 本身就是 $O(T^2)$。FlashAttention、SDPA 接受 `window_size` 或 block-sparse 参数，在 tile 内部打 $-\infty$，不写回 HBM。白板上仍然先写稠密偏置，再提 fused 实现。

Decode 时 $T=1$，`[1, S]` 很小，物化也无所谓。真正省显存的是 KV 只保留窗口内的部分（rolling cache），那是另一道题：cache 形状变成 `[B, H, W, D]`，写入下标取模。做 mask 题时不要偷偷改 cache 布局，除非面试官问到。

左 padding 时，有效 token 的绝对位置 $i$ 从 pad 长度之后开始算，窗口要按 `position_ids` 来，而不是按当前 tensor 里的列号。多文档 packing 还要再和文档边界取交集，见 `coding-packed-lm`。

## 追问

- **窗口外打 $0$ 行不行？** 不行，$0$ 仍会参与 softmax。必须是 $-\infty$，或者在 fused kernel 里直接跳过。
- **decode 的偏置为什么是 `[1, 1, 1, S]`？** 这一步只有一个 query，head 和 batch 维靠广播。写成 `[1, 1, S, S]` 是把 prefill 的形状照抄过来了。
- **和 attention sink 一起用怎么写？** 滑窗丢掉远处历史时，开头几个 sink token 要额外标成可见，否则注意力质量会被重新分配，生成质量下降，见 `openai-attention-sink`。
- **$j=i-W$ 算不算在窗口里？** 和训练时的约定一致就行。Mistral 风格是长度为 $W$、包含当前位置的窗口，即 $j=i-W$ 不可见；单测时用小 $W$ 数一数每行可见的 key 个数。

## 相关题

- [[coding-attn-mask]]：把因果、padding、文档边界三种条件合成一张 bias，本题的窗口条件可以直接再与上去。
- [[openai-softmax-bug]]：专讲窗口外打 0 为什么不行、softmax 轴写错会怎样，附最小单测。

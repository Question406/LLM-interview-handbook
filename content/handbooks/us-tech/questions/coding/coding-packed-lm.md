---
id: coding-packed-lm
section: coding
order: 18
level: A
title: 白板：packed sequences 的 cu_seqlens 和文档边界 mask
quick: >-
  有效 token 拼成 `[total, D]`，`cu_seqlens` 是长度为 $B+1$ 的前缀和，从 $0$ 到
  $total$。变长 kernel 按这段切序列，互不看。同一条 `[B, T]` 里塞多篇文档，还要块对角因果
  mask，否则后一篇会看见前一篇。
tags:
  - Coding
  - Packed Sequences
  - FlashAttention
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention with IO-Awareness
    url: https://arxiv.org/abs/2205.14135
    type: primary
  - title: FlashAttention (varlen / cu_seqlens API)
    url: https://github.com/Dao-AILab/flash-attention
    type: primary
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
---

## 题怎么来的

训练要去 padding：短句把 `[B, T]` 填满，注意力和 MLP 都在空位上烧。FlashAttention 的 varlen 路径用 `cu_seqlens` 把一个 batch 收成一条 packed 张量。Meta 长上下文训练还会在 **同一条长度 $T$ 的样本里拼多篇文档**，这时只有 causal 不够——后一篇会当前文来读前一篇。NVIDIA 问 kernel 接口，OpenAI debug 问 mask 漏打。IO 背景见 `nvidia-flash-attn`。

## `cu_seqlens`：batch 维变成前缀和

每条样本长度 $\ell_b$，packed token 形状 `[total]` 或 `[total, D]`，

$$
\mathrm{cu}[0]=0,\quad \mathrm{cu}[b]=\sum_{i=0}^{b-1}\ell_i,\quad \mathrm{cu}[B]=\mathrm{total}.
$$

dtype 用 `int32`。第 $b$ 条是 `packed[cu[b] : cu[b+1]]`。`max_seqlen` 是 $\max_b \ell_b$，给 kernel 定 tile。$Q$ 和 $K$ 可以不同 `cu_seqlens`（cross-attn），因果 LM 通常同一份。这条边界是硬的：不同 $b$ 之间 **没有** 注意力，等价于把它们当成独立序列，不是「拼在一起当上下文」。

```python
import torch

def cu_seqlens_from_lens(lens):
    # lens: [B] int64/int32 -> cu: [B+1] int32
    cu = torch.zeros(lens.numel() + 1, dtype=torch.int32, device=lens.device)
    cu[1:] = torch.cumsum(lens, 0).to(torch.int32)
    return cu


def pack_tokens(tokens, lens):
    # tokens: [B, T] 右 pad；返回 packed [total], cu [B+1]
    parts = [tokens[i, : int(lens[i])] for i in range(tokens.size(0))]
    packed = torch.cat(parts, dim=0)
    cu = cu_seqlens_from_lens(lens)
    assert int(cu[-1]) == packed.size(0)
    return packed, cu


def doc_causal_keep(doc_ids):
    # doc_ids: [T]；True 表示允许 i attend j
    causal = torch.tril(torch.ones(doc_ids.numel(), doc_ids.numel(), dtype=torch.bool))
    same = doc_ids[:, None] == doc_ids[None, :]
    return causal & same
```

`cu[-1] == total` 是第一条 assert。lens 和 pad 对不上会在 kernel 里读越界，比 Python 报错更糟。

## 文档边界：causal 不够

把两篇文档拷进同一行 `[T]`，标准下三角仍允许位置 $t$ 看见 $0..t$。若 $t$ 已进入第二篇，它会看见第一篇的所有 token。训练 packing 若不想跨文档泄漏，mask 必须是 **块对角因果**：同 `doc_id` 且 $j\le i$。实现上要么构造 `doc_ids` 再 `masked_fill(-inf)`，要么把每篇文档当成 varlen 的一条序列，让 `cu_seqlens` 切开。后者不物化 `[T, T]` mask，和 FlashAttention 更亲。

RoPE 的 `position_ids` 也要一起定：跨文档是继续累加还是每篇从 $0$ 数，必须和训练一致。Decode 偏移见 `coding-rope-cache`。Loss 只在有效 token 上平均，pad / 文档末的 ignore 见 `coding-cross-entropy`。

## 追问

- **`cu_seqlens` 为什么是 $B+1$ 不是 $B$？** 要同时给出每条的起点和整段终点。只有长度数组的话，kernel 还得自己 cumsum。
- **packed 还要 attention mask 吗？** varlen 路径用 cu 切边界，因果在 kernel 里按每条的局部下标做。再传一份 `[B, T, T]` pad mask 是叠床架屋，还容易和 packed 布局对不上。
- **后一篇看见前一篇一定错吗？** 不一定。有的 packing 故意当超长上下文。面试先问清契约，再写块对角还是纯因果。
- **left pad 怎么 pack？** 先按真实长度切片再 cat。带着 pad 去 cumsum，cu 会把 pad 算进序列。

---
id: coding-packed-lm
section: coding
order: 18
level: A
title: 白板：packed sequences 的 cu_seqlens 和文档边界 mask
quick: "把有效 token 拼成一条，`cu_seqlens` 是长 $B+1$ 的前缀和；同一行塞多篇文档时还要块对角因果 mask，否则后一篇会看见前一篇。"
tags:
  - 完整编程练习
  - Coding
  - Packed Sequences
  - FlashAttention
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
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

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `cu_seqlens_from_lens(lens) -> cu`：`lens` 是 `[B]` 的整数长度，返回 `[B+1]` 的 `int32` 前缀和，`cu[0] = 0`。
- `pack_tokens(tokens, lens) -> (packed, cu)`：`tokens` 形状 `[B, T]`，右 padding；把每行前 `lens[b]` 个有效 token 拼成 `packed`，形状 `[sum(lens)]`。
- `doc_causal_keep(doc_ids) -> [T, T] bool`：`doc_ids` 形状 `[T]`，`True` 表示位置 $i$ 可以看位置 $j$，条件是同一文档且 $j\le i$。同一文档的 token 必须连续出现，不能复用同一个 id 去表示两篇独立文档。
- 约束：$0\le$ `lens[b]` $\le T$，总 token 数不超过 $2^{31}-1$（`int32` 能表示）。`B = 0` 和长度全为 0 都合法。违反约束时抛 `ValueError`。

### 输入输出示例

```text
lens = [2, 0, 1]          -> cu = [0, 2, 2, 3]
B = 0                     -> packed = [], cu = [0]
doc_ids = [0, 0, 1]       -> keep = [[T, F, F],
                                     [T, T, F],
                                     [F, F, T]]
```

### 解题思路与正确性

`pack_tokens` 按每行的有效长度切片再拼接，前缀和 `cu` 记下每段的起止位置：第 $b$ 条样本是 `packed[cu[b]:cu[b+1]]`。拼完后检查 `cu[-1]` 是否等于总长度。

`doc_causal_keep` 把下三角因果条件和“同一文档”条件取与。只有因果的话，第二篇文档的 token 会看到第一篇；加上同文档条件后，mask 变成块对角下三角，跨文档的信息泄漏就被挡住了。

### 完整参考实现（Python 3）

```python
import torch

INT32_MAX = 2**31 - 1


def cu_seqlens_from_lens(lens):
    """[B] 长度 -> [B+1] int32 前缀和，cu[0] = 0。"""
    total = int(lens.sum()) if lens.numel() else 0
    if total > INT32_MAX:
        raise ValueError(f"total tokens {total} does not fit in int32")
    cu = torch.zeros(lens.numel() + 1, dtype=torch.int32, device=lens.device)
    cu[1:] = torch.cumsum(lens, 0).to(torch.int32)
    return cu


def pack_tokens(tokens, lens):
    """tokens: [B, T] 右 pad；返回 packed [total] 和 cu [B+1]。"""
    batch_size, max_len = tokens.shape
    if lens.shape != (batch_size,):
        raise ValueError(f"lens shape {tuple(lens.shape)} does not match batch size {batch_size}")
    if lens.numel() and (int(lens.min()) < 0 or int(lens.max()) > max_len):
        raise ValueError(f"lens must lie in [0, {max_len}], got {lens.tolist()}")

    parts = [tokens[b, :int(lens[b])] for b in range(batch_size)]
    packed = torch.cat(parts, dim=0) if parts else tokens.new_empty((0,))
    cu = cu_seqlens_from_lens(lens)
    if int(cu[-1]) != packed.size(0):
        raise ValueError("cu_seqlens does not match the packed length")
    return packed, cu


def doc_causal_keep(doc_ids):
    """doc_ids: [T]，同一文档连续出现。返回 [T, T]，True 表示 i 可以看 j（同文档且 j <= i）。"""
    seq_len = doc_ids.numel()
    if seq_len:
        starts = 1 + int((doc_ids[1:] != doc_ids[:-1]).sum())
        if starts != doc_ids.unique().numel():
            raise ValueError("each doc id must appear in one contiguous run")
    causal = torch.tril(torch.ones(seq_len, seq_len, dtype=torch.bool))
    same_doc = doc_ids[:, None] == doc_ids[None, :]
    return causal & same_doc
```

### 可执行测试

```python
torch.set_num_threads(1)


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError from {fn.__name__}")


# 中间夹一条空样本
tokens = torch.tensor([[1, 2, 0], [0, 0, 0], [3, 0, 0]])
packed, cu = pack_tokens(tokens, torch.tensor([2, 0, 1]))
assert packed.tolist() == [1, 2, 3]
assert cu.tolist() == [0, 2, 2, 3]
assert cu.dtype == torch.int32

# B = 0
packed, cu = pack_tokens(torch.empty((0, 3), dtype=torch.long), torch.empty(0, dtype=torch.long))
assert packed.numel() == 0
assert cu.tolist() == [0]

# 长度全为 0
packed, cu = pack_tokens(torch.zeros(2, 3, dtype=torch.long), torch.tensor([0, 0]))
assert packed.numel() == 0
assert cu.tolist() == [0, 0, 0]

# 长度越界或个数不对
expect_value_error(pack_tokens, tokens, torch.tensor([4, 0, 1]))
expect_value_error(pack_tokens, tokens, torch.tensor([-1, 0, 1]))
expect_value_error(pack_tokens, tokens, torch.tensor([1, 1]))

# 块对角因果：第二篇文档看不到第一篇
keep = doc_causal_keep(torch.tensor([0, 0, 1]))
assert keep.tolist() == [[True, False, False], [True, True, False], [False, False, True]]

# 同一个 id 不连续出现时拒绝
expect_value_error(doc_causal_keep, torch.tensor([0, 1, 0]))
```

### 复杂度与追问

设 $B$ 为 batch 大小，$N$ 为总有效 token 数，$T$ 为行长度。`pack_tokens` 的时间和输出都是 $O(B+N)$；稠密的文档 mask 另外需要 $O(T^2)$，varlen kernel 用 `cu_seqlens` 切边界，不需要这份矩阵。

## 题怎么来的

训练时要去掉 padding：短句被填满成 `[B, T]` 之后，注意力和 MLP 仍然会在这些空位上计算，白白浪费。FlashAttention 的 varlen 路径用 `cu_seqlens` 把一个 batch 收成一条 packed 张量。Meta 的长上下文训练还会在同一条长度为 $T$ 的样本里拼多篇文档，这时只有 causal mask 不够，后一篇会把前一篇当成上下文。NVIDIA 会问 kernel 接口，OpenAI 的 debug 题会问 mask 漏了哪一层。IO 方面的背景见 `nvidia-flash-attn`。

## `cu_seqlens`：batch 维变成前缀和

设每条样本长度为 $\ell_b$，packed token 的形状是 `[total]` 或 `[total, D]`：

$$
\mathrm{cu}[0]=0,\quad \mathrm{cu}[b]=\sum_{i=0}^{b-1}\ell_i,\quad \mathrm{cu}[B]=\mathrm{total}.
$$

dtype 用 `int32`。第 $b$ 条是 `packed[cu[b] : cu[b+1]]`。`max_seqlen` 是 $\max_b \ell_b$，kernel 用它确定分块大小。$Q$ 和 $K$ 可以用不同的 `cu_seqlens`（cross-attention），因果 LM 通常共用一份。这条边界是硬边界：不同 $b$ 之间完全没有注意力，相当于把它们当成独立序列，而不是拼在一起当上下文。

`cu[-1] == total` 是第一条要做的检查。lens 和 pad 对不上时，kernel 会越界读内存，这比 Python 报错更难排查。

## 文档边界：causal 不够

把两篇文档放进同一行 `[T]`，标准下三角 mask 仍允许位置 $t$ 看到 $0..t$ 的所有位置。如果 $t$ 已经在第二篇里，它就会看到第一篇的全部 token。训练 packing 时如果不希望跨文档泄漏，mask 必须是块对角因果：同 `doc_id` 且 $j\le i$。实现上有两种办法：一是构造 `doc_ids` 再 `masked_fill(-inf)`；二是把每篇文档当成 varlen 的一条序列，让 `cu_seqlens` 切开。后者不需要真的构造 `[T, T]` 的 mask，更适合 FlashAttention。

RoPE 的 `position_ids` 也要一起约定：跨文档时是继续累加，还是每篇从 $0$ 开始数，必须和训练时一致。decode 时的位置偏移见 `coding-rope-cache`。loss 只在有效 token 上平均，pad 和文档末尾的 ignore 处理见 `coding-cross-entropy`。

## 追问

- **`cu_seqlens` 为什么是 $B+1$ 而不是 $B$？** 要同时给出每条的起点和最后的终点。只给长度数组的话，kernel 还得自己做一次 cumsum。
- **packed 之后还要 attention mask 吗？** varlen 路径用 `cu_seqlens` 切边界，因果在 kernel 里按每条的局部下标处理。再传一份 `[B, T, T]` 的 pad mask 是重复工作，还容易和 packed 布局对不上。
- **后一篇看见前一篇一定是错的吗？** 不一定。有的 packing 就是故意当超长上下文用。面试时先问清约定，再决定写块对角还是纯因果。
- **left pad 怎么 pack？** 先按真实长度切出有效部分再拼接。如果带着 pad 去 cumsum，`cu` 会把 pad 也算进序列里。

## 相关题

- [[meta-pack-seq]]：同一主题的 Meta 口答版，多讲了 `position_ids` 重置、RoPE 和 SFT 为什么更不能串话。
- [[coding-attn-mask]]：把文档边界写成显式的加性 mask，并和因果、padding 合成一张，适合不走 varlen kernel 的情况。
- [[openai-long-ctx-train]]：长上下文续训里的 packing，问题放在 RoPE 基频和续训配方的大背景下。
- [[sys-eos-mask]]：后训练里多条回答 pack 在一条序列时，loss mask 也要按每条的 EOS 切开。

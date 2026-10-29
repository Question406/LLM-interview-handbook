---
id: coding-packed-lm
section: coding
order: 18
level: A
title: 白板：packed sequences 的 cu_seqlens 和 document boundaries mask
quick: >-
  先按真实长度拼接有效 token，用长度为 $B+1$ 的 `cu_seqlens` prefix sum 标出各段起止。同一行放多篇独立文档时，要用块对角
  causal mask，或把每篇当 varlen 序列，防止跨文档 attention。
tags:
  - 完整编程练习
  - Coding
  - Packed Sequences
  - FlashAttention
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: >-
      FlashAttention — Fast and Memory-Efficient Exact Attention with
      IO-Awareness
    url: 'https://arxiv.org/abs/2205.14135'
    type: primary
  - title: FlashAttention (varlen / cu_seqlens API)
    url: 'https://github.com/Dao-AILab/flash-attention'
    type: primary
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: 'https://arxiv.org/abs/2307.09288'
    type: primary
---

## 题目描述

将右侧 padding 的 token batch 压成一维有效 token 流，生成 sequence boundaries，并构造隔离不同文档的 causal 可见性 matrix。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `cu_seqlens_from_lens(lens) -> cu`：`lens` 是 `[B]` 的整数长度，返回 `[B+1]` 的 `int32` prefix sum，`cu[0] = 0`。
- `pack_tokens(tokens, lens) -> (packed, cu)`：`tokens` 形状 `[B, T]`，右 padding；把每行前 `lens[b]` 个有效 token 拼成 `packed`，形状 `[sum(lens)]`。
- `doc_causal_keep(doc_ids) -> [T, T] bool`：`doc_ids` 形状 `[T]`，`True` 表示位置 $i$ 可以看位置 $j$，条件是同一文档且 $j\le i$。同一文档的 token 必须连续出现，不能复用同一个 id 去表示两篇独立文档。
- 约束：$0\le$ `lens[b]` $\le T$，总 token 数不超过 $2^{31}-1$（`int32` 能表示）。`B = 0` 和长度全为 0 都合法。

### 输入输出示例

```text
tokens = [[1,2,0], [0,0,0], [3,0,0]], lens = [2,0,1]
pack_tokens(tokens,lens) -> (packed=[1,2,3], cu=[0,2,2,3])
cu_seqlens_from_lens([]) -> [0]
doc_causal_keep([0,0,1]) -> [[True,False,False],
                            [True,True,False],
                            [False,False,True]]
```

## 解题思路与参考答案

packed LM 先丢掉 pad，再把有效 token 拼接，并用 attention isolation 保证独立样本互不关注。`pack_tokens` 按每行有效长度 evaluation slices，prefix sum `cu` 记录起止，第 $b$ 条样本就是 `packed[cu[b]:cu[b+1]]`。拼完后检查 `cu[-1]` 是否等于总长度。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `cu_seqlens_from_lens(lens) -> cu`：`lens` 是 `[B]` 的整数长度，返回 `[B+1]` 的 `int32` prefix sum，`cu[0] = 0`。
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

`doc_causal_keep` 把下三角 causal 条件和“同一文档”条件取与。只有 causal 的话，第二篇文档的 token 会看到第一篇；加上同文档条件后，mask 变成块对角下三角，跨文档的信息 leakage 就被挡住了。

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
        raise ValueError(
            f"lens shape {tuple(lens.shape)} does not match batch size {batch_size}"
        )
    if lens.numel() and (int(lens.min()) < 0 or int(lens.max()) > max_len):
        raise ValueError(f"lens must lie in [0, {max_len}], got {lens.tolist()}")

    parts = [tokens[b, : int(lens[b])] for b in range(batch_size)]
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

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert packed.tolist() == [1, 2, 3]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

数值结果用 `allclose` 一类带容差的 assertion 检查，并同时确认形状；随机输入固定 seed。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

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
packed, cu = pack_tokens(
    torch.empty((0, 3), dtype=torch.long), torch.empty(0, dtype=torch.long)
)
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
assert keep.tolist() == [
    [True, False, False],
    [True, True, False],
    [False, False, True],
]

# 同一个 id 不连续出现时拒绝
expect_value_error(doc_causal_keep, torch.tensor([0, 1, 0]))
```

### 复杂度与追问

设 $B$ 为 batch 大小，$N$ 为总有效 token 数，$T$ 为行长度。`pack_tokens` 的时间和输出都是 $O(B+N)$；稠密的文档 mask 另外需要 $O(T^2)$，varlen kernel 用 `cu_seqlens` 分隔 documents，不需要这份 matrix。

## 题怎么来的

训练时要去掉 padding：短句被填满成 `[B, T]` 之后，attention 和 MLP 仍然会在这些空位上计算，白白浪费。FlashAttention 的 varlen 路径用 `cu_seqlens` 把一个 batch 收成一条 packed tensor。Meta 的 long context 训练还会在同一条长度为 $T$ 的样本里拼多篇文档，这时只有 causal mask 不够，后一篇会把前一篇当成上下文。NVIDIA 会问 kernel 接口，OpenAI 的 debug 题会问 mask 漏了哪一层。IO 方面的背景见 `nvidia-flash-attn`。

## `cu_seqlens`：batch 维变成 prefix sum

设每条样本长度为 $\ell_b$，packed token 的形状是 `[total]` 或 `[total, D]`：

$$
\mathrm{cu}[0]=0,\quad \mathrm{cu}[b]=\sum_{i=0}^{b-1}\ell_i,\quad \mathrm{cu}[B]=\mathrm{total}.
$$

dtype 用 `int32`。第 $b$ 条是 `packed[cu[b] : cu[b+1]]`。`max_seqlen` 是 $\max_b \ell_b$，kernel 用它确定分块大小。$Q$ 和 $K$ 可以用不同的 `cu_seqlens`（cross-attention），causal LM 通常共用一份。这是一项 hard constraint：不同 $b$ 之间完全没有 attention，相当于把它们当成独立序列，而不是拼在一起当上下文。

`cu[-1] == total` 是第一条要做的检查。lens 和 pad 对不上时，kernel 会越界读内存，这比 Python 报错更难排查。

## document boundaries：causal 不够

把两篇文档放进同一行 `[T]`，标准下三角 mask 仍允许位置 $t$ 看到 $0..t$ 的所有位置。如果 $t$ 已经在第二篇里，它就会看到第一篇的全部 token。训练 packing 时如果不希望跨文档 leakage，mask 必须是块对角 causal：同 `doc_id` 且 $j\le i$。实现上有两种办法：一是构造 `doc_ids` 再 `masked_fill(-inf)`；二是把每篇文档当成 varlen 的一条序列，让 `cu_seqlens` 切开。后者不需要真的构造 `[T, T]` 的 mask，更适合 FlashAttention。

RoPE 的 `position_ids` 也要一起约定：跨文档时是继续累加，还是每篇从 $0$ 开始数，必须和训练时一致。decode 时的位置偏移见 `coding-rope-cache`。loss 只在有效 token 上平均，pad 和文档末尾的 ignore 处理见 `coding-cross-entropy`。

## 追问

**`cu_seqlens` 为什么是 $B+1$ 而不是 $B$？**
要同时给出每条的起点和最后的终点。只给长度数组的话，kernel 还得自己做一次 cumsum。
**packed 之后还要 attention mask 吗？**
varlen 路径用 `cu_seqlens` 分隔 documents，causal 在 kernel 里按每条的局部下标处理。再传一份 `[B, T, T]` 的 pad mask 是重复工作，还容易和 packed 布局对不上。
**后一篇看见前一篇一定是错的吗？**
不一定。有的 packing 就是故意当超 long context 用。面试时先问清约定，再决定写块对角还是纯 causal。
**left pad 怎么 pack？**
先按真实长度切出有效部分再拼接。如果带着 pad 去 cumsum，`cu` 会把 pad 也算进序列里。

## 相关题

- [[meta-pack-seq]]：同一主题的 Meta 口答版，多讲了 `position_ids` 重置、RoPE 和 SFT 为什么更不能串话。
- [[coding-attn-mask]]：把 document boundaries 写成显式的加性 mask，并和 causal、padding 合成一张，适合不走 varlen kernel 的情况。
- [[openai-long-ctx-train]]：long context 续训里的 packing，问题放在 RoPE 基频和续训配方的大背景下。
- [[sys-eos-mask]]：post-training 里多条回答 pack 在一条序列时，loss mask 也要按每条的 EOS 切开。

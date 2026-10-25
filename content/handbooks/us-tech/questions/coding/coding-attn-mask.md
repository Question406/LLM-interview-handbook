---
id: coding-attn-mask
section: coding
order: 34
level: A
title: 白板：因果、padding、文档边界合成一张注意力 mask
quick: "先把因果 $j\\le i$、key 非 pad、query 与 key 同文档三个条件按位与，再生成 `[B, 1, T, S]` 的加性 bias。合法位填 $0$，非法位填 $-\\infty$；比如 packing 后第二篇文档不能读第一篇，一行全屏蔽时还要由 softmax 端处理 NaN。"
tags:
  - 完整编程练习
  - Coding
  - Attention Mask
  - Packed Sequences
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: FlashAttention (varlen / cu_seqlens API)
    url: https://github.com/Dao-AILab/flash-attention
    type: primary
  - title: Attention is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

## 题目描述

为训练和增量解码构造注意力偏置，同时满足因果、padding 与文档隔离三个可见性条件。

以下接口、边界和规模限制是手册重构的练习约定，不代表面试原题逐字原文；输入默认满足所列合法约束。

### 接口与规则

- `compose_attn_bias(q_pos, k_pos, key_valid, doc_q, doc_k)`：`q_pos` 形状 `[T]`，`k_pos` 形状 `[S]`，`key_valid` 是 `[B, S]` 的布尔张量（True 表示不是 pad），`doc_q` 和 `doc_k` 分别是 `[B, T]` 和 `[B, S]` 的文档 id。返回 `[B, 1, T, S]` 的 float32 加性 bias：因果、key 有效、同一文档三个条件都满足的位置是 $0$，其余是 $-\infty$。
- `decode_attn_bias(s_len, key_valid, doc_ids)`：逐 token 生成时用。`s_len` 已经算上新 token，新 query 就是第 `s_len - 1` 列；`key_valid` 和 `doc_ids` 都是 `[B, s_len]`。返回 `[B, 1, 1, s_len]`。`s_len >= 1`。
- 输入形状合法、位置是整数。因果条件为 `k_pos[j] <= q_pos[i]`。一行全被屏蔽是允许的，此接口只返回全 `-inf` 的 bias。

### 输入输出示例

```text
q_pos = [1, 2], k_pos = [0, 1, 2, 3]
key_valid = [[T, T, F, T]], doc_q = [[0, 1]], doc_k = [[0, 0, 1, 1]]

保留位置（1 = 有限值 0，0 = -inf）：
query 1 (doc 0): [1, 1, 0, 0]   # key 2 是 pad，key 3 在未来
query 2 (doc 1): [0, 0, 0, 0]   # key 0、1 属于 doc 0；key 2 是 pad；key 3 在未来
```

## 解题思路与参考答案

我会先分别算因果、key 是否有效和是否同文档，再按位与成 keep，最后转成加性 bias。比如两个文档拼进同一行，即使前一个文档在时间上更早，后一个文档也不能读取它；只加因果 mask 挡不住这种泄漏。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，只在 CPU 浮点张量上验证，没有验证 GPU、多卡或性能。

### 题面、接口与约束

- `compose_attn_bias(q_pos, k_pos, key_valid, doc_q, doc_k)`：`q_pos` 形状 `[T]`，`k_pos` 形状 `[S]`，`key_valid` 是 `[B, S]` 的布尔张量（True 表示不是 pad），`doc_q` 和 `doc_k` 分别是 `[B, T]` 和 `[B, S]` 的文档 id。返回 `[B, 1, T, S]` 的 float32 加性 bias：因果、key 有效、同一文档三个条件都满足的位置是 $0$，其余是 $-\infty$。
- `decode_attn_bias(s_len, key_valid, doc_ids)`：逐 token 生成时用。`s_len` 已经算上新 token，新 query 就是第 `s_len - 1` 列；`key_valid` 和 `doc_ids` 都是 `[B, s_len]`。返回 `[B, 1, 1, s_len]`。`s_len < 1` 时抛 `ValueError`。
- 输入形状合法、位置是整数。一行全被屏蔽是允许的，这时 softmax 会得到 NaN，由调用方处理（见复杂度与追问）。

### 输入输出示例

```text
q_pos = [1, 2], k_pos = [0, 1, 2, 3]
key_valid = [[T, T, F, T]], doc_q = [[0, 1]], doc_k = [[0, 0, 1, 1]]

保留位置（1 = 有限值 0，0 = -inf）：
query 1 (doc 0): [1, 1, 0, 0]   # key 2 是 pad，key 3 在未来
query 2 (doc 1): [0, 0, 0, 0]   # key 0、1 属于 doc 0；key 2 是 pad；key 3 在未来
```

### 解题思路与正确性

三个条件各自算成布尔张量：因果比较只依赖位置，形状 `[T, S]`；padding 只依赖 key，形状 `[B, 1, 1, S]`；同文档比较 query 和 key 的 id，形状 `[B, 1, T, S]`。把它们广播后按位与，得到 `keep`，再把 `~keep` 的位置填成 $-\infty$。batch 维和 head 维要显式留出来，否则加到 `[B, H, T, S]` 的 scores 上时会广播错位。

decode 只是 $T=1$ 的特例：query 的位置是当前绝对位置 `s_len - 1`，文档 id 取那一列，然后复用同一个函数。

### 完整参考实现（Python 3）

```python
import torch


def compose_attn_bias(q_pos, k_pos, key_valid, doc_q, doc_k):
    """合成因果 + padding + 文档边界的加性 attention bias。

    q_pos: [T]，k_pos: [S]，key_valid: [B, S]（True = 非 pad），
    doc_q: [B, T]，doc_k: [B, S]。返回 [B, 1, T, S]，保留位为 0，其余为 -inf。
    """
    causal = k_pos[None, :] <= q_pos[:, None]                      # [T, S]
    not_pad = key_valid[:, None, None, :]                          # [B, 1, 1, S]
    same_doc = doc_q[:, None, :, None] == doc_k[:, None, None, :]  # [B, 1, T, S]
    keep = causal[None, None] & not_pad & same_doc                 # [B, 1, T, S]
    bias = torch.zeros(keep.shape)
    return bias.masked_fill(~keep, float("-inf"))


def decode_attn_bias(s_len, key_valid, doc_ids):
    """单步 decode 的 bias：新 query 位于第 s_len - 1 列。

    key_valid、doc_ids: [B, s_len]。返回 [B, 1, 1, s_len]。
    """
    if s_len < 1:
        raise ValueError(f"s_len must be >= 1, got {s_len}")
    q_pos = torch.tensor([s_len - 1])
    k_pos = torch.arange(s_len)
    doc_q = doc_ids[:, s_len - 1:s_len]  # [B, 1]
    return compose_attn_bias(q_pos, k_pos, key_valid, doc_q, doc_ids)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert bias.shape == (1, 1, 2, 4)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_error(error_type, fn, *args):
    try:
        fn(*args)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


torch.set_num_threads(1)

# 三个条件一起生效：pad、未来、跨文档都被屏蔽
q_pos = torch.tensor([1, 2])
k_pos = torch.arange(4)
key_valid = torch.tensor([[True, True, False, True]])
doc_q = torch.tensor([[0, 1]])
doc_k = torch.tensor([[0, 0, 1, 1]])
bias = compose_attn_bias(q_pos, k_pos, key_valid, doc_q, doc_k)
expected_keep = torch.tensor([[1, 1, 0, 0], [0, 0, 0, 0]], dtype=torch.bool)
assert bias.shape == (1, 1, 2, 4)
assert torch.equal(torch.isfinite(bias[0, 0]), expected_keep)
assert torch.all(bias[0, 0][expected_keep] == 0)

# 单文档、无 pad 时退化成普通因果下三角
positions = torch.arange(3)
all_valid = torch.ones(1, 3, dtype=torch.bool)
one_doc = torch.zeros(1, 3, dtype=torch.long)
bias = compose_attn_bias(positions, positions, all_valid, one_doc, one_doc)
assert torch.equal(torch.isfinite(bias[0, 0]), torch.ones(3, 3, dtype=torch.bool).tril())

# decode：新 token 能看到同文档的全部历史
bias = decode_attn_bias(3, all_valid, one_doc)
assert bias.shape == (1, 1, 1, 3)
assert torch.isfinite(bias).all()

# decode：新 token 在第二篇文档时看不到第一篇
bias = decode_attn_bias(3, all_valid, torch.tensor([[0, 1, 1]]))
assert torch.equal(torch.isfinite(bias[0, 0, 0]), torch.tensor([False, True, True]))

# s_len 必须至少为 1
expect_error(ValueError, decode_attn_bias, 0, all_valid, one_doc)
```

### 复杂度与追问

设 batch 为 $B$、query 长度为 $T$、key 长度为 $S$。时间和输出空间都是 $O(BTS)$；head 维靠广播，不额外占空间。

- 追问「一行全被屏蔽怎么办」：softmax 对全 $-\infty$ 的行会得到 NaN。要么在 softmax 端定义这种行输出 0，要么保证每个有效 query 至少能看到自己（对角线保留），pad 的 query 再在损失端 ignore 掉。
- 追问「生产上会物化这张表吗」：一般不会。FlashAttention 的 varlen 接口用 `cu_seqlens` 划分序列，因果在 kernel 里按局部下标算，不需要 $T\times S$ 的稠密 mask。

## 题怎么来的

OpenAI 的 Transformer debug 题和 Meta 的 packing 训练题都会问：mask 漏了一层会怎样。只写因果时，pad 位置仍然分到注意力概率，后一篇文档也能读到前一篇；只写 padding 时，未来 token 的信息会泄漏。正确做法是把三个条件按位与成一张 `keep`，再变成加性 $-\infty$。

文档 packing 的 `cu_seqlens` 写法见 `coding-packed-lm`；滑动窗口是第四个条件，见 `coding-swa-mask`。

## 三个条件，一张 bias

设 query 位置为 $i$、key 位置为 $j$。$i,j$ 可以是绝对的 `position_ids`，在 packed 的一行里则是列下标。允许注意力当且仅当：

$$
(j\le i)\ \wedge\ \mathrm{valid}(j)\ \wedge\ \mathrm{doc}(i)=\mathrm{doc}(j).
$$

$\mathrm{valid}(j)$ 来自 padding：右 pad 时，$j$ 超过真实长度就是假；左 pad 时，前缀的 pad 是假。query 侧如果也有 pad，那些行的输出本来就会在损失里被 ignore，但 key 侧必须挡住，否则有效 query 会读到 pad 位置的 $k$。$\mathrm{doc}$ 是文档 id；只有一篇文档时它是常数，这个条件永远成立。

`keep` 的形状要能广播到 scores 的 `[B, H, T, S]`，通常写成 `[B, 1, T, S]`。然后

$$
\mathrm{bias}=\begin{cases}0 & \text{keep}\\ -\infty &
\text{otherwise.}\end{cases}
$$

bias 加在 $QK^\top/\sqrt{D}$ 之后、softmax 之前。非法位填 $0$ 等于没有 mask。decode 时 $T=1$，bias 是 `[B, 1, 1, S]`，$i$ 要取当前的绝对位置；如果拿 $0$ 去和 $j$ 比因果，新 token 就只能看到第 0 个位置。

ALiBi 是另一张加性表，直接和这张 bias 相加即可：非法位已经是 $-\infty$，再加上斜率项也还是 $-\infty$，见 `coding-alibi`。不要先把两张 mask 用乘法混成 $0/1$，再当 logits 用。

用 `cu_seqlens` 把不同样本切成独立序列后，就不必再物化跨样本的 pad mask；如果每条 varlen 序列恰好是一篇文档，同文档条件也可以省掉。稠密的 `[B, T, S]` 只是白板上的契约。

## 漏哪一层，现象不一样

- 漏因果：训练 loss 很好看，生成时却像在看未来，或者和 prefix LM 混在一起。
- 漏 padding：pad 位置的 $k$ 参与归一化，短句的表示被拉向 pad 向量；batch 里长度差越大，偏得越厉害。
- 漏文档边界：下一篇文档可以抄上一篇的答案。packing 越密，这种数据泄漏越容易被误当成模型能力。

一张 `[B, S]` 的 `attention_mask` 通常只编码 padding，因此还要分别确认因果和文档边界；SDPA 的 `is_causal` 也需单独设置。

FlashAttention 的稠密 mask 接口接受布尔 mask 或加性 bias；varlen 接口用 `cu_seqlens` 划分样本，因果在 kernel 内按局部下标处理。白板上先写稠密的三条件与，再说明生产路径不会物化 $T\times S$。

## 追问

**公式里为什么写 $\le$，不写尖括号？**
构建器会把尖括号包着字母的写法当成 HTML 标签。下标写成 $1:t-1$，比较写 $\le$、$\lt$。
**query 的 pad 要不要进 keep？**
挡住 key 侧的 pad 是正确性要求。query 行如果全是 $-\infty$，softmax 会出 NaN；pad query 的损失本来就 ignore，可以跳过它的 softmax，或者先保证对角线保留。
**decode 时还要文档 id 吗？**
要。生成落在第二篇文档时，不能让 key 扫到第一篇，除非训练时就允许跨文档注意力。
**和滑动窗口一起用？**
在 `keep` 上再与一个 $i-W \lt j$。四个条件仍然合成一张 bias，见 `coding-swa-mask`。

## 相关题

- [[coding-swa-mask]]：在因果条件上再加滑动窗口，并分开写 prefill 和 decode 两种 bias 形状。
- [[coding-packed-lm]]：文档边界的另一种做法，不物化 mask，而是用 `cu_seqlens` 走 varlen kernel。
- [[meta-pack-seq]]：Meta 的口答版，讲 packing 时为什么文档要互相隔离、`position_ids` 要重置，不写代码。
- [[openai-softmax-bug]]：mask 填 0 而不是 $-\infty$、softmax 轴写错会怎样，以及怎么写单测固定住。
- [[apple-mha-code]]：完整的手写 MHA，mask 只是其中一步，重点在 shape 和拆 head。
- [[apple-ondevice-quant]]：端侧量化图里 $-\infty$ 可能失效，要改用 fp16 能表示的大负数。

---
id: coding-alibi
section: coding
order: 28
level: A
title: 白板：ALiBi 斜率加到 scores 上，decode 用 cache 长度当 query 位
quick: "ALiBi 在 softmax 前给每个 head 的 scores 加 $m_h(j-i)$，远处历史得到更负的偏置，未来位置另加因果 mask。decode 时新 query 的位置就是旧 cache 长度，偏置形状 `[1, H, 1, S]`；与 prefill 最后一行对照就能检查偏移。"
tags:
  - 完整编程练习
  - Coding
  - ALiBi
  - Position Bias
  - HuggingFace
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Train Short, Test Long — Attention with Linear Biases Enables Input Length Extrapolation
    url: https://arxiv.org/abs/2108.12409
    type: primary
  - title: BLOOM — A 176B-Parameter Open-Access Multilingual Language Model
    url: https://arxiv.org/abs/2211.05100
    type: secondary
  - title: Hugging Face ALiBi implementation notes
    url: https://huggingface.co/docs/transformers/en/model_doc/bloom
    type: secondary
---

## 题目描述

实现 ALiBi 的每头斜率和因果位置偏置接口。输入包括 query 的绝对位置、key 序列长度以及 head 斜率；输出必须同时表达距离惩罚和未来位置不可见的约束。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `alibi_slopes(n_heads) -> Tensor[H]`：生成每个 head 的斜率。`n_heads=H` 是任意正整数。若 H 是 2 的幂，第 i 项为 `2^(-8*(i+1)/H)`（i 从 0 开始）。否则令 m 为不超过 H 的最大 2 的幂，先取 m 头的全部斜率，再按下标 0、2、4…取 2m 头的斜率，补到 H 项。
- `alibi_score_bias(q_pos, s_len, slopes) -> Tensor[1, H, T, S]`：`q_pos` 是 `[T]` 的 query 绝对位置，key 位置是 `0..s_len-1`。可见位置（`j <= q_pos[t]`）的值是 `m_h * (key_pos - query_pos)`，未来位置是 $-\infty$。
- `decode_alibi(cache_len, slopes) -> Tensor[1, H, 1, cache_len + 1]`：`cache_len` 是不含新 token 的旧 cache 长度，也就是新 token 的绝对下标。
- 假定 `n_heads` 为正整数，所有张量在 CPU 上。

### 示例

```text
alibi_slopes(8) -> [1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128, 1/256]
alibi_slopes(3) -> [1/16, 1/256, 1/4]
decode_alibi(2, slopes=[0.5]) -> [[[[-1.0, -0.5, 0.0]]]]
alibi_score_bias(q_pos=[0], s_len=2, slopes=[0.5]) -> [[[[0.0, -inf]]]]
```

## 解题思路与参考答案

我会先为每个 query head 生成固定斜率，再把相对距离乘斜率加到 attention scores，最后单独屏蔽未来位置。比如旧 cache 长度为 2，新 query 位于 2，三个 key 的距离就是 -2、-1、0；这应与 prefill 最后一行完全相同。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `alibi_slopes(n_heads) -> Tensor[H]`：生成每个 head 的斜率。`n_heads` 是任意正整数，不是 2 的幂时按原论文参考代码的递归规则补齐。
- `alibi_score_bias(q_pos, s_len, slopes) -> Tensor[1, H, T, S]`：`q_pos` 是 `[T]` 的 query 绝对位置，key 位置是 `0..s_len-1`。可见位置（$j \le i$）的值是 `m_h * (key_pos - query_pos)`，未来位置是 $-\infty$。
- `decode_alibi(cache_len, slopes) -> Tensor[1, H, 1, cache_len + 1]`：`cache_len` 是不含新 token 的旧 cache 长度，也就是新 token 的绝对下标。
- `n_heads` 不是正整数时抛 `ValueError`；所有张量在 CPU 上。

### 输入输出示例

```text
alibi_slopes(8)   -> [1/2, 1/4, ..., 1/256]
alibi_slopes(3)   -> [1/16, 1/256, 1/4]     # 先放 2 头的斜率，再从 4 头序列里隔一个取
decode_alibi(2)   -> 每个 head 的距离是 [-2, -1, 0]，乘以 m_h
```

### 解题思路与正确性

head 数是 2 的幂时，斜率是从 $2^{-8/H}$ 开始的等比数列。不是 2 的幂时不能直接代公式：先取不超过 H 的最大 2 的幂 F，生成 F 个斜率；再生成 2F 头的序列，隔一个取一个，补上剩下的 H − F 个。这样补进来的斜率正好落在已有斜率之间。

偏置是 `key_pos - query_pos`，对可见位置非正，离得越远越负。未来位置必须单独置 $-\infty$，线性偏置只会让未来位置「比较负」，不会禁止它。decode 时把新 token 的位置设成 `cache_len`，key 长度设成 `cache_len + 1`，得到的就是 prefill 最后一行，所以两条路径的偏置一致。

### 完整参考实现（Python 3）

```python
import math

import torch


def alibi_slopes(n_heads):
    """返回 [H] 的 ALiBi 斜率；非 2 的幂按原论文参考代码的交错规则补齐。"""
    if type(n_heads) is not int or n_heads < 1:
        raise ValueError(f"n_heads must be a positive int, got {n_heads!r}")

    def power_of_two_slopes(n):
        start = 2 ** (-2 ** -(math.log2(n) - 3))  # = 2^(-8/n)
        return [start ** i for i in range(1, n + 1)]

    floor = 2 ** int(math.floor(math.log2(n_heads)))
    values = power_of_two_slopes(floor)
    if floor != n_heads:
        values += power_of_two_slopes(2 * floor)[::2][: n_heads - floor]
    return torch.tensor(values, dtype=torch.float32)


def alibi_score_bias(q_pos, s_len, slopes):
    """q_pos: [T]，slopes: [H] -> bias [1, H, T, S]；未来位置为 -inf。"""
    k_pos = torch.arange(s_len)
    distance = (k_pos[None, :] - q_pos[:, None]).float()  # [T, S]，j - i
    causal = k_pos[None, :] <= q_pos[:, None]             # [T, S]
    bias = slopes[:, None, None] * distance[None, :, :]   # [H, T, S]
    bias = bias.masked_fill(~causal[None, :, :], float("-inf"))
    return bias.unsqueeze(0)


def decode_alibi(cache_len, slopes):
    """单步 decode 的偏置 [1, H, 1, cache_len + 1]；新 token 的位置是 cache_len。"""
    q_pos = torch.tensor([cache_len])
    return alibi_score_bias(q_pos, cache_len + 1, slopes)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.allclose(alibi_slopes(3), torch.tensor([1 / 16, 1 / 256, 1 / 4]))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


# 非 2 的幂：先 2 头的斜率，再从 4 头序列隔一个取
assert torch.allclose(alibi_slopes(3), torch.tensor([1 / 16, 1 / 256, 1 / 4]))

# 8 头：1/2, 1/4, ..., 1/256
slopes = alibi_slopes(8)
assert torch.allclose(slopes, 2.0 ** (-torch.arange(1, 9)))

# 1 头：2^-8
assert torch.allclose(alibi_slopes(1), torch.tensor([1 / 256]))

# decode 的偏置等于 prefill 的最后一行，对角线（自己）为 0
prefill = alibi_score_bias(torch.arange(3), 3, slopes)
decode = decode_alibi(2, slopes)
assert prefill.shape == (1, 8, 3, 3)
assert decode.shape == (1, 8, 1, 3)
assert torch.equal(prefill[:, :, -1:], decode)
assert torch.all(decode[:, :, :, -1] == 0)

# 距离为 -2 的偏置是 -2 * m_h
assert torch.allclose(decode[0, :, 0, 0], -2 * slopes)

# 未来位置是 -inf
assert torch.isneginf(prefill[:, :, 0, 1:]).all()

# 非法 head 数
expect_value_error(alibi_slopes, 0)
expect_value_error(alibi_slopes, 2.0)
```

### 复杂度与追问

设 head 数为 H、query 长度为 T、key 长度为 S。斜率是 O(H)；偏置的时间和空间都是 O(HTS)。

- 追问「放到 GPU 上要注意什么」：`q_pos`、`k_pos` 和 `slopes` 必须在同一个 device 上，否则 broadcast 时报错。
- 追问「偏置要不要每步重算」：斜率固定，可以缓存；decode 每步只需要一行 `[1, H, 1, S]`，O(HS)。

## 题怎么来的

Press et al. 提出的 ALiBi 是 BLOOM、MPT 这类模型的位置方案：既没有位置 embedding，也没有 RoPE，而是把线性偏置直接加在注意力 logits 上。HuggingFace 实现岗和「手写 MHA」的 follow-up 会问斜率怎么来、逐 token 生成（decode）时距离怎么算。Llama 默认用 RoPE，见 `coding-rope`。除非面试官明确给了混合架构，不要在同一套 $q,k$ 上叠两种位置编码。

## 斜率乘相对距离

Head $h$ 的斜率是 $m_h>0$。Query 位置 $i$、key 位置 $j$，在因果成立（$j\le i$）时：

$$
\mathrm{score}_{h,i,j}=\frac{q_{h,i}^\top k_{h,j}}{\sqrt{D}}+m_h(j-i).
$$

因为 $j-i\le 0$，偏置非正，越远的 key 被压得越低。head 数是 2 的幂时，斜率是几何序列 $m_h=1/2^{h\cdot 8/H}$（$h=1,\ldots,H$），8 头就是 $1/2,1/4,\ldots,1/256$。不是 2 的幂时用上面实现里的交错补齐，HuggingFace 的实现也是同一规则。

偏置的形状要能和 scores `[B, H, T, S]` 广播。Prefill 时是 `[1, H, T, S]`，$T=S$，$i$ 和 $j$ 都是 `arange`。Decode 时 $T=1$，$j=0,\ldots,S-1$；如果 $S$ 已经包含新 token，query 位置就是 $i=S-1$，bias 形状 `[1, H, 1, S]`。不要拿 $i=0$ 去减 $j$，那样离得最近的 key 反而最负。

ALiBi 加在 scores 上，在 softmax 之前。它不改 $q,k$ 的内容，也不碰 $V$。

`cache_len` 和 RoPE 那题用同一约定，表示新 token 的绝对下标，见 `coding-rope-cache`。可以补两条单测：固定 $q,k$ 时，ALiBi 只改变 softmax 权重，$V$ 本身不变；距离相同的 $(i,j)$ 在 prefill 和 decode 下必须得到同一偏置。

## 外推，以及和 RoPE 的对比

ALiBi 的典型用法是训练时用短序列、测试时用长序列：偏置随距离线性变化，不像 RoPE 那样有 cos/sin 表，不存在超过 `max_seq` 越界的问题。远处的 key 在 softmax 里仍分到概率，只是很小，这和硬滑窗那种截断不同，见 `coding-swa-mask`。不过 BLOOM 的训练长度和推理长度仍要在评测里报清楚。

用 GQA / MQA 时，斜率按 query head 数生成，每个 query head 一个 $m_h$。KV head 被若干个 query head 共享，但 bias 加在 $QK^\top$ 的 head 维上，形状跟着 `[B, H_q, T, S]` 走。不要按 $H_{\mathrm{kv}}$ 生成一套更短的斜率再沿错误的轴 repeat，repeat 的规则见 `coding-gqa-repeat`。

## 追问

**为什么写 $m(j-i)$，而不是 $-m|i-j|$ 再另加因果 mask？**
在因果条件下两者只差一个符号约定，关键是 $j\le i$ 时偏置 $\le 0$。如果对未来位置也加上绝对值形式的偏置而忘了 mask，非法 key 仍会分到概率；如果符号写反，未来位置还会变成正数。
**decode 时 query 位置用 $S$ 还是 $S-1$？**
看这一步的 $K$ 有没有已经 concat 进去。concat 之后 $S_{\mathrm{new}}=S_{\mathrm{old}}+1$，query 位置是 $S_{\mathrm{new}}-1$，也就是 $S_{\mathrm{old}}$。
**能和 RoPE 同时用吗？**
公开的 BLOOM 不用 RoPE。叠两套位置信号需要训练上的依据，白板默认二选一。
**斜率要不要学？**
论文用的是固定几何序列，不进优化器。改成可学习参数会改变外推行为，那就不是原版 ALiBi 了。

## 相关题

- [[coding-rope]]：RoPE 旋转 $q,k$ 而不是改 scores，decode 位置同样取 cache 长度，可以对照两种写法。
- [[meta-llama-rope]]：RoPE 为什么难外推、NTK / YaRN 在拧什么，和 ALiBi 靠线性偏置外推的思路对照。

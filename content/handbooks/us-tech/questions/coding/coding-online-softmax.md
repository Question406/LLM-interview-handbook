---
id: coding-online-softmax
section: coding
order: 15
level: S
title: 白板：FlashAttention 的 online softmax，两遍归约怎么写
quick: >-
  一遍扫描维护 running max 和 sumexp，最大值变大时把旧和换到新基准，第二遍即可写 softmax。attention 还同步
  rescale 已累加的输出，最后 normalization，不能让各 tile 独立 softmax。
tags:
  - 完整编程练习
  - Coding
  - Softmax
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
  - title: Online normalizer calculation for softmax
    url: 'https://arxiv.org/abs/1805.02867'
    type: primary
  - title: >-
      FlashAttention-2 — Faster Attention with Better Parallelism and Work
      Partitioning
    url: 'https://arxiv.org/abs/2307.08691'
    type: primary
---

## 题目描述

实现只能分块读取分数或 key/value 的数值稳定 normalization 接口。先为非空分数向量返回足以重建 softmax 的统计量，再提供使用这些统计量的 normalization 接口，以及单 query 的分块 attention 接口。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `online_stats(x) -> (m, ell)`：一遍扫描非空的有限向量 `x`，返回全局最大值 $m$ 和 $\ell=\sum_j e^{x_j-m}$。
- `softmax_from_stats(x, m, ell)`：用上面的统计量做第二遍，返回 softmax 概率。
- `online_attn_row(q, k, v, scale, tile=16)`：单个 query 的 attention，`q` 是 `[D]`，`k`、`v` 是 `[S, D]`。按每块 `tile` 个 key 扫描，不物化长度为 $S$ 的完整分数向量，返回 `softmax(k @ q * scale) @ v`，形状 `[D]`。假定 `S >= 1`、`tile >= 1`。
- 分数都是有限值，不处理整行被 mask 成 $-\infty$ 的情况。

### 示例

```text
online_stats([1000, 1000])                 -> m = 1000, ell = 2
softmax_from_stats([1000, 1000], 1000, 2)  -> [0.5, 0.5]    # 不会因 exp(1000) 溢出
online_attn_row(q=[1], k=[[0],[0]], v=[[2],[4]], scale=1, tile=1) -> [3]
```

## 解题思路与参考答案

online softmax 把求 max 和 sumexp 合进一遍扫描，随后用全局统计量写出概率。扫描时保持 $\ell=\sum_{j\le i} e^{x_j-m}$，$m$ 是目前见过的最大值。新的最大值 $m'$ 出现时，旧的和要乘 $e^{m-m'}$ 换到新标尺，再加上新元素的 $e^{x_i-m'}$。扫完后 $m$ 和 $\ell$ 就是全局统计量。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + NumPy，CPU 上用 float64 验证，没有验证 GPU kernel 或性能。

### 题面、接口与约束

- `online_stats(x) -> (m, ell)`：一遍扫描非空的有限向量 `x`，返回全局最大值 $m$ 和 $\ell=\sum_j e^{x_j-m}$。空输入抛 `ValueError`。
- `softmax_from_stats(x, m, ell)`：用上面的统计量做第二遍，返回 softmax 概率。
- `online_attn_row(q, k, v, scale, tile=16)`：单个 query 的 attention，`q` 是 `[D]`，`k`、`v` 是 `[S, D]`。按每块 `tile` 个 key 扫描，不物化长度为 $S$ 的完整分数向量，返回 `softmax(k @ q * scale) @ v`，形状 `[D]`。$S=0$ 或 `tile < 1` 时抛 `ValueError`。
- 分数都是有限值，不处理整行被 mask 成 $-\infty$ 的情况（见下文「Tile 上不能各 self-normalization」）。

### 输入输出示例

```text
online_stats([1000, 1000])                 -> m = 1000, ell = 2
softmax_from_stats([1000, 1000], 1000, 2)  -> [0.5, 0.5]    # 不会因 exp(1000) 溢出
online_attn_row(q, k, v, 0.5, tile=3)      -> 与 softmax(k @ q / 2) @ v 一致，tile 取 1、3、20 都一样
```

### 解题思路与正确性

attention 里还要维护未 normalization 的输出 $O=\sum_j e^{s_j-m}v_j$。它和 $\ell$ 用同一个 rescale 系数 $\alpha=e^{m-m'}$：每来一块 key，先把旧的 $O$ 和 $\ell$ 乘 $\alpha$，再加上本块的贡献。最后返回 $O/\ell$。第一块时 $m=-\infty$，$\alpha=0$，旧值本来就是 0，不需要特判。

### 完整参考实现（Python 3）

```python
import numpy as np


def online_stats(x):
    """一遍扫描求 (max, sum(exp(x - max)))；x 非空且有限。"""
    if len(x) == 0:
        raise ValueError("empty scores")
    running_max = -np.inf
    running_sum = 0.0
    for value in np.asarray(x, dtype=np.float64):
        new_max = max(running_max, value)
        running_sum = running_sum * np.exp(running_max - new_max) + np.exp(
            value - new_max
        )
        running_max = new_max
    return running_max, running_sum


def softmax_from_stats(x, m, ell):
    """第二遍：用全局 max 和 sumexp normalization。"""
    return np.exp(np.asarray(x, dtype=np.float64) - m) / ell


def online_attn_row(q, k, v, scale, tile=16):
    """单个 query 的分块 attention。q: [D]，k / v: [S, D]，返回 [D]。

    按 key 块扫描，running max 变化时同时 rescale 已累加的输出和 sumexp。
    """
    seq_len, head_dim = k.shape
    if seq_len == 0:
        raise ValueError("need at least one key")
    if tile < 1:
        raise ValueError(f"tile must be >= 1, got {tile}")
    running_max = -np.inf
    running_sum = 0.0
    output = np.zeros(head_dim, dtype=np.float64)
    for start in range(0, seq_len, tile):
        scores = (k[start : start + tile] @ q) * scale  # [tile]
        new_max = max(running_max, float(np.max(scores)))
        weights = np.exp(scores - new_max)
        alpha = np.exp(running_max - new_max)  # 旧标尺 -> 新标尺
        output = output * alpha + weights @ v[start : start + tile]
        running_sum = running_sum * alpha + float(weights.sum())
        running_max = new_max
    return output / running_sum
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert m == 1000` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_error(error_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


# 大数值不溢出：两个 1000 的 softmax 是 [0.5, 0.5]
m, ell = online_stats([1000.0, 1000.0])
assert m == 1000
assert ell == 2
assert np.allclose(softmax_from_stats([1000.0, 1000.0], m, ell), [0.5, 0.5])

# 与两遍写法的统计量一致
rng = np.random.default_rng(4)
x = rng.normal(size=11) * 5
m, ell = online_stats(x)
assert m == x.max()
assert np.isclose(ell, np.exp(x - x.max()).sum())
assert np.isclose(softmax_from_stats(x, m, ell).sum(), 1.0)

# 分块 attention 与完整 softmax attention 一致，与 tile 大小无关
q = rng.normal(size=4)
k = rng.normal(size=(7, 4))
v = rng.normal(size=(7, 4))
scores = k @ q / 2
probs = np.exp(scores - scores.max())
probs /= probs.sum()
for tile in (1, 3, 7, 20):
    assert np.allclose(online_attn_row(q, k, v, 0.5, tile), probs @ v)

# 非法输入
expect_error(ValueError, online_stats, [])
expect_error(ValueError, online_attn_row, q, k[:0], v[:0], 0.5)
expect_error(ValueError, online_attn_row, q, k, v, 0.5, tile=0)
```

### 复杂度与追问

设 key 数为 $S$、头维为 $D$。`online_attn_row` 时间 $O(SD)$；额外空间是 $O(D)$ 的输出累加器，加上当前块 $O(\text{tile}\cdot D)$ 的工作区。如果要的是 softmax 概率本身，输出仍然要 $O(S)$。

- 追问「多个 query 怎么办」：每一行各自维护 $(m,\ell,O)$，FlashAttention 外层沿 $K,V$ 块走，内层对一块 query 行同时更新。
- 追问「fp16 下怎么放精度」：running sumexp 和 rescale 系数放 fp32，见 `coding-softmax-stable`。

## 题怎么来的

NVIDIA / OpenAI 的 kernel 白板不考你背 fused kernel 的名字，而是让你把 softmax 的归约拆开。Dao 等人的 FlashAttention 把 Milakov 的 online softmax 嵌进 SRAM tiling，`[T, S]` 的分数矩阵从不写回 HBM。IO 开销分析见 `nvidia-flash-attn`；稳定但物化整张表的写法见 `coding-softmax-stable`。这道题要讲清两件事：为什么不能对每个 K 块单独做 softmax，以及 running max 变了以后旧的输出怎么乘回去。

## 三遍、两遍、online

对一行 logits $x\in\mathbb{R}^{S}$：

$$
m=\max_j x_j,\quad
\ell=\sum_j e^{x_j-m},\quad
p_j=e^{x_j-m}/\ell.
$$

最朴素的写法扫三遍：先求 max，再求 sumexp，再逐个相除。online 的做法是在一遍里流式维护 $(m,\ell)$：

$$
m_i=\max(m_{i-1},x_i),\quad
\ell_i=e^{m_{i-1}-m_i}\ell_{i-1}+e^{x_i-m_i}.
$$

扫完时 $m_S,\ell_S$ 就是全局 max 和 sumexp，和分开算的结果在数学上相等。于是第二遍直接写出 $p_i=\exp(x_i-m_S)/\ell_S$，总共两遍。

attention 连 $p$ 都不需要物化：每块的 $p$ 直接乘上对应的 $V$ 累加进输出；max 更新时，把已有输出乘上 $e^{m_{\mathrm{old}}-m_{\mathrm{new}}}$。单测时，`online_stats` 要对上 `x.max()` 和 `exp(x - m).sum()`，`online_attn_row` 要对上 `softmax(scale * K q) @ V`。对不上，通常是某处漏乘了 rescale 系数。

## Tile 上不能各 self-normalization

FlashAttention 的外层沿 $K,V$ 块走。块 $j$ 上局部的 $\mathrm{softmax}(Q K_j^\top)$，分母只是这一块的和，不是全局的 $\ell$，各块的权重彼此对不上，结果就不是精确 attention。必须在每一行上保留 $(m,\ell,O)$，新块只提供增量。

因果 mask 在 tile 内填 $-\infty$。如果一整行都是 $-\infty$，$\ell=0$，$O/\ell$ 会是 NaN，所以要跳过这种行，或者先检查有没有有限值。

decode 时 $T_q=1$，分数只是 `[1, S]`。online 省下的是把长度为 $S$ 的分数写回 HBM 的开销，但实际耗时大多花在读 KV cache 上，这和 prefill 时 $T^2$ 规模的 IO 不是一回事。白板上先把递推写对，再提这一点。

## 追问

**和减 max 的稳定 softmax 是什么关系？**
每一步减的是当前的 running max，而不是最终的全局 max；用 $e^{m_{\mathrm{old}}-m_{\mathrm{new}}}$ 把旧的 $\ell$ 和 $O$ 换到新标尺上，效果等价于从头减全局 max。
**为什么 FlashAttention 仍然有 normalization 这一步？**
统计量 $m,\ell$ 一遍就能扫完，但写出 normalization 后的 $P$ 仍要再访问 $x$。attention 把这「第二遍」融进了 $PV$ 的累加里，训练时反向再重算一次。
**块内先 softmax、再把各块加权平均，能凑合吗？**
不能。那是错误的 normalization，不算 FlashAttention 的近似。

## 相关题

- [[coding-softmax-stable]]：先把单行减全局 max 的稳定 softmax 写对，这张把它改成流式的 running max。
- [[coding-fused-ce]]：同一套 running $(m,\ell)$ 用在 vocabulary 维上，算 CE 时不物化完整 logits。
- [[coding-flash-decode]]：把这里串行扫 $K$ 块改成多段并行，各段的 $(m,\ell,O)$ 再按同一套 rescale 合并。
- [[nvidia-flash-decode]]：同一个 split-K 练习，从 NVIDIA 角度对照训练核和 decode 核切的轴。
- [[openai-flash-decode]]：同一个 split-K 练习，OpenAI 问法侧重 decode 时并行度为什么不够、什么时候不必切。
- [[nvidia-flash-attn]]：本题递推放回 FlashAttention 里的 IO 分析，SRAM tiling 省了多少 HBM 流量，decode 为什么收益小。

---
id: coding-flash-decode
section: coding
order: 25
level: S
title: 白板：FlashDecoding 的 split-K，online softmax 怎么沿 KV 切开再合并
quick: >-
  Decode 时 $T=1$，FlashAttention 沿 $Q$ 并行吃不满 SM。把 $K,V$ 沿长度切成 $G$ 段，每段各自维护
  $(m,\ell,O)$，再按同一套 rescale 合并。单段先 softmax 再平均是错的。合并后 $O/\ell$ 才是精确注意力。
tags:
  - 完整编程练习
  - Coding
  - FlashDecoding
  - Softmax
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Flash-Decoding for long-context inference (Stanford CRFM)
    url: https://crfm.stanford.edu/2023/10/12/flashdecoding
    type: primary
  - title: Flash-Decoding (PyTorch Blog)
    url: https://pytorch.org/blog/flash-decoding/
    type: secondary
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention with IO-Awareness
    url: https://arxiv.org/abs/2205.14135
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + NumPy，在 CPU 上做数值验证，没有验证 GPU、多卡或性能。

### 题面、接口与约束

- `split_stats(q, k, v, scale) -> (m, ell, O)`：对一段 KV 算出最大分数 `m`、指数和 `ell` 和未归一化的加权和 `O`。`q` 是 `[D]`，`k`、`v` 是 `[S_g, D]`，`S_g >= 1`。
- `merge_mlo(stats) -> [D]`：把各段统计按全局 max 重新缩放后合并，返回归一化输出；`ell == 0` 的段跳过，全部为空时抛 `ValueError`。
- `flash_decode(q, k, v, scale, n_split=4) -> [D]`：把长度 `S` 的 KV 切成 `n_split` 段，结果必须等于 `softmax(scale * K q) @ V`。
- 约束：`S >= 1`，`n_split >= 1`，否则抛 `ValueError`。`n_split` 可以大于 `S`，多出来的空段要安全跳过，不能对空数组取 max。

### 输入输出示例

```text
S = 7, D = 4, scale = 0.5
flash_decode(q, k, v, 0.5, n_split=3)   -> 等于 softmax(0.5 * k @ q) @ v
flash_decode(q, k, v, 0.5, n_split=20)  -> 同上；20 段里有 13 段为空，合并时跳过
flash_decode(q, k[:1], v[:1], 0.5, 8)   -> v[0]
flash_decode(q, k[:0], v[:0], 0.5, 2)   -> ValueError
```

### 解题思路与正确性

每段只保存三样东西：段内最大分数 $m_g$、指数和 $\ell_g$、没有除以 $\ell_g$ 的加权和 $O_g$。合并时取全局最大值 $m$，把每段乘上 $e^{m_g-m}$ 再相加，最后用总的 $O$ 除以总的 $\ell$。这样每个 token 的权重都变成 $e^{s_j-m}/\ell$，和一次性对整段做 softmax 完全一样。

不能先在段内做 softmax 再平均：每段用的是自己的分母，平均以后权重和全局 softmax 对不上。

空段没有分数，记成 $m_g=-\infty$、$\ell_g=0$，合并前过滤掉。否则全局 max 可能是 $-\infty$，算 $e^{-\infty-(-\infty)}$ 会得到 NaN。

### 完整参考实现（Python 3）

```python
import numpy as np


def split_stats(q, k, v, scale):
    """一段 KV 的 online softmax 统计 (m, ell, O)，O 未除以 ell。

    q: [D]，k, v: [S_g, D]，S_g >= 1。
    """
    scores = (k @ q).astype(np.float64) * scale   # [S_g]
    m = float(np.max(scores))
    weights = np.exp(scores - m)                  # [S_g]，每项在 (0, 1]
    ell = float(weights.sum())
    out = weights @ v.astype(np.float64)          # [D]，未归一化
    return m, ell, out


def merge_mlo(stats):
    """把各段的 (m, ell, O) 按全局 max 重新缩放后相加，返回归一化输出 [D]。

    ell == 0 的段（空段或整段被 mask）直接跳过。
    """
    valid = [(m, ell, out) for m, ell, out in stats if ell > 0 and np.isfinite(m)]
    if not valid:
        raise ValueError("all splits are empty, nothing to attend to")
    global_max = max(m for m, _, _ in valid)
    total_ell = 0.0
    total_out = 0.0
    for m, ell, out in valid:
        factor = np.exp(m - global_max)   # (0, 1]
        total_ell += factor * ell
        total_out = total_out + factor * out
    return total_out / total_ell


def flash_decode(q, k, v, scale, n_split=4):
    """把长度 S 的 KV 切成 n_split 段分别求统计，再合并成精确的 softmax(scale * K q) @ V。

    q: [D]，k, v: [S, D]。n_split 可以大于 S，多出来的段是空段。
    """
    seq_len, dim = k.shape
    if seq_len == 0:
        raise ValueError("KV cache is empty")
    if n_split < 1:
        raise ValueError(f"n_split must be >= 1, got {n_split}")
    cuts = np.linspace(0, seq_len, n_split + 1, dtype=int)
    stats = []
    for start, end in zip(cuts[:-1], cuts[1:]):
        if start == end:
            stats.append((-np.inf, 0.0, np.zeros(dim)))
        else:
            stats.append(split_stats(q, k[start:end], v[start:end], scale))
    return merge_mlo(stats)
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


def reference_attention(q, k, v, scale):
    scores = (k @ q) * scale
    weights = np.exp(scores - scores.max())
    weights /= weights.sum()
    return weights @ v


rng = np.random.default_rng(2)
q = rng.normal(size=4)
k = rng.normal(size=(7, 4))
v = rng.normal(size=(7, 4))
expected = reference_attention(q, k, v, 0.5)

# 不切、切成不等长的 3 段、段数远大于 S（大量空段）都等于直接 attention
for n_split in (1, 3, 7, 20):
    assert np.allclose(flash_decode(q, k, v, 0.5, n_split), expected)

# 只有一个 token 时输出就是那一行 V
assert np.allclose(flash_decode(q, k[:1], v[:1], 0.5, 8), v[0])

# 分数很大时也不溢出：每段先减自己的 max
big_q = q * 1000.0
assert np.allclose(flash_decode(big_q, k, v, 0.5, 3), reference_attention(big_q, k, v, 0.5))

# 常见错法：每段先归一化再平均，结果不对
per_split = [reference_attention(q, k[a:b], v[a:b], 0.5) for a, b in ((0, 2), (2, 7))]
assert not np.allclose(np.mean(per_split, axis=0), expected)

# 空 KV、n_split < 1、所有段都为空都报错
expect_value_error(flash_decode, q, k[:0], v[:0], 0.5, 2)
expect_value_error(flash_decode, q, k, v, 0.5, 0)
expect_value_error(merge_mlo, [(-np.inf, 0.0, np.zeros(4))])
```

### 复杂度与追问

设 KV 长度为 $S$，head 维度为 $D$，段数为 $G$（即 `n_split`）。算术量是 $O(SD)$，和不切一样；额外保存 $G$ 份统计，空间 $O(GD)$，合并是 $O(GD)$。这是 CPU 上的数值模拟，不能据此报 GPU 加速比。

- 追问「$G$ 怎么选」：让 batch × head × $G$ 大致盖住 SM 数，再看 $S$。$G$ 太大时部分结果变多、归约变重，每段也短到填不满一个 tile。
- 追问「如果 $O_g$ 已经除过 $\ell_g$」：合并改成 $O=\sum_g e^{m_g-m}\ell_g O_g$，最后再除以 $\ell$。两种约定不要混用。

## 题怎么来的

NVIDIA / CUDA 岗问完 `nvidia-flash-attn` 之后，常接着问逐 token 生成（decode）。Prefill 时 $Q$ 的长度 $T$ 很大，FlashAttention 沿 $Q$ 切 tile 就能铺满 GPU。Decode 每步 $T=1$，并行度只剩 batch $\times$ head；上下文一长，时间都花在扫 KV 上，SM 占用率掉下来。Dao 等人的 Flash-Decoding 多开了一条并行轴：沿 KV 长度做 split-K。白板上要讲清两件事：每段留下什么统计，以及怎样把它们合并成和单核 online softmax 一样的结果。单段内的递推见 `coding-online-softmax`。

## 每段留下 $(m,\ell,O)$，不要局部归一化

设 $q\in\mathbb{R}^{D}$，$K,V\in\mathbb{R}^{S\times D}$。把 $S$ 切成 $G$ 段，第 $g$ 段的分数是 $s^{(g)}=K^{(g)}q/\sqrt{D}$。段内照常做 online softmax，最后写出三样统计：

$$
m_g=\max_j s^{(g)}_j,\quad
\ell_g=\sum_j e^{s^{(g)}_j-m_g},\quad
O_g=\sum_j e^{s^{(g)}_j-m_g}\,V^{(g)}_j.
$$

$O_g$ 是还没除以 $\ell_g$ 的加权和，形状仍是 $[D]$（多头时是 $[B,H,D]$）。面试里最常见的误区是对每段先做 $\mathrm{softmax}$，再把 $G$ 个输出向量取平均。这样每段用的是各自的分母，得到的不是精确注意力。

合并和两个 tile 首尾相接用的是同一个公式，区别只是 $G$ 段可以同时算完，再一起归约：

$$
m=\max_g m_g,\quad
\ell=\sum_g e^{m_g-m}\ell_g,\quad
O=\sum_g e^{m_g-m}O_g,\quad
o=O/\ell.
$$

缩放因子 $e^{m_g-m}$ 落在 $(0,1]$，不会溢出。某段如果全被 mask 成 $-\infty$，就有 $m_g=-\infty$、$\ell_g=0$，合并时要跳过，否则会算出 $\exp(-\infty-(-\infty))=\text{NaN}$。所有段都空说明 mask 写错了，split 救不回来。因果 decode 里的 KV 全是已经生成的过去 token，分段只是切长度，不存在未来段。

单测时拿 `n_split=1` 和 `n_split=8` 的结果去对 `softmax(scale K q) @ V`。对不上，通常是某段提前除了 $\ell$，或者合并时漏乘了 $e^{m_g-m}$。

## 并行轴、IO 与 prefill 的区别

Split-K 换来的是占用率。每段只读自己那一截 $K,V$，产出的部分统计 $(m,\ell,O)$ 很小，最后做一次树形归约。HBM 上仍然要把整份 KV 读一遍，decode 的耗时依旧由带宽决定；收益来自更多 CTA 同时读，而不是读得更少。$G$ 太大时部分结果太多，归约变重，每段也可能短到填不满一个 SRAM tile。先把合并写对，再讨论 $G$ 的选择：它跟着 SM 数和 $S$ 走，不是越大越快。

统计量用 fp32 保存。段内 max 和跨段 max 的 rescale 都在 fp32 里做，和 `coding-softmax-stable` 是同一个原则。GQA 下 $K,V$ 仍是 `[B, H_{\mathrm{kv}}, S, D]`，split 沿 $S$ 切；沿 head 切开不叫 split-K。Paged KV 下每段还要先按 block table 做 gather，见 `coding-paged-table`。

Prefill 一般用不着 split-K，因为 $T$ 本身已经提供了足够的并行度。有人把 decode kernel 拿去跑 prefill，占用率看起来很好，但它的 $Q$ tile 访存模型和 FlashAttention-2 不一样，两者的加速比不要混在一起报。

## 追问

- **为什么不能每段先 softmax 再加权平均？** 各段的分母不是全局的 $\ell$，权重对不上。这不是对 FlashAttention 的近似，而是错的。
- **如果 $O_g$ 已经除过 $\ell_g$，怎么合并？** 用 $O\leftarrow\sum_g e^{m_g-m}\ell_g O_g$，最后再除以 $\ell$。它和未归一化版本差一个 $\ell_g$ 因子，两种约定不要混用。
- **某一段全是 $-\infty$ 怎么办？** 这段 $\ell_g=0$，合并时跳过。所有段都空则 $\ell=0$，那是 mask 写错了，不是 split 能解决的问题。
- **和顺序 online softmax 扫 $K$ 块相比有什么不同？** 数学上是同一套 rescale。Flash-Decoding 把「一个 CTA 串行扫所有块」改成「多个 CTA 并行算，再归约」，目的是在 $T=1$ 时提高占用率。

## 相关题

- [[nvidia-flash-decode]]：练习代码和这张完全相同，正文从 NVIDIA 角度对照训练用 FlashAttention 的切分轴和 CUDA Graph。
- [[openai-flash-decode]]：练习代码和这张完全相同，正文侧重什么时候 $BH$ 已经够大、不必 split，以及和 split-K GEMM 的类比。
- [[coding-online-softmax]]：$(m,\ell,O)$ 的 rescale 规则来自那里的顺序 online softmax，这张把它改成并行再合并。
- [[nvidia-flash-attn]]：本题的前一问，讲 prefill 时 FlashAttention 省的 HBM IO，以及为什么 decode 时这笔红利变小。

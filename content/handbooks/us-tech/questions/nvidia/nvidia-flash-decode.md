---
id: nvidia-flash-decode
section: nvidia
order: 21
level: S
title: NVIDIA：FlashDecoding split-K，和训练用 FlashAttention 差在哪
quick: >-
  我会在小 batch、长上下文 decode 时沿 KV 长度做 split-K，让更多 CTA 并行，再用各段 softmax 统计精确合并。训练用
  FlashAttention 主要沿 query 行铺开，decode 的 $Q$ 只有一行，直接沿用训练网格容易填不满 SM。
tags:
  - 完整编程练习
  - NVIDIA
  - FlashDecoding
  - Split-K
  - CUDA
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: Flash-Decoding for long-context inference
    url: 'https://crfm.stanford.edu/2023/10/12/flashdecoding.html'
    type: primary
  - title: Flash-Decoding — PyTorch Blog
    url: 'https://pytorch.org/blog/flash-decoding/'
    type: secondary
  - title: >-
      FlashAttention — Fast and Memory-Efficient Exact Attention with
      IO-Awareness
    url: 'https://arxiv.org/abs/2205.14135'
    type: primary
  - title: >-
      FlashAttention-2 — Faster Attention with Better Parallelism and Work
      Partitioning
    url: 'https://arxiv.org/abs/2307.08691'
    type: primary
---

## 题目描述

实现单 query 的分段 attention 统计及合并，模拟 Flash Decode 的输出。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`split_stats(q,k,v,scale)` 输入 q `[D]`、k/v `[Sg,D]`，返回 `(m,ell,O)`。分数定义为 `scale*(k@q)`；m 为段内最大分数，ell 为 `sum(exp(score-m))`，O 为以相同指数权重对 v 求和的未 normalization 向量。

`merge_mlo(stats)` 返回 `[D]` 输出，必须等于将各段合并后做一次完整 softmax attention 的结果；ell=0 的空段不贡献，至少有一段非空。`flash_decode(q,k,v,scale,n_split=4)` 输入完整 k/v `[S,D]`，返回相同输出，S>=1、`n_split`>=1；`n_split` 大于 S 时允许空段。要求对大幅值分数仍保持数值稳定。

### 示例

```text
q=[0], k=[[0],[0],[0]], v=[[1],[2],[6]], scale=1。
flash_decode 在 n_split=2 或 5 时均返回 [3]。
若仅有一个 key/value，输出等于该 value。
```

## 解题思路与参考答案

FlashDecoding 会沿 KV 长度切分工作，再把各段统计合并成同一个 softmax 结果，用来解决单 query 并行度不足。例如 $B=1$、$H=32$ 时，按 query 分配只有几十个 CTA，H100 的一百多个 SM 很多会闲着。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + NumPy，在 CPU 上做数值验证，没有验证 GPU、多卡或性能。

### 题面、接口与约束

- `split_stats(q, k, v, scale) -> (m, ell, O)`：对一段 KV 算出最大分数 `m`、指数和 `ell` 和未 normalization 的加权和 `O`。`q` 是 `[D]`，`k`、`v` 是 `[S_g, D]`，`S_g >= 1`。
- `merge_mlo(stats) -> [D]`：把各段统计按全局 max 重新缩放后合并，返回 normalization 输出；`ell == 0` 的段跳过，全部为空时抛 `ValueError`。
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
    scores = (k @ q).astype(np.float64) * scale  # [S_g]
    m = float(np.max(scores))
    weights = np.exp(scores - m)  # [S_g]，每项在 (0, 1]
    ell = float(weights.sum())
    out = weights @ v.astype(np.float64)  # [D]，未 normalization
    return m, ell, out


def merge_mlo(stats):
    """把各段的 (m, ell, O) 按全局 max 重新缩放后相加，返回 normalization 输出 [D]。

    ell == 0 的段（空段或整段被 mask）直接跳过。
    """
    valid = [(m, ell, out) for m, ell, out in stats if ell > 0 and np.isfinite(m)]
    if not valid:
        raise ValueError("all splits are empty, nothing to attend to")
    global_max = max(m for m, _, _ in valid)
    total_ell = 0.0
    total_out = 0.0
    for m, ell, out in valid:
        factor = np.exp(m - global_max)  # (0, 1]
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

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(flash_decode(q, k, v, 0.5, n_split), expected)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

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
assert np.allclose(
    flash_decode(big_q, k, v, 0.5, 3), reference_attention(big_q, k, v, 0.5)
)

# 常见错法：每段先 normalization 再平均，结果不对
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

NVIDIA CUDA / LLM serving 岗问完 `nvidia-flash-attn` 后，常会补一句：那逐 token 生成（decode）呢？Tri Dao、Haziza 等人 2023 年的 Flash-Decoding 博客给出了答案：再加一维并行，沿 KV 的序列长度切。xFormers 的 dispatcher、FlashAttention 2.2+、TensorRT-LLM 的 generation attention 都是同一个思路。回答时可以先画训练核的网格，再画 split-K 的网格。比较时要说清楚新增的并行维如何提高 occupancy。

## 训练核：沿 $Q$ 铺开，瓶颈是 $[T,T]$ 的 IO

标准 attention 会物化 $S=QK^{\top}$，形状 $[T,T]$，HBM 读写是 $\Theta(T^2)$。FlashAttention 把 $K,V$ 切成宽 $B_c$ 的块、把 $Q$ 切成高 $B_r$ 的块，在 SRAM 里做 online softmax，HBM 访问降到 $\Theta(T^2 d^2/M)$，其中 $M$ 是 SRAM 大小。网格主要沿 **query 行** 铺开，CTA 数大约是 $B\cdot H\cdot \lceil T/B_r\rceil$。训练和输入 prefill (即处理输入并建立 KV cache)时 $T$ 是几千到几万，这个 CTA 数足以喂满 A100/H100 的 SM。

FlashAttention-2 改的是 CTA **内部** 的 warp 分工。FA-1 用 sliced-K，多个 warp 各切一段 $K$，再在 shared memory 里归约；FA-2 改成切 $Q$，warp 之间的同步更少。这是 tile 内部的工作划分，并行轴仍然是 $Q$。backpropagation 还要重算 $S$，所以前向只存 $m,\ell$，不存完整的 $P$。这些都是训练核才有的开销，decode 没有。

## Decode 核：沿 $K$ 切，瓶颈是 occupancy

Decode 一步里，$Q$ 是 $[B, H, 1, d_h]$，历史 $K,V$ 长度为 $T$。分数只有 $[1,T]$，本来就不需要写回 HBM。IO 的主项是读 KV：

$$
\mathrm{bytes}\approx 2\cdot T\cdot H_{\mathrm{kv}}\cdot d_h\cdot b,
$$

其中 $b$ 是每个元素的字节数，系数 2 对应 $K$ 和 $V$。

如果还按训练核那样「一个 CTA 处理一整行 $Q$」，网格只剩 $B\cdot H$ 个 block。$B=1$、$H=32$ 时只有几十个 CTA，而 H100 有一百多个 SM，大半在空转。Nsight 上 theoretical occupancy 可能不差，但 **achieved** occupancy 很低，原因是根本没有足够的 block，见 `nvidia-occupancy`。

Flash-Decoding 的 split-K 分三步：

1. 把 $K,V$ 沿 $T$ 切成 $G$ 段，每段大约 $T/G$ 个 token。
2. $G$ 个 CTA 并行，各自在自己那段上跑 FlashAttention 式的 online softmax，写出一份段内已 normalization 的部分输出 $O^{(g)}$，外加一个标量 $\mathrm{lse}^{(g)}=\log\sum_j e^{s^{(g)}_j}$。博客特别强调，每个 split 每行只多写这一个标量。
3. 第二个 kernel 做归约，用各段的 lse 稳定地加权合并：

$$
\mathrm{lse}=\log\sum_g e^{\mathrm{lse}^{(g)}},\quad
O=\sum_g e^{\mathrm{lse}^{(g)}-\mathrm{lse}}\,O^{(g)}.
$$

实现上先减去 $\max_g \mathrm{lse}^{(g)}$ 再求指数，避免溢出。上面的练习代码用的是等价的另一种约定：每段存 $(m_g,\ell_g)$ 和未 normalization 的 $O_g$，有 $\mathrm{lse}^{(g)}=m_g+\log\ell_g$。

这里 online softmax 用了两层：段内一层（和 FA 一样），段间再一层。结果仍是精确 attention，只是求和顺序变了。$G$ 太大时归约 kernel 和额外写回变得明显，tile 也变窄；$G$ 太小又填不满 SM。经验是让 $B\cdot H\cdot G$ 至少盖住 SM 数，再根据 $T$ 调整。Paged 布局下每段还要按 block table 做 gather，见 `nvidia-paged-kv`。

xFormers 的 dispatcher 会按问题尺寸在 FA 和 Flash-Decoding 之间切换：$T$ 短、$B$ 大时不必 split，$T$ 长、$B$ 小才切。面试时不要说「decode 一律用 split-K」。

## 和训练核对照

| | 训练 / prefill FA | FlashDecoding |
|---|---|---|
| $Q$ 长度 | $T$，很大 | $1$ |
| 并行轴 | query tile | KV split |
| 主要瓶颈 | 不写出 $[T,T]$ | 填满 SM、读 KV |
| 反向 | 重算 + 存统计 | 没有 |
| 额外同步 | tile 内 warp 之间 | split 之间的 lse 归约 |

GQA 只减少 $H_{\mathrm{kv}}$，query head 数不变，$B\cdot H$ 可能够、也可能不够，长上下文下通常仍需要 split。Hopper 上还可以叠加 TMA 和 warp specialization，那属于实现层面，见 `nvidia-ws-decode`；算法上的区别仍然只是多了这一维并行。

FA-2 的 sliced-K 调整发生在 CTA 内部，目的是减少 warp 同步；Flash-Decoding 的 split-K 发生在 CTA 之间，用来增加 decode 的并行度。这两个层级要分清。

## 追问

**$G=1$ 是什么情况？**
退回到一个 CTA 处理整段 KV，小 batch、长上下文时 SM 会闲着。$T$ 短时反而可能更快，因为少一次合并。

**和 FlashAttention 的 sliced-K 什么关系？**
FA-1 在 CTA 内切 $K$，需要 shared memory 同步；FA-2 改成切 $Q$。FlashDecoding 的 split 发生在 CTA 之间，必须把部分结果写到 HBM，再合并。

**数值上要注意什么？**
段间合并必须走 log-sum-exp，不能把 $G$ 份 softmax 输出直接平均。$m$ 是 fp16 时，$\ell$ 也要用 fp32 累加。

**CUDA Graph 还能录吗？**
$G$ 随 $T$ 变化，形状不固定。常见做法是把 split 数 pad 到几个固定档位，或者只对 decode 步捕获，见 `nvidia-cuda-graph`。

## 相关题

- [[openai-flash-decode]]：同一题的 OpenAI 问法，练习代码完全相同；正文侧重何时 $BH$ 已够大不必切，以及和 split-K GEMM 的类比，没有训练核网格对照。
- [[coding-flash-decode]]：同一份练习代码的白板版，正文只讲每段留什么统计、怎么合并，不涉及 GPU 网格。
- [[nvidia-flash-attn]]：本题的前一问，训练和 prefill 时 FlashAttention 的 IO 分析，以及 decode 为什么收益不同。
- [[coding-online-softmax]]：段间合并用的 $(m,\ell,O)$ rescale 来自顺序的 online softmax，那张先把串行版写对。

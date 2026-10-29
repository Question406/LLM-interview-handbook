---
id: openai-flash-decode
section: openai
order: 31
level: S
title: OpenAI：FlashDecoding 为什么沿 KV 长度做 split-K，decode 时和 FlashAttention 差在哪
quick: >-
  decode 每步只有一个 query，batch 和 head 太少时难以占满 GPU，FlashDecoding 就沿 KV 长度再切一维并行。各段保存
  softmax 统计，用 log-sum-exp 精确合并；$BH$ 已够大时不切，避免额外归约开销。
tags:
  - 完整编程练习
  - OpenAI
  - FlashDecoding
  - Inference
  - CUDA
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Flash-Decoding for long-context inference (Stanford CRFM)
    url: 'https://crfm.stanford.edu/2023/10/12/flashdecoding.html'
    type: primary
  - title: Flash-Decoding (PyTorch Blog)
    url: 'https://pytorch.org/blog/flash-decoding/'
    type: primary
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention
    url: 'https://arxiv.org/abs/2205.14135'
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: >-
      https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 题目描述

实现单 query 对分段 KV 的 attention 统计及合并。长序列被分成任意数量的片段后，normalization 结果必须与完整 attention 一致。

以下为手册重构练习约定。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `split_stats(q,k,v,scale) -> (m,ell,O)`：q 是 `[D]`，k/v 是 `[Sg,D]`、Sg>=1。令分数 `s_i=scale*dot(k_i,q)`，返回 `m=max(s)`、`ell=sum(exp(s-m))` 和 `[D]` 的 `O=sum(exp(s_i-m)*v_i)`，O 尚未 normalization。
- `merge_mlo(stats) -> [D]` 接收上述统计三元组，返回所有分段合起来的 attention 输出。允许 ell 为 0 的空段，且至少有一个非空段。
- `flash_decode(q,k,v,scale,n_split=4) -> [D]` 中 k/v 是 `[S,D]`，S>=1，`n_split`>=1，可以大于 S。结果必须等于 `softmax(scale * (k @ q)) @ v`；空分段不影响结果。输入为有限浮点张量，D>=1。

### 输入输出示例

```text
q=[0], k=[[1],[2],[3]], v=[[2],[4],[6]], scale=1
flash_decode(q,k,v,1,n_split=2) -> [4]
flash_decode(q,k,v,1,n_split=5) -> [4]
split_stats([0],[[1],[2]],[[2],[4]],1) -> (0,2,[6])
```

## 解题思路与参考答案

FlashDecoding 通过沿 KV 长度切段，补足单 token decode 的并行度。比如 $B=1$、$H=32$，A100 有 108 个 SM，只沿 batch 和 head 发 CTA 就会有大量 SM 空闲；让多个 CTA 分段读同一个 query 的 KV，再合并结果，才可能把带宽用起来。

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

分段后保存段内最大分数 $m_g$、指数和 $\ell_g$，以及未除以 $\ell_g$ 的加权和 $O_g$，就足够还原全局结果。合并时取全局最大值 $m$，把每段乘上 $e^{m_g-m}$ 再相加，最后用总的 $O$ 除以总的 $\ell$。这样每个 token 的权重都变成 $e^{s_j-m}/\ell$，和一次性对整段做 softmax 完全一样。

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

Flash-Decoding 是 Dao、Haziza、Massa、Sizov 公开的推理 kernel。它接着 `openai-prefill-decode` 讨论 decode 的占用率：FlashAttention 已经避免物化 $[T,T]$，但单 query 时仍有其他瓶颈。片上 softmax 推导可对照 `google-flash-attention`、`nvidia-flash-attn`、`coding-online-softmax`。

## Decode 的并行度不够

FlashAttention 的外层并行是 batch、head 和 query tile。输入 prefill (即处理输入并建立 KV cache)时 $T_q$ 上千，每个 query 块都能占一个 CTA，HBM 往返被 tile 摊掉。

Decode 一步里，$Q$ 是 `[B, H, 1, D]`，$K,V$ 是 `[B, H_{\mathrm{kv}}, T, D]`。分数只有 `[1, T]`，没有 $[T,T]$ 可省，时间主要花在把整段 KV 从 HBM 读进来。更麻烦的是能发起 load 的 CTA 太少：并行度大约是 $B\cdot H$（GQA 时是 $B\cdot H_q$，但 KV 头更少）。$B=1$、$H=32$ 时，A100 的 108 个 SM 大部分闲着，带宽打不满。算术强度的公式没变，问题出在 occupancy。

所以 decode 时直接套用 prefill 的 FlashAttention，加速通常很小。GQA 和量化 cache 减少的是每步要读的字节，见 `google-gqa-mqa`；FlashDecoding 解决的是读这些字节时 SM 闲着的问题。两者互不冲突，可以叠加。

## Split-K：沿 KV 切开，再用 LSE 合并

Flash-Decoding 多加了一个并行轴：把长度为 $T$ 的 $K,V$ 切成 $S$ 段。每段对同一个 $q$ 跑一块 FlashAttention，写出段内 normalization 的局部输出 $O_s$，以及该段的 log-sum-exp $\ell_s=\log\sum\exp(q k^\top/\sqrt{d})$。然后做一次小规模归约：

$$
\ell=\log\sum_{s=1}^{S}e^{\ell_s},\qquad
O=\sum_{s=1}^{S}e^{\ell_s-\ell}\,O_s.
$$

实现时先减去 $\max_s \ell_s$ 再求指数，避免溢出。这和 online softmax 跨块 rescale 是同一套代数，结果是精确 attention，不是近似。练习代码用的是等价约定：每段存最大值 $m$、指数和 $\ell$（不取对数）和未 normalization 的 $O$，两者的关系是 $\ell_s=m+\log\ell$。

切完以后 CTA 数大约是 $B\cdot H\cdot S$，只要 $T$ 够长就能把 SM 喂饱。博客报告过长序列上最高约 8 倍的生成加速；这个数字随 GPU、头数以及原本的 $BH$ 是否已经够大而变化，面试时讲趋势，不要说成保证的指标。

什么时候不切：$BH$ 已经大于 SM 数时，`num_splits=1`。这时硬切成 $S=8$ 只会多一次同步和几次额外的 $O_s$ 写回，反而更慢。FlashAttention-2 论文也讨论过 split-K 带来的多余同步；decode、长上下文、小 batch 才是这条路径的适用场景。$S$ 太大时每段只有 $T/S$ 个 token，tile 效率下降，和 prefill 块切得太小是同一类问题。

因果 mask 在这里不是主要因素：decode 一步里没有未来的 key。Paged KV 只改变物理布局，split 仍按逻辑上的 $T$ 切，见 `openai-continuous-batching`。speculative decoding 的验证步 $T_q=\gamma\gt 1$，并行度回来了，通常不必 split-K，见 `openai-speculative-decoding`。

FlashDecoding 保持同一套精确 attention 公式，也没有改变 decode 原有的线性算术量。切分增加并行度的同时引入归约，所以大 batch 是否启用要根据 SM 占用率测量。

## 追问

**和 split-K GEMM 什么关系？**
思想相同：M 维太窄，就把 K 维切开来填满 SM，最后归约。区别是 attention 的归约必须带 LSE，不能把各段 $O_s$ 直接平均。
**GQA 的 $H_{\mathrm{kv}}$ 更少，还要不要 split？**
更需要。KV 头少意味着发起 load 的 CTA 更少，长 $T$ 下更打不满带宽。
**数值会和单核结果 bit exact 吗？**
不会。浮点归约顺序变了，会有 ulp 级的差异。回归测试应该检查 greedy decoding 出的 token 是否一致，不要用逐位比较。
**训练要不要用 FlashDecoding？**
不需要。训练时 $T_q$ 很大，prefill 式的 FlashAttention 才是主路径。FlashDecoding 是专门解决推理 decode 占用率的方案。

## 相关题

- [[nvidia-flash-decode]]：同一题的 NVIDIA 问法，练习代码完全相同；正文多了训练核与 decode 核的网格对照、FA-2 的 sliced-K 区别和 CUDA Graph。
- [[coding-flash-decode]]：同一份练习代码的白板版，只讲分段统计和合并的正确性，不讲何时切。
- [[nvidia-flash-attn]]：本题前置的 FlashAttention IO 分析，解释为什么 decode 时没有 $[T,T]$ 可省。
- [[coding-online-softmax]]：LSE 合并的 rescale 规则来自顺序的 online softmax，那张先把单 CTA 串行扫 $K$ 的版本写对。

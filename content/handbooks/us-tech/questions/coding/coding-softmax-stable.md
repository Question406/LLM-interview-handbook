---
id: coding-softmax-stable
section: coding
order: 1
level: S
title: 白板：数值稳定 softmax，为什么减 max，轴怎么选
quick: >-
  先确定哪些位置一起分配概率，再沿那一维逐行减 max、取 exp 并 normalization。分子分母同乘常数，分布保持不变，同时每行至少有一项指数是
  1，避免溢出和整行下溢；分类沿 vocabulary 维，attention 沿 key 维。
tags:
  - 完整编程练习
  - Coding
  - Softmax
  - OpenAI
  - Numerical Stability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: torch.nn.functional.softmax
    url: 'https://pytorch.org/docs/stable/generated/torch.nn.functional.softmax.html'
    type: primary
  - title: scaled_dot_product_attention
    url: >-
      https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
    type: primary
---

## 题目描述

用 NumPy 实现按指定轴 normalization 的 softmax 和 log-softmax，适用于数值较大的 logits 和合法的屏蔽项。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `softmax(x, axis=-1)`：沿指定轴做数值稳定的 softmax，输出形状和输入相同。
- `log_softmax(x, axis=-1)`：沿指定轴做数值稳定的 log-softmax。
- 输入里允许出现 `-inf`，表示这个位置被屏蔽，对应概率精确为 0。
- normalization 轴非空，每行至少有一个有限值，不含 NaN 或 `+inf`。
- 不修改输入；内部用 float64 计算。

### 输入输出示例

```text
softmax([1000, 1000])    -> [0.5, 0.5]
softmax([0, -inf])       -> [1, 0]
```

## 解题思路与参考答案

我会沿指定轴逐行减最大值，再取指数并除以该行指数和。比如 [1000, 1000] 先变成 [0, 0]，就能稳定得到 [0.5, 0.5]。代码还要明确全屏蔽行的处理；这份练习选择报错，避免对全 -inf 的行继续 normalization。


## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + NumPy，CPU 上验证。

### 题面、接口与约束

- `softmax(x, axis=-1)`：沿指定轴做数值稳定的 softmax，输出形状和输入相同。
- `log_softmax(x, axis=-1)`：沿指定轴做数值稳定的 log-softmax。
- 输入里允许出现 `-inf`，表示这个位置被屏蔽，对应概率精确为 0。
- 整行都是 `-inf`（全屏蔽）、含 NaN 或 `+inf`、normalization 的轴长度为 0 时，抛 `ValueError`。
- 不修改输入；内部用 float64 计算。

### 输入输出示例

```text
softmax([1000, 1000])    -> [0.5, 0.5]
softmax([0, -inf])       -> [1, 0]
softmax([-inf, -inf])    -> ValueError（全屏蔽行）
```

### 解题思路与正确性

沿 normalization 的那一维减去该行的最大值，再做 `exp` 和 normalization。分子分母同时乘了 $e^{-m}$，分布不变；每行最大的一项变成 $e^0=1$，其余都在 $(0,1]$，不会上溢，分母也至少是 1。

如果对整个 tensor 减同一个常数，在精确算术下分布同样不变，所以不能说它「数学上错了」。问题在数值上：logits 远小于全局最大值的那些行，所有指数可能一起下溢成 0，分母变成 0。逐行减 max 保证每行至少有一项等于 1。

全屏蔽行的最大值是 `-inf`，此时没有任何位置可以分到概率，这份练习选择直接报错。

### 完整参考实现（Python 3）

```python
import numpy as np


def _shift_by_row_max(x, axis):
    """检查输入，返回沿 axis 减去最大值后的 float64 副本（不修改输入）。"""
    x = np.asarray(x, dtype=np.float64)
    if x.shape[axis] == 0:
        raise ValueError(f"cannot normalize over empty axis {axis}")
    if np.isnan(x).any() or np.isposinf(x).any():
        raise ValueError("input contains NaN or +inf")
    row_max = x.max(axis=axis, keepdims=True)
    if np.isneginf(row_max).any():
        raise ValueError("a row is fully masked (all -inf)")
    return x - row_max


def softmax(x, axis=-1):
    """沿 axis 的数值稳定 softmax；-inf 表示屏蔽，输出形状与输入相同。"""
    shifted = _shift_by_row_max(x, axis)
    exps = np.exp(shifted)  # 每行最大的一项是 e^0 = 1，不会溢出
    return exps / exps.sum(axis=axis, keepdims=True)


def log_softmax(x, axis=-1):
    """沿 axis 的数值稳定 log-softmax：shifted - log(sum(exp(shifted)))。"""
    shifted = _shift_by_row_max(x, axis)
    return shifted - np.log(np.exp(shifted).sum(axis=axis, keepdims=True))
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(probs[0], probs[1])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} accepted invalid input {args}")


logits = np.array([[1000.0, 1001.0], [-1000.0, -999.0]])

# 大正数、大负数都不溢出；两行差值相同，所以分布相同
probs = softmax(logits)
assert np.allclose(probs[0], probs[1])

# 每行各自加一个常数，分布不变
assert np.allclose(softmax(logits + np.array([[500.0], [-700.0]])), probs)

# 示例：[1000, 1000] -> [0.5, 0.5]
assert np.allclose(softmax([1000.0, 1000.0]), [0.5, 0.5])

# axis=0 时沿列 normalization
assert np.allclose(softmax(logits, axis=0).sum(axis=0), 1)

# log_softmax 和 softmax 一致
assert np.allclose(np.exp(log_softmax(logits)), probs)

# -inf 表示屏蔽，对应概率精确为 0
assert np.array_equal(softmax([0.0, -np.inf]), [1.0, 0.0])

# 不修改输入
original = logits.copy()
softmax(logits)
log_softmax(logits)
assert np.array_equal(logits, original)

# 非法输入：全屏蔽行、NaN、+inf、空轴，两个函数都报错
for bad in ([-np.inf, -np.inf], [np.nan, 1.0], [np.inf, 0.0], np.zeros((2, 0))):
    expect_value_error(softmax, bad)
    expect_value_error(log_softmax, bad)
```

### 复杂度与追问

设输入有 N 个元素。时间 O(N)，输出和中间结果的空间 O(N)。

- 追问「全屏蔽行应该报错还是输出全 0」：要和上游 attention 的约定保持一致。有的实现约定全屏蔽 query 输出 0（比如 `apple-mha-code` 的练习），这份练习选择报错，让问题尽早暴露。

## 题怎么来的

OpenAI、Apple、Meta 的 ML coding 几乎都会碰到 softmax：手写一层 attention，修一份带 bug 的 Transformer，或者算 entropy。公开 debug 题里最常见的植入就是轴写错，以及直接 `exp` 导致溢出。生产代码早就走 `scaled_dot_product_attention` 了，但白板上要能把融合 kernel 里的这一步拆开讲清楚。相关真题见 `openai-transformer-debug`、`openai-entropy-l1`。

## 减 max：平移不变，避免数值溢出

$$
\mathrm{softmax}(z)_i=\frac{e^{z_i}}{\sum_j e^{z_j}}=\frac{e^{z_i-m}}{\sum_j e^{z_j-m}},\quad m=\max_j z_j.
$$

减的是同一条比较轴上的最大值，不是整个 tensor 的一个标量。减完后 $e^{z-m}\in(0,1]$。fp16 里原始 logits 到十几（$e^{12}$ 已经超过 fp16 的最大值 65504）就会得到 `inf`，normalization 之后全是 NaN。减 max 不改变分布，只改变中间结果的量级。

写的时候要带上 `keepdims=True`。否则 `[B, T]` 的 max 和 `[B, T, D]` 的输入对不上，NumPy 可能悄悄广播到错误的轴上。

后面要接 cross entropy 时，优先保留 `log_softmax`，不要先 softmax 再取 `log`，见 `coding-cross-entropy`。

## 轴：在哪一维 normalization 概率

先把 shape 写出来，再选 `axis`：

- 分类 logits `[B, T, V]`：沿 vocabulary 维 $V$。
- attention scores `[B, H, T, S]`：沿 key 长度 $S$，也就是最后一维。写成 `dim=0` 或沿 head 维，是 OpenAI 题里的经典 bug。

mask 必须在 softmax 之前填成 $-\infty$，不能填 $0$，因为 $e^0=1$，填 0 的位置仍然会分到概率。全部位置都是 $-\infty$ 时最大值也是 $-\infty$，相减得到 NaN，所以要先检查每行有没有有限值。温度 $z/T$ 也要在 softmax 之前除，顺序见 `coding-topk-nucleus`。

NVIDIA 的面试官可能会追问：约简沿最后一维时，warp 可以连续读写；轴在中间就要多做一次 transpose。白板上先把逻辑写对，再提融合的 SDPA 会把 mask、缩放和 softmax 放进同一个 kernel。

## 追问

**为什么不对整个 batch 减一个标量？**
减一个全局常数不改变精确的数学分布，风险在于其他行的指数可能全部下溢。逐行减 max 能保证每行至少有一个指数等于 1。
**fp16 还要升精度吗？**
减 max 之后大多数情况够用。遇到极端 logits，或者 entropy 这类约简，可以把这一步放到 fp32 里算，再转回去。
**和 log-sum-exp 的关系？**
$\log\sum e^{z}=m+\log\sum e^{z-m}$，softmax 的分母就是它的指数。cross entropy loss（CE）直接用 log-sum-exp 计算，不需要把 $p$ 算出来，见 `coding-logsumexp`。

## 相关题

- [[coding-logsumexp]]：同一个减 max 技巧放到 log 域，用来直接算 CE 而不先算概率。
- [[coding-online-softmax]]：把这里一次性减全局 max 改成流式的 running max，是 FlashAttention 的基础。
- [[openai-softmax-bug]]：OpenAI debug 题，softmax 轴选错、mask 填 0 时 attention 会怎样，这张的「轴」一节是它的前置。
- [[openai-entropy-l1]]：OpenAI 真题，先用稳定 softmax 得到概率再算熵，追问把损失换成 L1 时梯度怎么传。
- [[coding-gumbel-max]]：从 softmax 分布 sampling 的另一种写法，顺带区分 sampling 温度和 Gumbel-softmax 的温度。

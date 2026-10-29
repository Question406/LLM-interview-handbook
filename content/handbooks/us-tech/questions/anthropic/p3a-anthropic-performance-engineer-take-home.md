---
id: p3a-anthropic-performance-engineer-take-home
section: anthropic
order: 620
level: S
title: Anthropic：性能 Take-home：优化模拟 GPU kernel
quick: 我会先固定输入、正确性检查和计时协议，再用 roofline 判断该优化哪部分。每次只改一个点，覆盖多种尺寸测量，并记录运行次数和波动，确认加速能复现。
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · Anthropic · performance-engineer-take-home
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/performance-engineer-take-home
    type: secondary
---

## 题目描述

完成两项小规模数值任务：估计矩阵乘法的理论时间下界，以及实现支持尾部小块的矩阵乘法接口。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `roofline(m, k, n, flops_per_s, bytes_per_s, bytes_per_element=2)`：估计一次 $(m \times k) \cdot (k \times n)$ GEMM 的耗时下界。计算量按 $2mkn$ FLOPs，访存按理想情况算：A、B 各读一次，C 写一次。计算和访存假设可以完全重叠，因此时间下界取二者较大值。返回 `compute_seconds`、`memory_seconds`、`lower_bound` 和 `arithmetic_intensity`（FLOPs / 字节）。
- `gemm_blocked(a, b, block=32)`：分块矩阵乘，结果必须和 `a @ b` 一致。`a` 为 `[M,K]`、`b` 为 `[K,N]`，返回 `[M,N]` 浮点数组；`block` 为正整数，各维可以不被它整除。
- 所有尺寸和硬件参数都要为正数。硬件参数由调用方显式传入，代表假设的峰值，不是实测值。矩阵维度不超过 256。

### 输入输出示例

```text
roofline(2, 2, 2, flops_per_s=1e9, bytes_per_s=1e9)
-> compute_seconds = 1.6e-8, memory_seconds = 2.4e-8,
   lower_bound = 2.4e-8, arithmetic_intensity = 2/3

gemm_blocked([[1, 2]], [[3], [4]], block=2) -> [[11]]
```

## 解题思路与参考答案

## 题目

限时优化一个模拟 GPU kernel 的核心函数，按测出来的加速比评分。真实 kernel 的代码没有公开。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定；练习固定用分块 GEMM 代替未公开的 kernel。

我会先建立能复现的正确性基线，再逐项优化。比如练习用分块 GEMM 代替未公开 kernel，就先固定输入和随机种子，用原输出建立对照；每次改块大小或访存方式，先确认结果仍然正确。

计时协议也要先定：输入规模、运行次数、计时办法，看均值还是中位数。每次优化单独记录这些条件和方差，多换几组输入，防止只在公开样例上变快。

定位时先算 FLOPs 和最低访存字节，用 roofline 看瓶颈。带宽受限就尝试分块复用、融合相邻操作来减少搬运；计算受限就检查指令和并行度。两者都离上限很远，再排查调度和同步。

工具和 AI 使用规则以当前邀请邮件为准，旧面经未必适用。相关题 [[anthropic-perf-takehome]] 是已有的同题整理，契约不同的地方分别练，不混用。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `roofline(m, k, n, flops_per_s, bytes_per_s, bytes_per_element=2)`：估计一次 $(m \times k) \cdot (k \times n)$ GEMM 的耗时下界。计算量按 $2mkn$ FLOPs，访存按理想情况算：A、B 各读一次，C 写一次。返回 `compute_seconds`、`memory_seconds`、`lower_bound` 和 `arithmetic_intensity`（FLOPs / 字节）。
- `gemm_blocked(a, b, block=32)`：分块矩阵乘，结果必须和 `a @ b` 一致。形状不匹配或 `block < 1` 时抛 `ValueError`。
- 所有尺寸和硬件参数都要为正数，否则抛 `ValueError`。硬件参数由调用方显式传入，代表假设的峰值，不是实测值。矩阵维度不超过 256。

### 输入输出示例

```text
roofline(2, 2, 2, 1e9, 1e9)
  -> compute_seconds = 16e-9       # 2*2*2*2 = 16 FLOPs
     memory_seconds  = 24e-9       # (4 + 4 + 4) 个元素 * 2 字节 = 24 字节
     lower_bound     = 24e-9       # 访存更慢，这个规模受带宽限制
     arithmetic_intensity = 0.667
gemm_blocked(a, b, block=4)  -> 与 a @ b 在 allclose 意义下相等
```

### 解题思路与正确性

假设计算和访存可以完全重叠，那么耗时至少是两者中较慢的那个，所以 `lower_bound` 取最大值。访存量按每个矩阵只碰一次来算，这是理想下界；真实 kernel 会因为缓存放不下而重复读取，实际字节数只会更多。

`gemm_blocked` 把输出切成 `block × block` 的块，对每个输出块沿 K 方向遍历所有分块并累加。输出块 $(i, j)$ 的值等于 $\sum_p A_{ip} B_{pj}$，循环正好把每一项加了一次，所以结果和 `a @ b` 相同。最后一块不满时 NumPy 切片会自动截短，不需要额外处理。

练习不要求 Python 版本比 `a @ b` 更快。它的作用是提供一个能对照的数值参考：先写对，再在这个基础上讨论块大小、访存复用和计时方法。

### 完整参考实现（Python 3）

```python
import numpy as np


def roofline(m, k, n, flops_per_s, bytes_per_s, bytes_per_element=2):
    """估计 (m, k) @ (k, n) 的 roofline 下界。

    计算量按 2mkn FLOPs；访存按理想情况，A、B 各读一次、C 写一次。
    假设计算和访存可以完全重叠，所以下界取两者的较大值。
    """
    params = (m, k, n, flops_per_s, bytes_per_s, bytes_per_element)
    if min(params) <= 0:
        raise ValueError("all sizes and hardware rates must be positive")

    flops = 2 * m * k * n
    traffic_bytes = (m * k + k * n + m * n) * bytes_per_element
    compute_seconds = flops / flops_per_s
    memory_seconds = traffic_bytes / bytes_per_s
    return {
        "compute_seconds": compute_seconds,
        "memory_seconds": memory_seconds,
        "lower_bound": max(compute_seconds, memory_seconds),
        "arithmetic_intensity": flops / traffic_bytes,  # FLOPs / byte
    }


def gemm_blocked(a, b, block=32):
    """分块矩阵乘，结果应与 a @ b 一致。a: (M, K)，b: (K, N)，返回 (M, N)。"""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if block < 1:
        raise ValueError(f"block must be >= 1, got {block}")
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[0]:
        raise ValueError(f"incompatible shapes: {a.shape} @ {b.shape}")

    rows, inner = a.shape
    cols = b.shape[1]
    out = np.zeros((rows, cols))
    for i in range(0, rows, block):
        for j in range(0, cols, block):
            # 同一个输出块要把 K 方向所有分块的乘积累加起来
            for p in range(0, inner, block):
                out[i : i + block, j : j + block] += (
                    a[i : i + block, p : p + block] @ b[p : p + block, j : j + block]
                )
    return out
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.isclose(estimate["compute_seconds"], 16e-9)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

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


# 2x2x2：16 FLOPs、24 字节，带宽受限，下界 24 ns
estimate = roofline(2, 2, 2, 1e9, 1e9)
assert np.isclose(estimate["compute_seconds"], 16e-9)
assert np.isclose(estimate["memory_seconds"], 24e-9)
assert np.isclose(estimate["lower_bound"], 24e-9)
assert np.isclose(estimate["arithmetic_intensity"], 16 / 24)

# 形状不能整除块大小时，分块结果仍与 a @ b 一致
rng = np.random.default_rng(1)
a = rng.normal(size=(13, 7))
b = rng.normal(size=(7, 11))
for block in (1, 4, 32):
    assert np.allclose(gemm_blocked(a, b, block), a @ b)

# 非法输入
expect_value_error(roofline, 0, 2, 2, 1e9, 1e9)
expect_value_error(gemm_blocked, a, a)
expect_value_error(gemm_blocked, a, b, 0)

# cast 的反向在数学上是恒等映射，但 1e-9 的梯度在 FP16 里会下溢成 0
assert np.float16(1e-9) == 0
assert np.float32(1e-9) > 0
```

### 复杂度与追问

GEMM 的算术量是 $O(MKN)$，输出占 $O(MN)$ 空间；`roofline` 本身是 O(1)。

如果追问怎么证明优化有效，要覆盖多种尺寸，先预热，计时前后同步设备，报告中位数和分位数，并说明测量误差有多大。

如果追问块大小怎么选，原则是让一个输出块和它需要的 A、B 分块同时放进最快的那级存储里；具体取值要靠实测扫一遍。这份 NumPy 实现只用于核对数值，不要求比 `a @ b` 快，也不能证明 CUDA kernel 的性能。

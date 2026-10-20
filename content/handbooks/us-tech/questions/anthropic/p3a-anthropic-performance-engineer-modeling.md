---
id: p3a-anthropic-performance-engineer-modeling
section: anthropic
order: 633
level: S
title: "Anthropic：性能建模：matmul 算术强度与并行布局"
quick: "用 2mkn FLOPs 和最少访存字节数分别除以算力峰值和带宽，取较大者作为 matmul 的 roofline 下界，再加上流水气泡和张量并行通信开销估算实际时延。"
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
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · performance-engineer-modeling"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/performance-engineer-modeling
    type: secondary
---

## 题目

估算一次矩阵乘在 A100 上大概要多久，再把估算扩展到多层流水并行和 FFN 的张量并行分片。考察的是能不能从 FLOPs、访存和通信量推出一个有依据的时延，并说清楚哪些是理论下界、哪些是实际能做到的。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

先算两个数：计算量 $2mkn$ FLOPs，以及最少要搬的字节数 $(mk + kn + mn) \times$ 每元素字节数。分别除以计算峰值和有效带宽，得到计算时间和访存时间，较大的那个就是 roofline 下界。两者的比值叫算术强度，单位是 FLOPs / 字节；它高于硬件的「峰值算力 / 带宽」时受计算限制，低于时受带宽限制。

以 A100 的公开规格粗算（BF16 稠密约 312 TFLOP/s，HBM 带宽约 2 TB/s），拐点大约在 156 FLOPs / 字节。BF16 方阵乘的算术强度是 $2n^3 / (6n^2) = n/3$，所以 $n$ 大约超过 470 才进入计算受限区间；小矩阵或 batch 很小的 decode 阶段基本都受带宽限制。

下界之上还要加别的开销：

- 流水并行有气泡。$p$ 个 stage、$m$ 个 micro-batch 的 GPipe 式调度里，空闲比例约为 $(p - 1) / (m + p - 1)$，micro-batch 越多气泡越小。
- 张量并行要算集合通信。FFN 按 Megatron 方式切分（第一层按列切，第二层按行切）时，前向每个 FFN 需要一次 all-reduce；ring all-reduce 每张卡收发约 $2(t-1)/t$ 倍的激活字节数，再除以互联带宽就是通信时间。
- kernel 启动、同步和达不到峰值的利用率，都会让实际时延高于下界。

回答时要把硬件和并行假设列出来，并明确说明给出的是下界还是对实际时延的估计。

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
                out[i:i + block, j:j + block] += (
                    a[i:i + block, p:p + block] @ b[p:p + block, j:j + block]
                )
    return out
```

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

如果追问「实际跑出来比下界慢多少才算正常」，可以回答：大矩阵通常能到峰值的较高比例，小矩阵或形状不规整时差距很大。要用实测说话：覆盖多种尺寸，先预热，计时前后同步设备，报告中位数和分位数。

如果追问 FFN 怎么切，可以把单层的 GEMM 下界和一次 all-reduce 的通信时间分开算，再讨论通信能否和下一块计算重叠。这份 NumPy 实现只用于核对数值，不能证明 CUDA kernel 或 A100 上的性能。

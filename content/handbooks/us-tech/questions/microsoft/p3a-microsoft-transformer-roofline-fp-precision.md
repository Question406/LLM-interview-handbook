---
id: p3a-microsoft-transformer-roofline-fp-precision
section: microsoft
order: 615
level: S
title: "Microsoft AI / Copilot：MAI AI Infra：roofline、CUDA 与精度转换梯度"
quick: "先用 FLOPs 和访存量判断 matmul 是计算受限还是带宽受限，再讨论布局与融合；FP32 转 FP16 的 cast 在数学上让梯度原样通过，但 FP16 范围窄，小梯度会下溢、大值会溢出。"
companies:
  - microsoft
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Microsoft AI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Microsoft AI / Copilot · transformer-roofline-fp-precision"
    url: https://www.1point3acres.com/interview/problems/company/microsoft/transformer-roofline-fp-precision
    type: secondary
---

## 题目

读一段 Transformer 代码，估算其中 matmul 的耗时并实现一个 kernel，然后分析把残差从 FP32 转成 FP16 时，梯度在 cast 这一步怎么传、会出什么数值问题。

> 来源：一亩三分地 Microsoft AI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

性能部分先用 roofline 判断瓶颈：计算量 $2mkn$ FLOPs 除以计算峰值，最少访存字节数除以带宽，较大者是下界。判断出是计算受限还是带宽受限之后，再谈数据布局和 kernel 融合。比如带宽受限的逐元素操作，和前面的 matmul 融合后就省掉一次读写显存。

精度部分要把两件事分开讲：

- 数学上，cast 是恒等映射，反向时梯度原样穿过去（只是换了 dtype）。
- 数值上，FP16 的表示范围很窄。最小的正规格化数约 $6 \times 10^{-5}$，再小只能靠次正规数撑到约 $6 \times 10^{-8}$，更小的梯度直接变成 0；最大值约 65504，过大的激活或梯度会溢出成 inf。尾数只有 10 位，大量小数累加时还会丢精度，所以累加通常在 FP32 里做。

这就是混合精度训练要做 loss scaling、并保留 FP32 主权重的原因。性能预测要写明硬件和并行假设，不能只给一个数字。

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

测试里最后两条断言单独演示精度问题：$10^{-9}$ 在 FP32 里还能表示，转成 FP16 就成了 0。如果这是一个梯度，cast 的反向在数学上没有改变它，但存储格式已经把它丢掉了。

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

如果追问「残差为什么常留在 FP32」，可以回答：残差流是一层层累加出来的，FP16 尾数短，加上一个相对很小的更新时可能被舍掉；保留 FP32 能让小更新不丢失。

如果追问怎么验证 kernel 的性能，要覆盖多种尺寸，先预热，计时前后同步设备，报告中位数和分位数。这份 NumPy 实现只用于核对数值，不能证明 CUDA kernel 的性能。

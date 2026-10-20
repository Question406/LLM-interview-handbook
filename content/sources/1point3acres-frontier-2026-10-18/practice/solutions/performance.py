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


def test():
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


if __name__ == "__main__":
    test()

import math

import numpy as np


def noisy_ring_all_gather(values, extent, eps, flip_p, delta, rng):
    """BSC 上的单向环 all_gather：量化 + 按位重复码多数表决。

    返回 (result, stats)：result[rank, origin] 是 rank 对 values[origin] 的估计；
    stats 含 bits、repetitions、rounds。
    """
    values = np.asarray(values, float)
    if values.ndim != 1 or len(values) == 0 or not np.isfinite(values).all():
        raise ValueError("values must be a non-empty 1-D array of finite numbers")
    if not math.isfinite(extent) or extent <= 0:
        raise ValueError(f"extent must be positive and finite, got {extent}")
    if (values < 0).any() or (values > extent).any():
        raise ValueError(f"values must lie in [0, {extent}]")
    if eps <= 0:
        raise ValueError(f"eps must be positive, got {eps}")
    if not 0 <= flip_p < 0.5:
        raise ValueError(f"flip_p must be in [0, 0.5), got {flip_p}")
    if not 0 < delta < 1:
        raise ValueError(f"delta must be in (0, 1), got {delta}")

    n = len(values)
    levels = max(1, math.ceil(extent / (2 * eps)))  # 间隔 extent/levels <= 2 * eps
    bits = max(1, math.ceil(math.log2(levels + 1)))
    if bits > 32:
        raise ValueError(f"needs {bits} bits, but this practice allows at most 32")
    quantized = np.floor(values / extent * levels + 0.5).astype(np.int64)

    # union bound：全网 n(n-1)*bits 次 bit-hop，每次出错概率 <= exp(-R(1-2p)^2/2)
    total_bit_hops = max(1, n * (n - 1) * bits)
    repetitions = math.ceil(2 * math.log(total_bit_hops / delta) / (1 - 2 * flip_p) ** 2)
    if repetitions % 2 == 0:
        repetitions += 1  # 奇数次，多数表决不会平票

    seen = [{rank: int(q)} for rank, q in enumerate(quantized)]  # rank -> {origin: 量化值}
    for step in range(n - 1):
        received = []
        for rank in range(n):
            origin = (rank - step) % n  # 第 step 步，rank 转发 origin 为 rank-step 的值
            integer = seen[rank][origin]
            packet = np.array([(integer >> b) & 1 for b in range(bits)], dtype=np.int64)
            flips = rng.random((repetitions, bits)) < flip_p
            decoded = np.logical_xor(packet, flips).sum(axis=0) > repetitions // 2
            number = sum(int(bit) << b for b, bit in enumerate(decoded))
            received.append(((rank + 1) % n, origin, number))
        for rank, origin, number in received:  # 同步：本步收到的数据下一步才转发
            seen[rank][origin] = number

    result = np.array([
        [min(levels, max(0, row[origin])) * extent / levels for origin in range(n)]
        for row in seen
    ])
    stats = {"bits": bits, "repetitions": repetitions, "rounds": (n - 1) * repetitions}
    return result, stats


def expect_value_error(*args):
    try:
        noisy_ring_all_gather(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError for {args[:5]}")


values = np.array([0.0, 0.23, 0.91, 1.0])

# 无噪声：误差不超过 eps，每个 rank 结果相同
out, stats = noisy_ring_all_gather(values, 1, 0.02, 0, 0.01, np.random.default_rng(1))
assert np.max(np.abs(out - values)) <= 0.02 + 1e-12
assert np.allclose(out, out[0])

# 轮数 = (N - 1) * R，R 为奇数
assert stats["rounds"] == 3 * stats["repetitions"]
assert stats["repetitions"] % 2 == 1

# 有噪声：按 delta 选的 R 足够让这次结果仍在误差内
out, _ = noisy_ring_all_gather(values, 1, 0.02, 0.1, 0.001, np.random.default_rng(7))
assert np.max(np.abs(out - values)) <= 0.02 + 1e-12

# N = 1 不通信
_, stats = noisy_ring_all_gather([0.3], 1, 0.01, 0.1, 0.01, np.random.default_rng(2))
assert stats["rounds"] == 0

# 噪声越大，需要的重复次数越多
_, low = noisy_ring_all_gather(values, 1, 0.02, 0.05, 0.01, np.random.default_rng(3))
_, high = noisy_ring_all_gather(values, 1, 0.02, 0.3, 0.01, np.random.default_rng(3))
assert high["repetitions"] > low["repetitions"]

# 非法参数
rng = np.random.default_rng(0)
expect_value_error([1.5], 1, 0.1, 0.1, 0.01, rng)
expect_value_error([0.5], 1, 0.1, 0.5, 0.01, rng)
expect_value_error([0.5], 1, 0.0, 0.1, 0.01, rng)
expect_value_error([], 1, 0.1, 0.1, 0.01, rng)

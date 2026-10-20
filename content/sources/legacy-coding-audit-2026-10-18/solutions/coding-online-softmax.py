import numpy as np


def online_stats(x):
    """一遍扫描求 (max, sum(exp(x - max)))；x 非空且有限。"""
    if len(x) == 0:
        raise ValueError("empty scores")
    running_max = -np.inf
    running_sum = 0.0
    for value in np.asarray(x, dtype=np.float64):
        new_max = max(running_max, value)
        running_sum = running_sum * np.exp(running_max - new_max) + np.exp(value - new_max)
        running_max = new_max
    return running_max, running_sum


def softmax_from_stats(x, m, ell):
    """第二遍：用全局 max 和 sumexp 归一化。"""
    return np.exp(np.asarray(x, dtype=np.float64) - m) / ell


def online_attn_row(q, k, v, scale, tile=16):
    """单个 query 的分块注意力。q: [D]，k / v: [S, D]，返回 [D]。

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
        scores = (k[start:start + tile] @ q) * scale  # [tile]
        new_max = max(running_max, float(np.max(scores)))
        weights = np.exp(scores - new_max)
        alpha = np.exp(running_max - new_max)          # 旧标尺 -> 新标尺
        output = output * alpha + weights @ v[start:start + tile]
        running_sum = running_sum * alpha + float(weights.sum())
        running_max = new_max
    return output / running_sum


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

# 分块注意力与完整 softmax 注意力一致，与 tile 大小无关
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

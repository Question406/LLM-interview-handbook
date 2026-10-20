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

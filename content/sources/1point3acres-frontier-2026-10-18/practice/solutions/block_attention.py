import numpy as np


def block_attention(q, k, v, block):
    """单头 attention：softmax(q k^T / sqrt(D)) v，按 key 分块计算，不存完整的 T x S 分数矩阵。

    q: (T, D)，k: (S, D)，v: (S, Dv)，返回 (T, Dv)。
    """
    q, k, v = (np.asarray(x, dtype=float) for x in (q, k, v))
    if block < 1:
        raise ValueError(f"block must be >= 1, got {block}")
    if q.ndim != 2 or k.ndim != 2 or v.ndim != 2:
        raise ValueError("q, k, v must be 2-D")
    if q.shape[1] != k.shape[1] or k.shape[0] != v.shape[0]:
        raise ValueError(f"shape mismatch: q{q.shape} k{k.shape} v{v.shape}")
    if k.shape[0] == 0 or q.shape[1] == 0:
        raise ValueError("need at least one key and a non-empty head dim")

    num_queries, head_dim = q.shape
    # 每个 query 行维护三样东西，都相对同一个最大值 row_max：
    #   row_max: 目前见过的最大分数      (T, 1)
    #   denom:   sum(exp(score - row_max)) (T, 1)
    #   out:     sum(exp(score - row_max) * v)，尚未归一化 (T, Dv)
    row_max = np.full((num_queries, 1), -np.inf)
    denom = np.zeros((num_queries, 1))
    out = np.zeros((num_queries, v.shape[1]))

    for start in range(0, k.shape[0], block):
        k_block = k[start:start + block]                     # (b, D)
        v_block = v[start:start + block]                     # (b, Dv)
        scores = q @ k_block.T / np.sqrt(head_dim)           # (T, b)

        new_max = np.maximum(row_max, scores.max(axis=1, keepdims=True))
        # 最大值变大后，旧的累计量要乘 exp(旧最大值 - 新最大值) 换到新尺度
        rescale = np.exp(row_max - new_max)
        weights = np.exp(scores - new_max)                   # (T, b)

        out = out * rescale + weights @ v_block
        denom = denom * rescale + weights.sum(axis=1, keepdims=True)
        row_max = new_max

    return out / denom


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__} should raise ValueError")

    # 和一次性计算的稳定 softmax attention 对比；块大小整除、不整除、超过 S 都要对
    rng = np.random.default_rng(3)
    q = rng.normal(size=(7, 4))
    k = rng.normal(size=(11, 4))
    v = rng.normal(size=(11, 3))
    scores = q @ k.T / 2  # sqrt(D) = 2
    weights = np.exp(scores - scores.max(axis=1, keepdims=True))
    expected = weights @ v / weights.sum(axis=1, keepdims=True)
    for block in (1, 3, 11, 20):
        assert np.allclose(block_attention(q, k, v, block), expected)

    # 两个 key 分数相同，输出是 value 的平均
    assert np.allclose(block_attention([[1]], [[0], [0]], [[2], [4]], 1), [[3]])

    # 分数很大时也不溢出
    big = block_attention([[100.0]], [[100.0], [99.0]], [[1.0], [0.0]], 1)
    assert np.all(np.isfinite(big))

    # 非法输入
    expect_value_error(block_attention, q, k, v, 0)
    expect_value_error(block_attention, q, k[:, :3], v, 2)
    expect_value_error(block_attention, q, k[:0], v[:0], 2)


if __name__ == "__main__":
    test()

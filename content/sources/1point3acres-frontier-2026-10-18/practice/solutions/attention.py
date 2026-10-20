import numpy as np


def check_shapes(q, k, v):
    """q: [B, H, T, D]，k: [B, H, S, D]，v: [B, H, S, Dv]。"""
    if q.ndim != 4 or k.ndim != 4 or v.ndim != 4:
        raise ValueError("q, k, v must all be 4-D [B, H, len, dim]")
    if q.shape[:2] != k.shape[:2]:
        raise ValueError("q and k must share batch and head dims")
    if k.shape[:3] != v.shape[:3]:
        raise ValueError("k and v must share batch, head and key-length dims")
    if q.shape[-1] != k.shape[-1]:
        raise ValueError("q and k must have the same feature dim D")
    if k.shape[2] == 0:
        raise ValueError("key length S must be positive")
    if q.shape[-1] == 0:
        raise ValueError("feature dim D must be positive")


def attention(q, k, v, mask=None, causal=False):
    """缩放点积注意力。mask 可广播到 [B, H, T, S]，True 表示可见；返回 [B, H, T, Dv]。

    被全部屏蔽的 query 行输出全 0。
    """
    q, k, v = (np.asarray(x, dtype=np.float64) for x in (q, k, v))
    check_shapes(q, k, v)
    query_len, key_len, dim = q.shape[2], k.shape[2], q.shape[3]

    scores = np.einsum("bhtd,bhsd->bhts", q, k) / np.sqrt(dim)  # [B, H, T, S]

    allowed = np.ones(scores.shape, dtype=bool)
    if mask is not None:
        allowed &= np.broadcast_to(np.asarray(mask, dtype=bool), scores.shape)
    if causal:
        if query_len != key_len:
            raise ValueError("causal attention requires T == S")
        allowed &= np.tril(np.ones((query_len, key_len), dtype=bool))
    scores = np.where(allowed, scores, -np.inf)

    # 减去每行最大值防止 exp 溢出；全屏蔽行的最大值是 -inf，换成 0 以免出现 -inf - (-inf) = NaN
    row_max = np.max(scores, axis=-1, keepdims=True)
    row_max = np.where(np.isfinite(row_max), row_max, 0.0)
    weights = np.exp(scores - row_max)
    denom = weights.sum(axis=-1, keepdims=True)
    weights = np.divide(weights, denom, out=np.zeros_like(weights), where=denom > 0)

    return np.einsum("bhts,bhsv->bhtv", weights, v)


def test():
    def reference_row(q_row, keys, values):
        """单个 query 的朴素循环版本，用来对照 einsum 实现。"""
        scores = keys @ q_row / np.sqrt(q_row.shape[-1])
        weights = np.exp(scores - scores.max())
        weights /= weights.sum()
        return weights @ values

    def expect_value_error(fn, *args, **kwargs):
        try:
            fn(*args, **kwargs)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__} should raise ValueError")

    # 因果 mask：第 0 个位置只看自己，第 1 个位置平均两个 value
    q = np.ones((1, 1, 2, 1))
    v = np.array([[[[2.0], [4.0]]]])
    assert np.allclose(attention(q, q, v, causal=True), [[[[2.0], [3.0]]]])

    # 全部屏蔽时输出 0，而不是 NaN
    out = attention(q, q, v, mask=np.zeros((2, 2), dtype=bool))
    assert np.all(out == 0)

    # 随机输入与逐行循环版本对照（T != S，Dv != D）
    rng = np.random.default_rng(2)
    q = rng.normal(size=(2, 2, 3, 4))
    k = rng.normal(size=(2, 2, 5, 4))
    v = rng.normal(size=(2, 2, 5, 2))
    out = attention(q, k, v)
    for b in range(2):
        for h in range(2):
            for t in range(3):
                assert np.allclose(out[b, h, t], reference_row(q[b, h, t], k[b, h], v[b, h]))

    # 非法输入
    expect_value_error(attention, q, k, v, causal=True)          # T != S 不能用 causal
    expect_value_error(attention, q, k[:, :, :, :3], v)          # D 不一致
    expect_value_error(attention, q, k[:, :, :0], v[:, :, :0])   # 空 key


if __name__ == "__main__":
    test()

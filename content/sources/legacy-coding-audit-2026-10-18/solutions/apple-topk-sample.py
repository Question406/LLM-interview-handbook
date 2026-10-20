import math

import numpy as np


def sample_temp_k_p(logits, T, k, p, rng, mask=None):
    """按 mask → 温度 → top-k → top-p 的顺序采样一个 token id。

    T == 0 或 p == 0 时返回合法 token 中 logit 最大者；并列时取较小的 id。
    """
    scores = np.asarray(logits, dtype=float).copy()
    if scores.ndim != 1 or scores.size == 0:
        raise ValueError(f"logits must be a non-empty 1-D array, got shape {scores.shape}")
    if np.isnan(scores).any() or np.isposinf(scores).any():
        raise ValueError("logits must not contain NaN or +inf")
    if not math.isfinite(T) or T < 0:
        raise ValueError(f"temperature must be finite and >= 0, got {T}")
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError(f"top_p must be in [0, 1], got {p}")
    if k is not None and (type(k) is not int or k < 1):
        raise ValueError(f"top_k must be None or a positive int, got {k!r}")

    if mask is not None:
        if np.shape(mask) != scores.shape:
            raise ValueError(f"mask shape {np.shape(mask)} != logits shape {scores.shape}")
        scores = np.where(mask, scores, -np.inf)
    if not np.isfinite(scores).any():
        raise ValueError("every token is masked out")

    if T == 0 or p == 0:
        return int(np.argmax(scores))  # argmax 并列时返回最小下标

    # 先减 max 再除 T：极小的正 T 下也不会上溢
    scores = (scores - scores.max()) / T

    # 稳定排序：分数并列时较小的 token id 排在前面
    if k is not None:
        order = np.argsort(-scores, kind="stable")
        scores[order[k:]] = -np.inf

    weights = np.exp(scores)
    probs = weights / weights.sum()

    order = np.argsort(-probs, kind="stable")
    cumulative = np.cumsum(probs[order])
    # 第一个累计质量 >= p 的位置也要保留，因此核里至少有一个 token
    nucleus_size = min(probs.size, int(np.searchsorted(cumulative, p, side="left")) + 1)
    kept = order[:nucleus_size]

    kept_probs = probs[kept] / probs[kept].sum()
    return int(rng.choice(kept, p=kept_probs))


def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


rng = np.random.default_rng(2)

# 三个 logit 并列、k=1：只保留 id 最小的 token 0
assert all(sample_temp_k_p([0, 0, 0], 1, 1, 1, rng) == 0 for _ in range(20))

# 极小的正温度不会溢出，结果接近 greedy
assert sample_temp_k_p([1000, 999], 1e-10, None, 1, rng) == 0

# T=0 走 greedy，并且只在合法 token 里选
assert sample_temp_k_p([2, 1, 0], 0, None, 1, rng, [False, False, True]) == 2

# p=0 也走 greedy
assert sample_temp_k_p([0, 5, 1], 1, None, 0, rng) == 1

# 很小的 p 只保留概率最高的 token
assert all(sample_temp_k_p([0, 3, 1], 1, None, 0.01, rng) == 1 for _ in range(20))

# 全部 token 被 mask 时报错，而不是静默返回 token 0
expect_value_error(sample_temp_k_p, [1, 2], 1, None, 1, rng, [False, False])

# 非法参数
expect_value_error(sample_temp_k_p, [1, 2], -1, None, 1, rng)
expect_value_error(sample_temp_k_p, [1, 2], 1, 0, 1, rng)
expect_value_error(sample_temp_k_p, [1, 2], 1, None, 1.5, rng)
expect_value_error(sample_temp_k_p, [1, float("nan")], 1, None, 1, rng)

# 不截断时采样频率接近 softmax：logits [0, log 3] 对应概率 [0.25, 0.75]
draws = [sample_temp_k_p([0, math.log(3)], 1, None, 1, rng) for _ in range(10000)]
assert abs(sum(draws) / len(draws) - 0.75) < 0.02

import numpy as np


def sample(logits, k, rng):
    """只在最大的 k 个 logits 里按 softmax 概率采样，返回原词表里的 token id。"""
    logits = np.asarray(logits, dtype=float)  # [V]
    if logits.ndim != 1:
        raise ValueError(f"logits must be 1-D, got shape {logits.shape}")
    if not np.all(np.isfinite(logits)):
        raise ValueError("logits must be finite")
    if type(k) is not int or not 1 <= k <= len(logits):
        raise ValueError(f"k must be an int in [1, {len(logits)}], got {k!r}")

    # lexsort 以最后一个键为主键：先按 logit 降序，并列时按 token id 升序
    order = np.lexsort((np.arange(len(logits)), -logits))
    candidates = order[:k]  # [k]，原词表 id

    # 稳定 softmax：减去候选里的最大值不改变概率比，只防止 exp 溢出
    shifted = logits[candidates] - logits[candidates].max()
    probs = np.exp(shifted)
    probs /= probs.sum()
    return int(rng.choice(candidates, p=probs))


def test():
    def expect_value_error(*args):
        try:
            sample(*args)
        except ValueError:
            return
        raise AssertionError(f"sample{args[:2]} should raise ValueError")

    rng = np.random.default_rng(1)

    # k = 1 退化成 greedy
    assert sample([1, 2, 3, 4], 1, rng) == 3

    # 被截掉的 token 永远采不到
    assert {sample([1, 2, 3, 4], 2, rng) for _ in range(1000)} == {2, 3}

    # 并列时按 token id 升序进入候选
    assert sample([0, 0, 0], 1, rng) == 0

    # 极端 logits 不溢出
    assert sample([1000.0, -1000.0, 999.0], 2, rng) in {0, 2}

    # 等概率候选的经验频率接近 0.5
    rng = np.random.default_rng(2)
    draws = [sample([0, 0], 2, rng) for _ in range(10000)]
    assert abs(sum(draws) / len(draws) - 0.5) < 0.03

    # 同一个种子结果可复现
    first = [sample([1, 2, 3], 3, np.random.default_rng(7)) for _ in range(5)]
    second = [sample([1, 2, 3], 3, np.random.default_rng(7)) for _ in range(5)]
    assert first == second

    # 非法输入
    expect_value_error([1, 2], 0, rng)
    expect_value_error([1, 2], 3, rng)
    expect_value_error([1, float("inf")], 1, rng)
    expect_value_error([[1, 2]], 1, rng)


if __name__ == "__main__":
    test()

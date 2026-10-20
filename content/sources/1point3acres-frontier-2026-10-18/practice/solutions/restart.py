import math


def _check_distribution(times, probs, overhead):
    if not times or len(times) != len(probs):
        raise ValueError("times and probs must be non-empty and the same length")
    if any(t <= 0 for t in times):
        raise ValueError("solve times must be positive")
    if any(p < 0 for p in probs) or not math.isclose(sum(probs), 1.0):
        raise ValueError("probs must be non-negative and sum to 1")
    if overhead < 0:
        raise ValueError("overhead must be non-negative")


def expected_restart(times, probs, tau, overhead=0.0):
    """阈值为 tau 的重启策略下，求解完成的期望总耗时。

    每次尝试先付 overhead，跑到 min(T, tau)；T <= tau 算成功，否则从头独立重来。
    """
    _check_distribution(times, probs, overhead)
    if tau <= 0:
        raise ValueError("tau must be positive")

    success = sum(p for t, p in zip(times, probs) if t <= tau)
    if success == 0:
        return math.inf
    cost_per_attempt = overhead + sum(p * min(t, tau) for t, p in zip(times, probs))
    # E = cost + (1 - success) * E  =>  E = cost / success
    return cost_per_attempt / success


def best_threshold(times, probs, overhead=0.0):
    """在所有支持点里找期望耗时最小的阈值，返回 (期望耗时, tau)，并列取较小的 tau。"""
    candidates = sorted(set(times))  # 最大的支持点等价于「不重启」
    return min((expected_restart(times, probs, tau, overhead), tau) for tau in candidates)


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 一半概率 1 秒解出，一半 100 秒：tau = 1 时期望 2，不重启是 50.5
    assert expected_restart([1, 100], [0.5, 0.5], 1) == 2
    assert expected_restart([1, 100], [0.5, 0.5], 100) == 50.5
    assert best_threshold([1, 100], [0.5, 0.5]) == (2.0, 1)

    # 阈值小于所有求解时间，永远不会成功
    assert expected_restart([2], [1], 1) == math.inf

    # 每次尝试的固定开销
    assert expected_restart([2], [1], 2, 1) == 3

    # 开销大到重启不划算时，最佳阈值就是不重启
    assert best_threshold([1, 100], [0.5, 0.5], 100) == (150.5, 100)

    # 非法分布
    expect_value_error(expected_restart, [1, 2], [0.5, 0.6], 1)
    expect_value_error(expected_restart, [0], [1], 1)
    expect_value_error(expected_restart, [1], [1], 0)


if __name__ == "__main__":
    test()

def reservoir(stream, k, rng):
    """一遍扫描未知长度的流，O(k) 空间均匀无放回抽取 min(k, N) 项。

    rng 需提供 randrange；返回顺序不保证是原顺序。
    """
    if k < 0:
        raise ValueError("k must be non-negative")
    sample = []
    for index, item in enumerate(stream):
        if index < k:
            sample.append(item)
        elif k > 0:
            # 第 index + 1 个元素以 k / (index + 1) 的概率进入，进入时均匀替换一个槽位
            slot = rng.randrange(index + 1)
            if slot < k:
                sample[slot] = item
    return sample


def test():
    import random

    # 流比 k 短时全部返回；k = 0 时为空
    assert reservoir(range(3), 5, random.Random(1)) == [0, 1, 2]
    assert reservoir(range(10), 0, random.Random(1)) == []
    assert reservoir(iter([]), 3, random.Random(1)) == []

    # 重复试验：每个元素的入选频率应接近 k / N = 0.3，且一次抽样内不重复
    trials = 10000
    counts = [0] * 10
    rng = random.Random(3)
    for _ in range(trials):
        picks = reservoir(range(10), 3, rng)
        assert len(picks) == 3
        assert len(set(picks)) == 3
        for item in picks:
            counts[item] += 1
    # 0.025 约为二项分布标准差 sqrt(0.3 * 0.7 / 10000) ≈ 0.0046 的 5 倍
    assert all(abs(count / trials - 0.3) < 0.025 for count in counts)

    try:
        reservoir(range(3), -1, random.Random(1))
    except ValueError:
        pass
    else:
        raise AssertionError("negative k should raise ValueError")


if __name__ == "__main__":
    test()

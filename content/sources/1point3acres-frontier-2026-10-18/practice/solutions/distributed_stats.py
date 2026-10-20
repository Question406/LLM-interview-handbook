from collections import Counter


def mode_of(counts):
    """出现次数最多的值；并列时取较小的值。"""
    return min(counts, key=lambda value: (-counts[value], value))


def count_at_most(local, threshold):
    """worker 端：只回传本地 <= threshold 的元素个数，不传原始数据。"""
    return sum(1 for value in local if value <= threshold)


def distributed_stats(shards):
    """shards 是各 worker 的本地整数列表。返回 (众数, 中位数, 计数查询轮数)。"""
    total_count = sum(len(local) for local in shards)
    if total_count == 0:
        raise ValueError("no data on any worker")

    # 众数：每个 worker 发完整的本地计数，由 coordinator 合并；只发本地众数会出错
    merged = Counter()
    for local in shards:
        merged.update(Counter(local))
    mode = mode_of(merged)

    # 中位数：先用各 worker 的 min/max 得到全局值域，再在值域上二分
    low = min(min(local) for local in shards if local)
    high = max(max(local) for local in shards if local)
    rounds = 0

    def kth_smallest(k):
        """全局第 k 小（从 1 开始）：最小的 x 使得全局 <= x 的个数 >= k。"""
        nonlocal rounds
        left, right = low, high
        while left < right:
            mid = (left + right) // 2
            rounds += 1
            # 每一轮 coordinator 只从每个 worker 收到一个计数
            count = sum(count_at_most(local, mid) for local in shards)
            if count >= k:
                right = mid
            else:
                left = mid + 1
        return left

    if total_count % 2:
        median = kth_smallest((total_count + 1) // 2)
    else:
        half = total_count // 2
        median = (kth_smallest(half) + kth_smallest(half + 1)) / 2
    return mode, median, rounds


def test():
    import random
    import statistics

    # 每个分片的本地众数是 1 和 2，全局众数是 2
    assert distributed_stats([[1, 1, 9], [2, 2, 2]])[:2] == (2, 2.0)

    # 空分片
    assert distributed_stats([[], [7, 7]])[:2] == (7, 7.0)

    # 偶数个元素取中间两个的平均
    assert distributed_stats([[1, 4], [2, 3]])[1] == 2.5

    # 全局为空
    try:
        distributed_stats([[], []])
    except ValueError:
        pass
    else:
        raise AssertionError("empty input should raise ValueError")

    # 和单机 statistics.median、Counter 随机对照
    rng = random.Random(4)
    for _ in range(100):
        values = [rng.randrange(-20, 20) for _ in range(21)]
        mode, median, _ = distributed_stats([values[:7], values[7:]])
        assert median == statistics.median(values)
        assert mode == mode_of(Counter(values))


if __name__ == "__main__":
    test()

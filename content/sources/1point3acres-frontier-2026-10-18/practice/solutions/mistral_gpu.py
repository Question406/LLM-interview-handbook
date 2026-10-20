def remaining(capacity, usages):
    """返回 remain[day][cluster]：每天从 capacity 重新开始，扣掉当天在该集群的用量。

    usages 是 (day, cluster, gpus) 三元组，可以乱序；输出覆盖第 0 天到最大的 day，
    没有记录的日子就是满容量。usages 为空时返回 []。
    """
    if not capacity or any(gpus < 0 for gpus in capacity):
        raise ValueError("capacity must be non-empty and non-negative")
    if not usages:
        return []
    for day, cluster, gpus in usages:
        if day < 0 or not 0 <= cluster < len(capacity) or gpus < 0:
            raise ValueError(f"invalid usage: {(day, cluster, gpus)!r}")

    last_day = max(day for day, _, _ in usages)
    remain = [list(capacity) for _ in range(last_day + 1)]  # 每天独立复制，余量不结转
    for day, cluster, gpus in usages:
        remain[day][cluster] -= gpus
        if remain[day][cluster] < 0:
            raise ValueError(f"day {day} cluster {cluster} is over capacity")
    return remain


def unlimited(remain):
    """切换次数不限：各天互不约束，每天取最大的那个集群。"""
    return sum(max(row) for row in remain)


def limited(remain, k):
    """每天选一个集群，相邻两天集群不同算一次切换，最多 k 次，返回最大总余量。"""
    if k < 0:
        raise ValueError("k must be non-negative")
    if not remain:
        return 0
    clusters = len(remain[0])
    if clusters == 0 or any(len(row) != clusters for row in remain):
        raise ValueError("remain must be a non-empty rectangular matrix")

    k = min(k, len(remain) - 1)  # D 天最多只能切换 D - 1 次
    neg_inf = float("-inf")
    # best[used][cluster]：到当前这天为止用了 used 次切换、当天停在 cluster 的最大总和
    best = [[neg_inf] * clusters for _ in range(k + 1)]
    best[0] = list(remain[0])  # 第一天的选择不算切换
    for row in remain[1:]:
        nxt = [[neg_inf] * clusters for _ in range(k + 1)]
        for used in range(k + 1):
            for dest in range(clusters):
                stay = best[used][dest]
                switch = neg_inf
                if used > 0:
                    switch = max(
                        (best[used - 1][src] for src in range(clusters) if src != dest),
                        default=neg_inf,
                    )
                nxt[used][dest] = max(stay, switch) + row[dest]
        best = nxt
    return max(max(layer) for layer in best)


def test():
    import itertools
    import random

    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    def brute_force(remain, k):
        """枚举每天的集群选择，只保留切换次数不超过 k 的路径。"""
        totals = []
        for path in itertools.product(range(len(remain[0])), repeat=len(remain)):
            switches = sum(prev != cur for prev, cur in zip(path, path[1:]))
            if switches <= k:
                totals.append(sum(remain[day][cluster] for day, cluster in enumerate(path)))
        return max(totals)

    # 乱序记录；每天容量重置，不把前一天的余量带过去
    remain_matrix = remaining([10, 20], [(1, 0, 3), (0, 0, 5), (0, 1, 13)])
    assert remain_matrix == [[5, 7], [7, 20]]
    assert unlimited(remain_matrix) == 27
    assert limited(remain_matrix, 0) == 27

    # 中间没有记录的日子是满容量；同一天同集群的多条记录累加
    assert remaining([4, 4], [(2, 1, 1), (2, 1, 2)]) == [[4, 4], [4, 4], [4, 1]]
    assert remaining([4], []) == []

    # 非法输入
    expect_value_error(remaining, [5], [(0, 0, 3), (0, 0, 3)])  # 当天累计超额
    expect_value_error(remaining, [5], [(0, 1, 1)])             # 集群越界
    expect_value_error(remaining, [], [])                       # 空容量
    expect_value_error(limited, [[1]], -1)
    expect_value_error(limited, [[1, 2], [3]], 1)               # 不是矩形

    # 与暴力枚举对拍：交错的矩阵每多一次切换都能多拿分
    zigzag = [[9, 1], [1, 9], [9, 1]]
    for k in range(3):
        assert limited(zigzag, k) == brute_force(zigzag, k)
    assert limited(zigzag, 10) == unlimited(zigzag) == 27

    # 随机小矩阵对拍
    rng = random.Random(0)
    for _ in range(50):
        days, clusters = rng.randint(1, 4), rng.randint(1, 3)
        matrix = [[rng.randint(0, 9) for _ in range(clusters)] for _ in range(days)]
        for k in range(days + 1):
            assert limited(matrix, k) == brute_force(matrix, k)


if __name__ == "__main__":
    test()

FILL = "__fill__"  # 补洞时使用的新 owner，保留名


def _check_inputs(shards, lo, hi, limit):
    if lo >= hi:
        raise ValueError(f"empty target range [{lo}, {hi})")
    if limit < 1:
        raise ValueError(f"limit must be >= 1, got {limit}")
    ids = [shard_id for shard_id, _, _ in shards]
    if len(set(ids)) != len(ids):
        raise ValueError("shard ids must be unique")
    if FILL in ids:
        raise ValueError(f"{FILL!r} is reserved")
    for shard_id, start, end in shards:
        if start >= end:
            raise ValueError(f"shard {shard_id!r} has empty range [{start}, {end})")


def rebalance(shards, lo, hi, limit):
    """让 [lo, hi) 上每一点被 1 到 limit 个 shard 覆盖，迁移成本最小。

    shards 是 (id, start, end) 的半开区间列表。返回 (基本段列表, 总成本)，
    每个基本段是 (start, end, owners)；成本是新增和删除的「owner × 长度」之和。
    """
    _check_inputs(shards, lo, hi, limit)

    # 覆盖集合只会在端点处变化，用端点把 [lo, hi) 切成基本段
    cuts = {lo, hi}
    for _, start, end in shards:
        for point in (start, end):
            if lo < point < hi:
                cuts.add(point)
    cuts = sorted(cuts)

    segments = []
    cost = 0
    for seg_start, seg_end in zip(cuts, cuts[1:]):
        owners = sorted(
            shard_id for shard_id, start, end in shards
            if start <= seg_start and seg_end <= end
        )
        length = seg_end - seg_start
        if not owners:
            # 缺口：至少新增一个 owner
            segments.append((seg_start, seg_end, (FILL,)))
            cost += length
        else:
            # 超额：保留字典序前 limit 个，删掉其余的
            segments.append((seg_start, seg_end, tuple(owners[:limit])))
            cost += length * max(0, len(owners) - limit)
    return segments, cost


def test():
    def expect_value_error(*args):
        try:
            rebalance(*args)
        except ValueError:
            return
        raise AssertionError(f"rebalance{args} should raise ValueError")

    # [3, 5) 重叠删一个（成本 2），[8, 10) 缺口补一个（成本 2）
    segments, cost = rebalance([("a", 0, 5), ("b", 3, 8)], 0, 10, 1)
    assert cost == 4
    assert segments == [
        (0, 3, ("a",)),
        (3, 5, ("a",)),
        (5, 8, ("b",)),
        (8, 10, (FILL,)),
    ]

    # 没有任何 shard：整段补洞
    assert rebalance([], 0, 3, 2) == ([(0, 3, (FILL,))], 3)

    # limit 足够大时什么都不用动；目标范围外的部分忽略
    assert rebalance([("a", -5, 5), ("b", 0, 9)], 0, 5, 2) == ([(0, 5, ("a", "b"))], 0)

    # 非法输入
    expect_value_error([("a", 0, 1), ("a", 1, 2)], 0, 2, 1)
    expect_value_error([("a", 2, 2)], 0, 3, 1)
    expect_value_error([(FILL, 0, 1)], 0, 1, 1)
    expect_value_error([], 3, 3, 1)
    expect_value_error([], 0, 3, 0)


if __name__ == "__main__":
    test()

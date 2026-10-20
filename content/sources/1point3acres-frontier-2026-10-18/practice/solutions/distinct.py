import itertools


def distinct(nums, k):
    """每个元素可以加上 [-k, k] 内的任意整数，返回 (最多能有几个不同值, 一种变换后的数组)。"""
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")

    result = list(nums)
    last_used = None  # 目前分配出去的最大值；分配值严格递增
    count = 0
    # 所有区间 [x - k, x + k] 等长，按 x 排序就同时按左、右端点排好了
    for value, index in sorted((value, index) for index, value in enumerate(nums)):
        low, high = value - k, value + k
        choice = low if last_used is None else max(low, last_used + 1)
        if choice <= high:
            result[index] = choice
            last_used = choice
            count += 1
        # 分不到新值的元素保留原值：此时 [low, last_used] 已经全部被占用，
        # 原值必然和某个已分配值重复，不会多出一个不同值
    return count, result


def test():
    def brute_force(nums, k):
        choices = (range(x - k, x + k + 1) for x in nums)
        return max(len(set(candidate)) for candidate in itertools.product(*choices))

    # 三个相同元素，k = 1 时可以拉开成 0, 1, 2
    assert distinct([1, 1, 1], 1) == (3, [0, 1, 2])

    # k = 0 时不能改动
    assert distinct([1, 1, 1], 0)[0] == 1

    # 和暴力枚举对照：返回的数组也必须真的有这么多不同值
    for nums in itertools.product(range(3), repeat=3):
        count, result = distinct(nums, 1)
        best = brute_force(nums, 1)
        assert count == best
        assert len(set(result)) == best
        assert all(abs(new - old) <= 1 for new, old in zip(result, nums))

    # 空数组
    assert distinct([], 2) == (0, [])


if __name__ == "__main__":
    test()

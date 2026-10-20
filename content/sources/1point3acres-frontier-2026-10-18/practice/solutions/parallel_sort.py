from concurrent.futures import ThreadPoolExecutor
from heapq import merge
from math import ceil


def split_chunks(nums, parts):
    """按 ceil(len / parts) 切块，最多 parts 块，只有最后一块可能更短。"""
    size = ceil(len(nums) / parts)
    return [nums[start:start + size] for start in range(0, len(nums), size)]


def parallel_sort(nums, workers=4):
    """分块后由多个线程各自排序，再 k 路归并；返回新列表，不修改输入。"""
    if workers < 1:
        raise ValueError(f"workers must be at least 1: {workers}")
    if not nums:
        return []
    chunks = split_chunks(nums, workers)
    # with 块退出时会等所有线程结束，所以 sorted_chunks 里每块都已排好
    with ThreadPoolExecutor(max_workers=workers) as pool:
        sorted_chunks = list(pool.map(sorted, chunks))
    # heapq.merge 每次取各块当前最小的首元素
    return list(merge(*sorted_chunks))


def test():
    import random

    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 题面示例，含重复值
    assert parallel_sort([3, 1, 2, 1], 2) == [1, 1, 2, 3]

    # 随机输入与内置 sorted 对照，并检查输入没被修改
    rng = random.Random(4)
    for n in (0, 1, 7, 1000):
        nums = [rng.randrange(-20, 20) for _ in range(n)]
        original = nums[:]
        assert parallel_sort(nums, 3) == sorted(nums)
        assert nums == original

    # 线程数多于元素数
    assert parallel_sort([2, 1], 8) == [1, 2]

    expect_value_error(parallel_sort, [1], 0)


if __name__ == "__main__":
    test()

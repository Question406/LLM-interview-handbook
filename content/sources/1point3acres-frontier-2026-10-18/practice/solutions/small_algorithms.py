import heapq
from collections import defaultdict


def suffix_counts(nums, queries):
    """对每个查询下标 i，返回后缀 nums[i:] 的最大值在该后缀里出现几次。"""
    for i in queries:
        if type(i) is not int or not 0 <= i < len(nums):
            raise ValueError(f"query index out of range: {i!r}")

    counts = [0] * len(nums)
    maximum = None
    count = 0
    # 从右往左扫，maximum/count 始终描述「当前位置开始的后缀」
    for i in range(len(nums) - 1, -1, -1):
        if maximum is None or nums[i] > maximum:
            maximum = nums[i]
            count = 1
        elif nums[i] == maximum:
            count += 1
        counts[i] = count
    return [counts[i] for i in queries]


def topk(nums, k):
    """选出值最大的 k 个元素，值相同时先选下标小的，结果按原数组顺序输出。"""
    if type(k) is not int or not 0 <= k <= len(nums):
        raise ValueError(f"k must be in [0, {len(nums)}], got {k!r}")
    # 排序键 (-值, 下标)：nsmallest 内部用大小为 k 的堆，O(n log k)
    chosen = heapq.nsmallest(k, range(len(nums)), key=lambda i: (-nums[i], i))
    return [nums[i] for i in sorted(chosen)]


def dfs(edges, start):
    """无向图从 start 出发做 DFS，邻居按字典序访问；返回访问顺序。"""
    graph = defaultdict(set)
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)

    stack = [start]
    seen = set()
    order = []
    while stack:
        node = stack.pop()
        if node in seen:  # 同一节点可能被压栈多次，出栈时再判重
            continue
        seen.add(node)
        order.append(node)
        # 逆序压栈，字典序最小的邻居最先出栈，和递归版顺序一致
        stack.extend(sorted(graph[node] - seen, reverse=True))
    return order


def above(nums, threshold):
    """返回 (严格大于 threshold 的元素个数, 这些元素的零基下标列表)。"""
    indexes = [i for i, value in enumerate(nums) if value > threshold]
    return len(indexes), indexes


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # suffix_counts：最大值重复、负数
    assert suffix_counts([3, 1, 3], [0, 1, 2]) == [2, 1, 1]
    assert suffix_counts([-2, -2, -3], [0, 1, 2]) == [2, 1, 1]
    expect_value_error(suffix_counts, [1, 2], [2])
    expect_value_error(suffix_counts, [], [0])

    # topk：并列时取靠前的下标，输出保持原顺序
    assert topk([3, 1, 3, 2], 2) == [3, 3]
    assert topk([2, 3, 1], 2) == [2, 3]
    assert topk([5, 5, 5], 2) == [5, 5]
    assert topk([1, 2], 0) == []
    expect_value_error(topk, [1, 2], 3)

    # dfs：有环图按字典序访问；孤立起点也要输出
    assert dfs([("a", "b"), ("a", "c"), ("b", "c")], "a") == ["a", "b", "c"]
    assert dfs([("a", "c"), ("a", "b"), ("b", "d")], "a") == ["a", "b", "d", "c"]
    # 入栈时就标记的写法在这里会得到 a, b, d, c
    assert dfs([("a", "b"), ("a", "c"), ("b", "c"), ("b", "d")], "a") == ["a", "b", "c", "d"]
    assert dfs([], "x") == ["x"]

    # above：严格大于；空数组
    assert above([1, 5, 7], 4) == (2, [1, 2])
    assert above([4, 5], 4) == (1, [1])
    assert above([], 0) == (0, [])


if __name__ == "__main__":
    test()

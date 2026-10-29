---
id: p3a-microsoft-max-number-occurrences-in-suffix
section: microsoft
order: 607
level: A
title: Microsoft AI / Copilot：MAI 后缀最大值出现次数
quick: >-
  我会从右向左预处理，维护后缀最大值和次数：新值更大就重置为 1，相等就加 1，更小就保持。把每个起点的次数存下来，预处理 O(n)，查询只要
  O(1)，负数也要正确处理。
companies:
  - microsoft
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Microsoft AI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · Microsoft AI / Copilot · max-number-occurrences-in-suffix
    url: >-
      https://www.1point3acres.com/interview/problems/company/microsoft/max-number-occurrences-in-suffix
    type: secondary
---

## 题目描述

给定整数数组和若干后缀起点，分别返回每个后缀中最大值出现的次数。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `suffix_counts(nums, queries) -> list[int]`：对每个查询下标 i，返回 `nums[i:]` 的最大值在该后缀中的出现次数。`nums` 是整数列表，`queries` 是合法整数下标列表，下标位于 $[0,n)$；返回值按查询顺序排列。
- $n \le 10^5$，元素可以为负；空数组仅接受空查询，返回 `[]`。

### 输入输出示例

```text
suffix_counts([3, 1, 3], [0, 1, 2])    -> [2, 1, 1]
suffix_counts([-2, -2, -3], [0, 1, 2]) -> [2, 1, 1]
```

第一个例子里，后缀 `[3, 1, 3]` 的最大值 3 出现两次，后缀 `[1, 3]` 和 `[3]` 都只出现一次。

## 解题思路与参考答案

我会从右往左扫一遍，把每个后缀的最大值次数预先存好。例如 `[3, 1, 3]` 的答案是两次，往右移到 `[1, 3]` 就变成一次；查询时直接按起点查表。

## 题目

给一个整数数组和若干个起点下标。对每个起点 i，求后缀 `nums[i:]` 的最大值在这个后缀里出现了几次。查询很多时，不能每次都重新扫一遍后缀。

> 来源：一亩三分地 Microsoft AI / Copilot 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

## 思路

扫描时只需要当前后缀的最大值和出现次数。每向左加入一个新元素，就按它与当前最大值的关系更新：

- 比当前最大值大：最大值换成它，次数重置为 1；
- 等于当前最大值：次数加 1；
- 比当前最大值小：两个量都不变，沿用右边一格的答案。

把每个位置的次数存进数组，之后每个查询直接查表。预处理 O(n)，单次查询 O(1)。

与面试官确认的 edge cases：空数组和越界下标怎么处理（这里抛 `ValueError`），负数是否允许（允许，所以最大值初始化成 `None`，不能用 0）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `suffix_counts(nums, queries) -> list[int]`：对每个查询下标 i，返回 `nums[i:]` 的最大值在该后缀中的出现次数。下标不是整数或不在 $[0, n)$ 内时抛 `ValueError`。
- 同一个参考文件里还有 `topk`、`dfs`、`above` 三个函数，分别对应其他几张题卡，本题不要求实现。
- $n \le 10^5$，元素可以为负。

### 输入输出示例

```text
suffix_counts([3, 1, 3], [0, 1, 2])    -> [2, 1, 1]
suffix_counts([-2, -2, -3], [0, 1, 2]) -> [2, 1, 1]
```

第一个例子里，后缀 `[3, 1, 3]` 的最大值 3 出现两次，后缀 `[1, 3]` 和 `[3]` 都只出现一次。

### 解题思路与正确性

扫描到位置 i 时，`maximum` 和 `count` 恰好描述后缀 `nums[i:]`：新元素更大时，它就是新后缀唯一的最大值；相等时多一次出现；更小时不影响最大值。归纳下去，每个位置记下的次数都是对的。

查询下标在扫描前统一校验，任何一个不合法都会直接报错，不会返回部分结果。

### 完整参考实现（Python 3）

```python
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
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert suffix_counts([3, 1, 3], [0, 1, 2]) == [2, 1, 1]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
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
assert dfs([("a", "b"), ("a", "c"), ("b", "c"), ("b", "d")], "a") == [
    "a",
    "b",
    "c",
    "d",
]
assert dfs([], "x") == ["x"]

# above：严格大于；空数组
assert above([1, 5, 7], 4) == (2, [1, 2])
assert above([4, 5], 4) == (1, [1])
assert above([], 0) == (0, [])
```

### 复杂度与追问

设数组长度为 n、查询数为 q。预处理 O(n) 时间和 O(n) 空间，回答全部查询 O(q)，合计 O(n + q)。

如果数组会在末尾追加元素，已有后缀的答案都可能变化，这时可以把问题换成「区间最大值及其次数」，用线段树每个节点存 (最大值, 次数)，合并时比较两边最大值，单次更新和查询都是 O(log n)。

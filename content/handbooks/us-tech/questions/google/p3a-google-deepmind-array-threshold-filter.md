---
id: p3a-google-deepmind-array-threshold-filter
section: google
order: 807
level: A
title: "DeepMind Android：数组阈值过滤与索引"
quick: "用一次遍历收集严格大于阈值的元素下标，列表长度就是数量，时间 O(n)。开写前确认比较是否包含等号、下标从哪里开始；这份练习采用严格大于和零基下标，空数组返回 `(0, [])`。"
companies:
  - google
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - google-deepmind
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · DeepMind Android：数组阈值过滤与索引"
    url: https://www.1point3acres.com/interview/problems/6ef654a3-ec8c-4ce7-b96b-1eb1455d9e21
    type: secondary
---

## 题目描述

给定整数数组 nums 和阈值 threshold，找出所有严格大于阈值的元素，返回数量和它们在原数组中的下标。不得改动原数组中的元素顺序或把值当成下标返回。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `above(nums, threshold) -> tuple[int, list[int]]`：返回 (严格大于 `threshold` 的元素个数, 这些元素的零基下标列表)，下标按升序排列。
- $n \le 10^5$。

### 示例

```text
above([1, 5, 7], 4) -> (2, [1, 2])
above([4, 5], 4)    -> (1, [1])
above([], 0)        -> (0, [])
```

## 解题思路与参考答案

## 题目

给一个数组和一个阈值，统计有多少个元素严格大于阈值，并返回这些元素的下标。题目来自 DeepMind Android 岗位相关的题目目录。

> 来源：一亩三分地题目详情页（2026-10-18 读取），题面是网站从面经整理的，没有逐条核对原帖；网站收录不等于公司官方确认。这条属于 Android 岗位，不能当成 DeepMind 研究岗的题。下面的接口、约束和测试是手册补的练习约定。

## 思路

我会直接遍历数组，把严格大于阈值的元素下标追加到列表，最后返回列表长度和列表本身。例如 `[4, 5]` 的阈值是 4 时，只收集下标 1，因为等于阈值的 4 不满足条件。

这是一道基础题，重点是把边界问清楚：比较用「大于」还是「大于等于」，下标从 0 还是从 1 开始，空数组返回什么。这份练习的约定是严格大于、零基下标、空数组返回 `(0, [])`。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `above(nums, threshold) -> tuple[int, list[int]]`：返回 (严格大于 `threshold` 的元素个数, 这些元素的零基下标列表)，下标按升序排列。
- 同一个参考文件里还有 `suffix_counts`、`topk`、`dfs` 三个函数，分别对应其他几张题卡，本题不要求实现。
- $n \le 10^5$。

### 输入输出示例

```text
above([1, 5, 7], 4) -> (2, [1, 2])
above([4, 5], 4)    -> (1, [1])
above([], 0)        -> (0, [])
```

第二个例子里 4 等于阈值，不算在内。

### 解题思路与正确性

这个做法会检查每个元素一次，不会漏掉满足条件的项；只有比较成立才追加，也不会多收。遍历按下标从小到大进行，所以返回的下标自然升序。

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

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

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
assert dfs([("a", "b"), ("a", "c"), ("b", "c"), ("b", "d")], "a") == ["a", "b", "c", "d"]
assert dfs([], "x") == ["x"]

# above：严格大于；空数组
assert above([1, 5, 7], 4) == (2, [1, 2])
assert above([4, 5], 4) == (1, [1])
assert above([], 0) == (0, [])
```

### 复杂度与追问

数组长 n、命中 k 个元素时，扫描时间为 O(n)，返回列表需要 O(k) 空间。空数组没有元素可追加，因此得到 `(0, [])`。

如果同一个数组要回答很多个不同阈值的查询，可以先把 (值, 下标) 按值排序，每次用二分找到第一个大于阈值的位置，数量是 O(log n) 得到；要返回下标时仍需输出 k 个元素。

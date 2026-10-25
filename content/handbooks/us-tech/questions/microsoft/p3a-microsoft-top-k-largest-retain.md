---
id: p3a-microsoft-top-k-largest-retain
section: microsoft
order: 608
level: A
title: "Microsoft AI / Copilot：MAI Top-K：排序、保留原序与复合排名"
quick: "我会先用大小为 K 的堆选出入选下标，再按下标升序输出，保留原数组顺序。并列和业务排名都放进排序键，选择阶段 O(n log K)、空间 O(K)；K 接近 n 时全排序更简单。"
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
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Microsoft AI / Copilot · top-k-largest-retain"
    url: https://www.1point3acres.com/interview/problems/company/microsoft/top-k-largest-retain
    type: secondary
---

## 题目描述

从数组中选出数值最大的 k 个元素，但按它们在原数组中的先后顺序返回。

以下接口、边界和规模限制是手册重构的练习约定，不代表面试原题逐字原文；输入默认满足所列合法约束。

### 接口与规则

- `topk(nums, k) -> list`：选出值最大的 k 个元素，值相同时先选下标小的，输出按元素在 `nums` 中的原顺序排列。`nums` 是数值列表，`k` 为 $[0,n]$ 内的整数；`k=0` 返回 `[]`。
- $n \le 10^5$。

### 输入输出示例

```text
topk([3, 1, 3, 2], 2) -> [3, 3]
topk([2, 3, 1], 2)    -> [2, 3]
topk([1, 2], 0)       -> []
```

第二个例子中入选的是 3 和 2，按原数组顺序输出成 `[2, 3]`，而不是按值降序的 `[3, 2]`。

## 解题思路与参考答案

我会把「哪些元素入选」和「按什么顺序输出」分开处理。比如入选值是 3 和 2，原数组里 2 在前，就要输出 `[2, 3]`；先选下标，再按下标排序就能保证这一点。

## 题目

从数组里取出值最大的 K 个元素。题卡提到的变体有两种：结果要保持元素在原数组中的顺序，或者按业务给的复合规则排名。

> 来源：一亩三分地 Microsoft AI / Copilot 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

n 很大而 K 较小时，用一个大小为 K 的最小堆：堆顶是目前入选元素里最差的那个，新元素比它好就替换。这样时间是 O(n log K)，额外空间 O(K)。Python 的 `heapq.nsmallest(k, ..., key=...)` 内部就是这么做的。

保留原序时，堆记录入选下标，选完把下标升序排列后再取值。直接按值输出会丢掉原始顺序。

并列规则必须先说清楚。这份练习用排序键 `(-值, 下标)`：值大的优先，值相同时下标小的优先。业务上的复合排名也是同一个思路，把规则写成一个排序键即可。另外要约定 K 为 0 或超过数组长度时怎么办，这里 K 必须在 $[0, n]$ 内，否则抛 `ValueError`。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `topk(nums, k) -> list`：选出值最大的 k 个元素，值相同时先选下标小的，输出按元素在 `nums` 中的原顺序排列。k 不在 $[0, n]$ 内时抛 `ValueError`。
- 同一个参考文件里还有 `suffix_counts`、`dfs`、`above` 三个函数，分别对应其他几张题卡，本题不要求实现。
- $n \le 10^5$。

### 输入输出示例

```text
topk([3, 1, 3, 2], 2) -> [3, 3]
topk([2, 3, 1], 2)    -> [2, 3]
topk([1, 2], 0)       -> []
```

第二个例子中入选的是 3 和 2，按原数组顺序输出成 `[2, 3]`，而不是按值降序的 `[3, 2]`。

### 解题思路与正确性

排序键 `(-nums[i], i)` 是一个全序，所以「最小的 k 个键」唯一确定，对应的就是按题目规则排名前 k 的下标。再把这些下标升序排列后取值，输出顺序就和原数组一致。

`heapq.nsmallest` 维护大小为 k 的堆，与先全排序再取前 k 个结果相同，只是在 k 远小于 n 时更快。

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

设数组长度为 n。选下标是 O(n log k)，最后给 k 个下标排序是 O(k log k)，额外空间 O(k)。

- 数据是流式到达、不能全部存下时，仍然只维护大小为 k 的堆，但要保持原序输出，堆里就得存 (排序键, 下标, 值)，流结束后再按下标排序。
- 如果 k 接近 n，直接全排序 O(n log n) 更简单；只要第 k 大的阈值时，可以用快速选择做到平均 O(n)。
- 复合排名只需要换排序键，例如「分数降序、时间升序、ID 升序」就是 `(-score, time, id)`。

## 相关题

- [[p3a-xai-twitter-spaces-active-hours]]：同样按复合键（人数降序、名字升序）取 top-K，但数据是流式的，计数会下降，堆里要处理过期条目。

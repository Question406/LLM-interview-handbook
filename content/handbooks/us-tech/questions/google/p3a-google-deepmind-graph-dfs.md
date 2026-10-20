---
id: p3a-google-deepmind-graph-dfs
section: google
order: 806
level: A
title: "DeepMind Android：构图与 DFS"
quick: "用邻接表建无向图，再用显式栈做 DFS：邻居逆序压栈、出栈时判重，既能处理环，又能得到和递归版一致的固定访问顺序。"
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
  - title: "1Point3Acres · DeepMind Android：构图与 DFS"
    url: https://www.1point3acres.com/interview/problems/ec95664e-bb65-47c5-87fb-bbedfad728d4
    type: secondary
---

## 题目

给一组无向边，先建图，再从给定起点做深度优先遍历，返回节点的访问顺序。来源帖子标注的是 DeepMind 的 Android 岗位。

> 来源：一亩三分地题目详情页（2026-10-18 读取），题面是网站从面经整理的，没有逐条核对原帖；网站收录不等于公司官方确认。这条属于 Android 岗位，不能当成 DeepMind 研究岗的题。下面的接口、约束和测试是手册补的练习约定。

## 思路

用邻接表存图，每条无向边要在两个端点各加一次。遍历时用 `seen` 集合记录已经访问过的节点，有环的图才不会无限循环。

访问顺序取决于先走哪个邻居。如果测试要求固定顺序，就要和面试官约定规则：按邻居排序，或者保留边的输入顺序。这份练习按邻居的字典序访问。

递归写法最直观，但图很深时可能超过 Python 的递归深度限制，所以参考实现用显式栈。用栈模拟递归时有两个细节：

- 邻居要逆序压栈，这样字典序最小的邻居最先出栈；
- 同一个节点可能被不同邻居压栈多次，要在出栈时判重，而不是入栈时。入栈时就标记的话，顺序会和递归版不一致：边为 a-b、a-c、b-c、b-d 时，递归版是 a, b, c, d，入栈标记版会得到 a, b, d, c。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `dfs(edges, start) -> list`：`edges` 是无向边 `(u, v)` 的列表。从 `start` 出发做 DFS，邻居按字典序访问，返回访问顺序。`start` 不在任何边里时也要访问它，结果是 `[start]`。
- 同一个参考文件里还有 `suffix_counts`、`topk`、`above` 三个函数，分别对应其他几张题卡，本题不要求实现。
- 节点可比较大小（用于排序），边数 $\le 10^5$。

### 输入输出示例

```text
dfs([("a", "b"), ("a", "c"), ("b", "c")], "a") -> ["a", "b", "c"]
dfs([("a", "c"), ("a", "b"), ("b", "d")], "a") -> ["a", "b", "d", "c"]
dfs([], "x")                                    -> ["x"]
```

第二个例子里，从 a 先走字典序更小的 b，b 再走到 d，回溯后才访问 c。

### 解题思路与正确性

栈顶永远是「递归版接下来会进入的节点」：节点出栈并首次访问时，把它未访问的邻居逆序压栈，最小的邻居就在栈顶，下一步会先展开它的整棵子树，这和递归版先递归第一个邻居的行为一致。已访问的节点出栈时直接跳过，所以每个节点只会被输出一次。

和起点不连通的节点不会出现在结果里。

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

设节点数为 V、边数为 E。建图 O(E)；每个节点展开时要给邻居排序，总共 O(E log V)。不要求固定顺序时去掉排序就是 O(V + E)。同一节点可能被压栈多次，栈最坏占 O(E) 空间。

- 要遍历整张图（含不连通部分）时，在外层对每个未访问节点调用一次 DFS。
- 要按边的输入顺序访问邻居时，把邻接表从 `set` 换成 `list`，并在压栈时逆序即可；但要注意重复边会让邻居出现多次，出栈判重可以兜住。

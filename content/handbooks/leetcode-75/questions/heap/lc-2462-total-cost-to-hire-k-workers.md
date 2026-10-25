---
id: lc-2462-total-cost-to-hire-k-workers
section: heap
order: 4
level: A
title: LC 2462 · 雇佣 K 位工人的总代价
quick: >-
  用左右两个小根堆分别装前 `candidates` 个和后 `candidates` 个工人，两个指针从两端往中间补人，每轮取最小只要对数时间。每轮比较两个堆顶，取更小的（相等取左边），弹出后从同一侧补一个。时间 $O((k+c)\log c)$，额外空间 $O(c)$。
tags:
  - Heap
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2462. Total Cost to Hire K Workers
    url: https://leetcode.com/problems/total-cost-to-hire-k-workers/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

工人按原始下标从左到右排成一列，`costs[i]` 是雇佣第 i 人的费用。进行 k 轮雇佣：每轮只能从尚未雇佣工人的最前 candidates 人和最后 candidates 人中选择，选择其中费用最低的人；费用相同则选原始下标较小者。选中后此人移出队伍，下一轮按剩余队伍重新确定候选范围。

### 输入与输出

实现 `totalCost(costs, k, candidates) -> int`，返回 k 轮的总费用。前后候选范围重叠时，同一工人只能算一个候选；剩余人数少于 candidates 时，可以考虑所有剩余工人。每个工人至多被雇佣一次。

### 约束

- `1 <= len(costs) <= 10^5`。
- `1 <= costs[i] <= 10^5`。
- `1 <= k, candidates <= len(costs)`，保证能完成 k 轮。
- 返回值可能超过32位整数范围。

### 示例

```text
输入：costs = [17,12,10,2,7,2,11,20,8], k = 3, candidates = 4
输出：11
```

[LeetCode 原题](https://leetcode.com/problems/total-cost-to-hire-k-workers/description/)

## 解题思路与参考答案

## 题意

`costs[i]` 是第 $i$ 个工人的代价。进行 $k$ 轮雇佣，每轮从剩余工人的前 `candidates` 个和后 `candidates` 个里选代价最小的，代价相同选下标更小的。被雇的人移出队伍。剩余人数少于 `2 * candidates` 时前后两组会重叠，就从全体剩余里选。返回总代价。

## 思路

我会用两个小根堆，左堆装最前面的 `candidates` 个人，右堆装最后面的 `candidates` 个人。每轮只在这两组里挑最便宜的，堆顶正好是各组的最小值。每轮线性扫两端 $2c$ 个人找最小值是 $O(k\cdot c)$，最坏到 $10^{10}$ 量级，太慢。

指针 `l`、`r` 夹住还没进任何堆的区间 $[l, r]$。哪一侧的堆被弹走一个人，就从同一侧补一个，`l` 右移或 `r` 左移。补人时要求 $l\le r$，这样左右两组不会重叠；指针交错以后中间已经没人了，两个堆合起来正好是全部剩余工人，继续比堆顶就行。平局要选下标小的，左堆里的下标全都小于右堆，所以两个堆顶相等时取左边。

拿 `costs = [17, 12, 10, 2, 7, 2, 11, 20, 8]`、$k=3$、`candidates = 4` 走一遍。左堆装 17、12、10、2，右堆装 8、20、11、2，中间只剩下标 4 的 7。第一轮两个堆顶都是 2，取左边，左堆补进 7，这时指针已经交错。第二轮左堆顶 7、右堆顶 2，取右边的 2，右侧没人可补了。第三轮左堆顶 7、右堆顶 8，取 7。总代价 $2+2+7=11$。

## 参考代码

```python
import heapq
import random
from typing import List


def totalCost(costs: List[int], k: int, candidates: int) -> int:
    l, r = 0, len(costs) - 1
    left: List[int] = []
    right: List[int] = []
    total = 0
    for _ in range(k):
        while len(left) < candidates and l <= r:
            heapq.heappush(left, costs[l])
            l += 1
        while len(right) < candidates and l <= r:
            heapq.heappush(right, costs[r])
            r -= 1
        if right and (not left or right[0] < left[0]):
            total += heapq.heappop(right)
        else:
            total += heapq.heappop(left)
    return total


def simulate(costs: List[int], k: int, candidates: int) -> int:
    workers = list(costs)
    total = 0
    for _ in range(k):
        n = len(workers)
        pool = set(range(min(candidates, n))) | set(range(max(0, n - candidates), n))
        best = min(pool, key=lambda i: (workers[i], i))
        total += workers.pop(best)
    return total


if __name__ == "__main__":
    assert totalCost([17, 12, 10, 2, 7, 2, 11, 20, 8], 3, 4) == 11
    assert totalCost([1, 2, 4, 1], 3, 3) == 4
    assert totalCost([5], 1, 1) == 5
    assert totalCost([3, 3, 3, 3], 4, 1) == 12
    random.seed(1)
    for _ in range(300):
        n = random.randint(1, 10)
        costs = [random.randint(1, 6) for _ in range(n)]
        k = random.randint(1, n)
        c = random.randint(1, n)
        assert totalCost(costs, k, c) == simulate(costs, k, c)
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert totalCost([17, 12, 10, 2, 7, 2, 11, 20, 8], 3, 4) == 11
assert totalCost([1, 2, 4, 1], 3, 3) == 4
assert totalCost([5], 1, 1) == 5
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

初始建堆最多 $2c$ 次入堆，之后每轮一次出堆、至多一次入堆，时间 $O((k+c)\log c)$，$c$ 为 `candidates`。额外空间 $O(c)$。

## 边界

$2c\ge n$ 的时候，第一轮左堆装满后 `l` 和 `r` 就交错了，右堆可能是空的或者很少，比较堆顶时要处理某一侧为空。

左右堆顶相等时取左，因为左侧下标更小；同一个堆里的平局不影响总代价。

$k=n$ 时所有人都会被雇，答案等于 `sum(costs)`，可以拿来自检。

## 追问

**要返回被雇工人的下标怎么办？**
堆里改存 `(cost, index)`。元组比较会先比代价再比下标，平局规则直接由元组保证，两个堆顶之间也改成比较元组。

**一个堆行不行？**
能做，但麻烦一些。一个堆存所有候选时，弹出一个人后不知道该从哪一侧补人；存 `(cost, index)` 再按下标判断属于左组还是右组也可以，两个堆更直观。这题和 `lc-215-kth-largest-element-in-an-array` 一样，都是用堆把「每轮取最小」从线性降到对数。

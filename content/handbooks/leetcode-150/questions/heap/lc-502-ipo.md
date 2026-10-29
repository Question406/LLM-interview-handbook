---
id: lc-502-ipo
section: heap
order: 2
level: A
title: LC 502 · IPO
quick: 项目按启动资本排序，资本够得着的项目把利润放进大根堆，每次取堆顶利润最大的来做，最多做 $k$ 次。每个项目进出堆一次，时间 $O(n\log n)$。
tags:
  - Heap
  - Greedy
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 502. IPO
    url: 'https://leetcode.cn/problems/ipo/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

有 n 个项目，第 i 个项目要求当前资本至少为 `capital[i]`，完成后获得纯利润 `profits[i]`。初始资本为 w，最多选择 k 个不同项目，项目按先后次序完成，每个项目最多一次。项目的启动资本只是进入 threshold，不会从资本中扣除；完成后把利润加入现有资本。求最大最终资本。

### 接口与输出

实现 `findMaximizedCapital(k: int, w: int, profits: List[int], capital: List[int]) -> int`。返回结束时的资本总额，而非仅返回新增利润。项目数可以少于 k。

### 合法输入与约束

`1 <= n,k <= 100000`，`0 <= w, capital[i] <= 10^9`，`0 <= profits[i] <= 10000`，profits 与 capital 等长。只能选择当前资本满足要求的项目。

### 示例

```text
输入：k = 2, w = 0, profits = [1,2,3], capital = [0,1,1]
输出：4
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/ipo/description/)。

## 解题思路与参考答案

## 题意

$n$ 个项目，启动资本是 `capital[i]`，做完后利润 `profits[i]` 加进当前资本。初始资本为 $w$，最多做 $k$ 个，求最终资本。

## 思路

我会用贪心：在当前资本能启动的项目里，挑利润最大的那个做。实现上先把项目按资本升序排好，用指针把所有 `capital <= w` 的项目利润推进堆里（取负放进小根堆当大根堆）。每轮弹出堆顶，$w$ 加上这个利润，再用指针解锁新的项目。堆空了说明做不下去了。

拿第一个例子 $k=2$、$w=0$、`profits=[1,2,3]`、`capital=[0,1,1]` 走一遍：资本 0 只能做第一个项目，利润 1，$w$ 变成 1；这下后两个都解锁了，挑利润 3 的那个，$w$ 变成 4。

常见误区是每轮都扫描全部没做的项目，那是 $O(kn)$；排序加指针就不用重扫。

## 参考代码

```python
import heapq
from typing import List


def findMaximizedCapital(k: int, w: int, profits: List[int], capital: List[int]) -> int:
    projects = sorted(zip(capital, profits))
    heap = []
    i, n = 0, len(projects)
    for _ in range(k):
        while i < n and projects[i][0] <= w:
            heapq.heappush(heap, -projects[i][1])
            i += 1
        if not heap:
            break
        w += -heapq.heappop(heap)
    return w


if __name__ == "__main__":
    assert findMaximizedCapital(2, 0, [1, 2, 3], [0, 1, 1]) == 4
    assert findMaximizedCapital(3, 0, [1, 2, 3], [0, 1, 2]) == 6
    assert findMaximizedCapital(1, 0, [1, 2, 3], [1, 1, 2]) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

如果题目允许答案以任意顺序返回，先排序或转成集合再比较；只有题目保证没有重复结果时才适合直接用集合，否则还要检查重复次数。

```python
assert findMaximizedCapital(2, 0, [1, 2, 3], [0, 1, 1]) == 4
assert findMaximizedCapital(3, 0, [1, 2, 3], [0, 1, 2]) == 6
assert findMaximizedCapital(1, 0, [1, 2, 3], [1, 1, 2]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

排序 $O(n\log n)$，每个项目进出堆一次也是 $O(n\log n)$，额外空间 $O(n)$。

## Edge Cases

初始资本一个项目都做不了时，第一轮解锁循环不进，堆是空的，直接返回 $w$。$k$ 比能做的项目数还大时，某一轮堆空就 `break`，不会空弹。利润为 $0$ 的项目仍可能解锁后续资本更高的项目，该做还是做，只是 $w$ 不变。

## 追问

**每个项目只能做一次，这个写法保证了吗？**
保证了。按资本排序后指针 `i` 只增不减，每个项目的利润最多入堆一次，弹出就等于「做完」。如果每次都从全部未做项目里重扫，是 $O(kn)$，实现上也容易重复选。

```python
# 指针 i 只前进：projects[i] 入堆后不会再看
while i < n and projects[i][0] <= w:
    heapq.heappush(heap, -projects[i][1])
    i += 1
```

**如果项目有截止日期呢？**
这题没有时间维度，资本够就能做。要是每个项目占 $1$ 单位时间、有截止时刻 $d_i$，就变成「带截止的单位时间调度」：按截止升序扫，小根堆里放已选项目的利润；当前截止之前还塞得下就做，塞不下时如果当前利润大于堆里最小的利润，就替换掉它。这时堆的键是利润，跟资本无关。更一般的「时长 $+ $ 截止 $+ $ 利润」是加权区间调度，要按截止做 DP，这套贪心就不适用了。

```python
def maxProfitWithDeadline(jobs):
    # jobs: (deadline, profit)，每个占时 1，时间从 1 计
    jobs = sorted(jobs)
    heap = []
    for d, p in jobs:
        heapq.heappush(heap, p)
        if len(heap) > d:
            heapq.heappop(heap)
    return sum(heap)
```

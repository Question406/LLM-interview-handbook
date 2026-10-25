---
id: lc-216-combination-sum-iii
section: backtracking
order: 2
level: A
title: LC 216 · 组合总和 III
quick: >-
  回溯从 $1$ 到 $9$ 里选 $k$ 个不同的数凑出和 $n$：下一层只从更大的数开始，天然去重；剩余和放不下或数字不够就剪枝。搜索空间最多 $\binom{9}{k}$，时间 $O(\binom{9}{k}\cdot k)$，额外空间 $O(k)$。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 216. Combination Sum III
    url: https://leetcode.com/problems/combination-sum-iii/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

从整数 1 到 9 中选取恰好 k 个互不相同的数，使这些数的和为 n，返回所有这样的组合。同一组数的不同排列属于同一个组合，不能重复返回。

### 接口与输出

实现 `combinationSum3(k: int, n: int) -> List[List[int]]`。每个结果必须包含恰好 k 个数，每个数最多使用一次；结果组合之间的顺序不限。无解时返回空列表。

### 合法输入与约束

`2 <= k <= 9`，`1 <= n <= 60`。不能使用 0、负数或大于 9 的数，也不能为了凑和重复使用同一个数。

### 示例

```text
输入：k = 3, n = 7
输出：[[1,2,4]]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/combination-sum-iii/description/)。

## 解题思路与参考答案

## 题意

找出所有由 $k$ 个数组成、和为 $n$ 的组合：只能用 $1$ 到 $9$，每个数最多用一次。返回组合列表，组合之间顺序任意，同一组合不能重复出现。约束 $2\le k\le 9$，$1\le n\le 60$。

## 思路

我会用回溯，并且每层只往更大的数枚举，这样每个组合只会以升序出现一次，不用另外去重。`dfs(start, remain)` 从 `start` 到 $9$ 枚举下一个数 $x$，放进路径后递归 `dfs(x + 1, remain - x)`。路径长度到 $k$ 时检查 `remain == 0` 再收。

拿 $k=3, n=9$ 走一遍：先选 1、2，剩 6，第三个数取 6，收下 `[1, 2, 6]`；回退换成 1、3，剩 5，收下 `[1, 3, 5]`；1、4 之后剩 4，第三个数至少是 5，放不下；从 2 开始还能凑出 `[2, 3, 4]`。

剪枝有两条。数是升序枚举的，$x \gt remain$ 以后更大的数也放不下，直接 `break`；剩下能选的数不够凑满 $k$ 个，也提前停。

暴力做法是枚举 $2^9=512$ 个子集再筛，规模这么小其实也能过，但回溯的写法能直接套到 LC 39 / 40 这类候选集更大的题上。

## 参考代码

```python
from typing import List


def combinationSum3(k: int, n: int) -> List[List[int]]:
    ans: List[List[int]] = []
    path: List[int] = []

    def dfs(start: int, remain: int) -> None:
        if len(path) == k:
            if remain == 0:
                ans.append(path[:])
            return
        for x in range(start, 10):
            if x > remain:
                break
            if 9 - x + 1 < k - len(path):
                break
            path.append(x)
            dfs(x + 1, remain - x)
            path.pop()

    dfs(1, n)
    return ans


if __name__ == "__main__":
    assert sorted(combinationSum3(3, 7)) == [[1, 2, 4]]
    assert sorted(combinationSum3(3, 9)) == [[1, 2, 6], [1, 3, 5], [2, 3, 4]]
    assert combinationSum3(4, 1) == []
    assert combinationSum3(9, 45) == [[1, 2, 3, 4, 5, 6, 7, 8, 9]]
    assert combinationSum3(2, 18) == []
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

如果题目允许答案以任意顺序返回，先排序或转成集合再比较；只有题目保证没有重复结果时才适合直接用集合，否则还要检查重复次数。

```python
assert sorted(combinationSum3(3, 7)) == [[1, 2, 4]]
assert sorted(combinationSum3(3, 9)) == [[1, 2, 6], [1, 3, 5], [2, 3, 4]]
assert combinationSum3(4, 1) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

最多枚举 $\binom{9}{k}$ 个组合，每个收集时拷贝 $O(k)$，时间 $O(\binom{9}{k}\cdot k)$，上界是常数级。额外空间 $O(k)$，是递归栈和路径，输出另计。

## 边界

- $n$ 太小、凑不出 $k$ 个不同数时，比如 $k=4, n=1$，返回 `[]`。
- $n$ 太大、超过 $9+8+\dots$ 能凑出的最大和时，同样返回 `[]`，剪枝会让搜索很快结束。
- $k=9$ 时只能全选，和必须是 $45$。

## 追问

**不用回溯，用位掩码怎么做？**
枚举 $0$ 到 $2^9-1$ 的每个 mask，第 $i$ 位为 $1$ 表示选了 $i+1$，`popcount == k` 且和为 $n$ 就收。时间 $O(2^9\cdot 9)$，写起来更短，但不好推广到更大的候选集。

```python
def combinationSum3Mask(k, n):
    ans = []
    for mask in range(1 << 9):
        if bin(mask).count("1") != k:
            continue
        nums = [i + 1 for i in range(9) if mask >> i & 1]
        if sum(nums) == n:
            ans.append(nums)
    return ans
```

**候选数可以重复使用（LC 39）呢？**
递归时下一层从 $x$ 本身开始，不再从 $x+1$ 开始，终止条件改成 `remain == 0`，其余骨架不变。

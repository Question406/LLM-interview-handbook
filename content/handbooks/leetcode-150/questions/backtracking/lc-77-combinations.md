---
id: lc-77-combinations
section: backtracking
order: 2
level: A
title: LC 77 · 组合
quick: "用回溯按升序选，下一层从 $i+1$ 开始，这样每个组合只生成一次。剩余名额不够时提前剪枝。时间 $O(\\binom{n}{k}\\cdot k)$。"
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 77. 组合
    url: https://leetcode.cn/problems/combinations/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

从整数 1 到 n 中选出 k 个不同的数，返回所有不同的选择。组合不考虑选取顺序，例如 [1,2] 与 [2,1] 是同一种组合，不能重复返回。

### 输入与输出

实现 `combine(n, k) -> list[list[int]]`。每个内部列表表示一个含 k 个不同整数的组合；外部列表顺序不限。

### 约束与约定

- `1 <= n <= 20`。
- `1 <= k <= n`；每个被选数字都属于闭区间 `[1,n]`。

### 示例

```text
输入：n = 4, k = 2
输出：[[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]
```

从 1 到 4 选两个数，共有六种组合。

[官方原题与完整题面](https://leetcode.com/problems/combinations/description/)。

## 解题思路与参考答案

## 题意

给定 $n$ 与 $k$，返回 $[1,n]$ 中所有长度为 $k$ 的组合。组合与顺序无关，$[1,2]$ 与 $[2,1]$ 算同一个。

## 思路

我会回溯，并记录下一次可选的起点 `start`。本层枚举 $i\in[start,n]$，选了 $i$ 之后，下一层只从 $i+1$ 往后选，所以每条组合都是升序生成的，不会同时出现 `[1,2]` 和 `[2,1]`。路径长度到 $k$ 就存一份。用全排列再排序去重会做很多无用功。

拿 $n=4,k=2$ 看。选 1 之后下一层在 2、3、4 里选，得到 `[1,2]`、`[1,3]`、`[1,4]`；选 2 之后只能在 3、4 里选；选 3 之后只剩 4。第一层选 4 就不用试了，后面没有数能凑够两个。这就是剪枝：还要 $need$ 个数时，$i$ 最大只能到 $n-need+1$，再往后凑不齐。

和 LC 46 对比，组合的下标只往前走，排列靠 `used`。

## 参考代码

```python
from typing import List


def combine(n: int, k: int) -> List[List[int]]:
    ans = []
    path = []

    def dfs(start: int) -> None:
        if len(path) == k:
            ans.append(path[:])
            return
        need = k - len(path)
        for i in range(start, n - need + 2):
            path.append(i)
            dfs(i + 1)
            path.pop()

    dfs(1)
    return ans


if __name__ == "__main__":
    assert combine(4, 2) == [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
    assert combine(1, 1) == [[1]]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert combine(4, 2) == [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
assert combine(1, 1) == [[1]]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\binom{n}{k}\cdot k)$，空间 $O(k)$ 加输出。

## 边界

$k=1$ 时答案是 `[1]..[n]` 各一个。$k=n$ 时只有 `[1,2,...,n]` 一条。$n=k=1$ 时是 `[[1]]`。这些情况下剪枝上界 `n-need+1` 都不会把区间剪空。

## 追问

**变成组合总和怎么改？**
那就是 LC 39，独立卡 `lc-39-combination-sum`。选的是数组里的值，要带剩余量 `remain`；每个数能再用，下一层还从 $i$ 开始，不能再用就从 $i+1$。本题没有 `target`，剪枝只看剩余名额够不够。

**允许重复选，或者输入里有重复值呢？**
这是两件不同的事。同一元素能用无限次（可重复组合）时，下一层起点还是 $i$，相当于 LC 39 去掉目标和、改成长度 $k$。输入数组本身有重复值、组合要去重时，先排序，同层 `i>start` 且 `nums[i]==nums[i-1]` 就跳过，下一层仍从 $i+1$ 开始，每个下标最多用一次。

```python
def combineRepeat(n, k):
    """1..n，同一数字可重复，组合长度 k。"""
    ans, path = [], []

    def dfs(start):
        if len(path) == k:
            ans.append(path[:])
            return
        for i in range(start, n + 1):
            path.append(i)
            dfs(i)
            path.pop()

    dfs(1)
    return ans


def combineDup(nums, k):
    """nums 含重复值，组合去重。"""
    nums.sort()
    ans, path = [], []

    def dfs(start):
        if len(path) == k:
            ans.append(path[:])
            return
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            dfs(i + 1)
            path.pop()

    dfs(0)
    return ans
```

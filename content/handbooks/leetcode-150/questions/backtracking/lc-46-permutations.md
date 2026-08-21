---
id: lc-46-permutations
section: backtracking
order: 3
level: S
title: LC 46 · 全排列
quick: >-
  回溯 + `used`（或交换原地）。每次从未用过的数里选一个，路径长度为 $n$
  就收一份。时间 $O(n\cdot n!)$。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 46. 全排列
    url: https://leetcode.cn/problems/permutations/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

互不相同的整数数组 `nums`，返回所有可能的全排列。

## 思路

回溯：路径存已选，`used[i]` 标记 `nums[i]` 是否在路径里。本层扫一遍数组，没用过的就选上、递归、再撤销。路径长度到 $n$ 拷一份进答案。

交换写法：下标 `i` 与 `[i,n)` 每个位置交换后递归 `i+1`，回来换回去。少开 `used`，但更绕。本题无重复值，不必排序去重；有重复见 LC 47。

## 参考代码

```python
from typing import List


def permute(nums: List[int]) -> List[List[int]]:
    ans = []
    used = [False] * len(nums)
    path = []

    def dfs() -> None:
        if len(path) == len(nums):
            ans.append(path[:])
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True
            path.append(x)
            dfs()
            path.pop()
            used[i] = False

    dfs()
    return ans


if __name__ == "__main__":
    assert permute([1, 2, 3]) == [
        [1, 2, 3],
        [1, 3, 2],
        [2, 1, 3],
        [2, 3, 1],
        [3, 1, 2],
        [3, 2, 1],
    ]
    assert permute([0, 1]) == [[0, 1], [1, 0]]
    assert permute([1]) == [[1]]
    print("ok")
```

## 复杂度

时间 $O(n\cdot n!)$（每个排列拷贝 $n$），额外空间 $O(n)$（`used` + 栈）。

## 边界

- $n=1$：答案就是 `[[nums[0]]]`。
- 含负数 / $0$：值不参与运算，当普通元素即可。
- $n$ 较大（如 $n \gt 10$）：$n!$ 爆炸，面试只问复杂度 $O(n\cdot n!)$，不要硬优化爆搜。组合（与顺序无关）见 LC 77，独立卡 `lc-77-combinations`。

## 追问

- **有重复值、要去重排列（LC 47）？** 先排序，让相同值相邻。本层枚举时：`used[i]` 已占用则跳；若 `i>0` 且 `nums[i]==nums[i-1]` 且 **`used[i-1]` 为假**，说明同一层里前一个相同值没选、当前再选会得到同一排列，跳过。相对本题只多这一句剪枝。

```python
def permuteUnique(nums):
    nums.sort()
    ans, path = [], []
    used = [False] * len(nums)

    def dfs():
        if len(path) == len(nums):
            ans.append(path[:])
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue
            used[i] = True
            path.append(x)
            dfs()
            path.pop()
            used[i] = False

    dfs()
    return ans
```

- **只要第 $k$ 个排列（LC 60）？** 不必生成 $n!$ 个串。数字为 $1..n$，按字典序。第 $1$ 位：剩下 $n-1$ 个数有 $(n-1)!$ 种排法，下标 $\lfloor (k-1)/(n-1)! \rfloor$ 就是该位该选的数，然后 $k \leftarrow (k-1)\bmod (n-1)!$，从剩余数字里删掉它，继续下一位。时间 $O(n^2)$（每次从 list 按下落）。

```python
from math import factorial

def getPermutation(n, k):
    nums = list(range(1, n + 1))
    k -= 1
    ans = []
    for i in range(n, 0, -1):
        f = factorial(i - 1)
        idx, k = divmod(k, f)
        ans.append(str(nums.pop(idx)))
    return "".join(ans)
```

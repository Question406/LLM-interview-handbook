---
id: lc-46-permutations
section: backtracking
order: 3
level: S
title: LC 46 · 全排列
quick: 用回溯加 `used` 数组（或原地交换）。每一层从没用过的数里选一个，路径长度到 $n$ 就收一份。时间 $O(n\cdot n!)$。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 46. 全排列
    url: 'https://leetcode.cn/problems/permutations/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一个元素互不相同的整数数组，返回这些元素的所有全排列。每个排列必须恰好使用数组里的每个元素一次，不得遗漏或重复输出相同排列。

### 输入与输出

实现 `permute(nums: List[int]) -> List[List[int]]`。每个内层列表是一种排列，外层列表的顺序不限。

### 约束

- `1 <= len(nums) <= 6`。
- `-10 <= nums[i] <= 10`，所有元素互不相同。

### 示例

```text
输入：nums = [1,2,3]
输出：[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
```

## 解题思路与参考答案

## 题意

互不相同的整数数组 `nums`，返回所有可能的全排列。

## 思路

我会用回溯，路径存已经选的数，`used[i]` 标记 `nums[i]` 在不在路径里。每一层扫一遍数组，没用过的就选上、递归、再撤销；路径长度到 $n$，拷一份进答案。

拿 `[1,2,3]` 看。第一层选 1，第二层只能在 2、3 里选，选 2 后第三层只剩 3，收 `[1,2,3]`；撤销回来改选 3，再收 `[1,3,2]`。然后第一层换成 2、再换成 3，一共 6 条，顺序和测试里一样。

还有一种交换写法，下标 `i` 依次和 `[i,n)` 里每个位置交换，递归 `i+1`，回来再换回去。它省掉 `used`，但更绕。本题没有重复值，不用排序去重；有重复是 LC 47。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
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
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n\cdot n!)$，每个排列要拷贝 $n$ 个数；额外空间 $O(n)$，是 `used` 加递归栈。

## Edge Cases

$n=1$ 时答案就是 `[[nums[0]]]`。含负数或 $0$ 也没关系，值不参与运算，当普通元素处理。$n$ 较大（如 $n \gt 10$）时 $n!$ 会爆炸，白板上只会问复杂度 $O(n\cdot n!)$，不用硬去优化爆搜。和顺序无关的组合是 LC 77，独立卡 `lc-77-combinations`。

## 追问

**有重复值、要去重排列（LC 47）怎么改？**
先排序，让相同值相邻，然后只比本题多一句剪枝。本层枚举时，`used[i]` 已占用就跳；如果 `i>0` 且 `nums[i]==nums[i-1]` 且 `used[i-1]` 为假，说明同一层里前一个相同的值没选，当前再选会得到同一个排列，也跳过。

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

**只要第 $k$ 个排列（LC 60）呢？**
不用生成 $n!$ 个串，一位一位算。数字是 $1..n$，按字典序排。看第 $1$ 位，剩下 $n-1$ 个数有 $(n-1)!$ 种排法，所以下标 $\lfloor (k-1)/(n-1)! \rfloor$ 就是这一位该选的数；然后 $k \leftarrow (k-1)\bmod (n-1)!$，从剩余数字里删掉它，继续下一位。时间 $O(n^2)$，因为每次按下标从 list 里删元素要移动后面的元素。

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

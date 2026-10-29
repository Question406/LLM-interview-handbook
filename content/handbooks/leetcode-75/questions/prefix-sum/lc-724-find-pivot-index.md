---
id: lc-724-find-pivot-index
section: prefix-sum
order: 2
level: S
title: LC 724 · 寻找数组的中心下标
quick: >-
  右侧和可以由总和推出来，所以先求总和 `total`，从左扫时维护左侧和 `left`，右侧和就是 `total - left -
  nums[i]`，相等即返回，第一个命中的就是最左的 $i$。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Prefix Sum
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 724. Find Pivot Index
    url: 'https://leetcode.com/problems/find-pivot-index/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定整数数组，寻找一个中心下标，使严格位于它左侧的所有元素之和等于严格位于它右侧的所有元素之和。下标对应的元素本身不计入任何一侧；某侧没有元素时，该侧的和为 0。

### 输入与输出

实现 `pivotIndex(nums) -> int`。下标从 0 开始，若存在多个中心下标，返回最小者；不存在时返回 -1。数组元素可以为负数或 0。

### 约束与约定

- `1 <= len(nums) <= 10000`。
- `-1000 <= nums[i] <= 1000`。

### 示例

```text
输入：nums = [1,7,3,6,5,6]
输出：3
```

示例下标 3 左边的和为 1+7+3=11，右边为 5+6=11，故返回 3。

[官方原题与完整题面](https://leetcode.com/problems/find-pivot-index/description/)。

## 解题思路与参考答案

## 题意

中心下标 $i$ 满足：严格在它左边的元素之和等于严格在它右边的元素之和，`nums[i]` 本身不算。左端 $i=0$ 时左侧和为 $0$，右端同理。返回最靠左的中心下标，没有返回 $-1$。$n \le 10^4$，元素可正可负。

## 思路

我会先求总和，再从左扫一遍维护左侧和，因为右侧和可以直接推出来：$\text{right} = \text{total} - \text{left} - nums[i]$。每个位置先判 `left == total - left - nums[i]`，再把 `nums[i]` 加进 `left`。先判后加，保证 `left` 不含自己。从左往右第一个命中的就是最左答案。对每个 $i$ 分别求左右和是 $O(n^2)$。

拿 `[1, 7, 3, 6, 5, 6]` 走一遍，`total = 28`。下标 0 时左边 0、右边 27；下标 1 时左边 1、右边 20；下标 2 时左边 8、右边 17；下标 3 时左边 11、右边 $28-11-6=11$，相等，返回 3。

元素有负数，左右和不单调，别想着用二分或双指针往中间逼，只能线性扫。

## 参考代码

```python
from typing import List


def pivotIndex(nums: List[int]) -> int:
    total = sum(nums)
    left = 0
    for i, x in enumerate(nums):
        if left == total - left - x:
            return i
        left += x
    return -1


if __name__ == "__main__":
    assert pivotIndex([1, 7, 3, 6, 5, 6]) == 3
    assert pivotIndex([1, 2, 3]) == -1
    assert pivotIndex([2, 1, -1]) == 0
    assert pivotIndex([0]) == 0
    assert pivotIndex([-1, -1, 0, 1, 1, 0]) == 5
    assert pivotIndex([0, 0, 0]) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert pivotIndex([1, 7, 3, 6, 5, 6]) == 3
assert pivotIndex([1, 2, 3]) == -1
assert pivotIndex([2, 1, -1]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，两遍扫描。额外空间 $O(1)$。

## Edge Cases

答案可能在最左端。`[2, 1, -1]` 右侧和为 $0$，左侧空和也是 $0$，返回 $0$。

答案在最右端时右侧空和为 $0$，公式里 `total - left - x` 自然给出 $0$。

有多个中心下标时，比如全 $0$，返回第一个。

## 追问

**不排除 `nums[i]`，改成把数组切成两段和相等（切点在两元素之间）呢？**
条件变成 `left == total - left`，即 `2 * left == total`，这里 `left` 包含到切点为止的元素。`total` 为奇数时可以直接判无解。时间 $O(n)$，额外空间 $O(1)$。

```python
def splitPoint(nums):
    total = sum(nums)
    left = 0
    for i in range(len(nums) - 1):
        left += nums[i]
        if 2 * left == total:
            return i + 1
    return -1
```

**要多次查询任意区间的和呢？**
开前缀和数组 `pre`，`pre[0] = 0`、`pre[i+1] = pre[i] + nums[i]`，区间 `[l, r]` 的和是 `pre[r+1] - pre[l]`。预处理 $O(n)$，单次查询 $O(1)$。本题只是其中一个特例，用滚动变量省掉了数组。

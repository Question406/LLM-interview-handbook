---
id: lc-2300-successful-pairs-of-spells-and-potions
section: binary-search
order: 2
level: A
title: LC 2300 · 咒语和药水的成功对数
quick: >-
  药水排序后二分：对每个咒语 $s$ 算出最小合格强度 $\lceil success/s\rceil$，用 `bisect_left` 找第一个不小于它的位置，后面的药水全部成功。时间 $O((n+m)\log m)$，额外空间 $O(m)$。
tags:
  - Binary Search
  - Sorting
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2300. Successful Pairs of Spells and Potions
    url: https://leetcode.com/problems/successful-pairs-of-spells-and-potions/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定咒语强度数组 `spells`、药水强度数组 `potions` 和阈值 `success`。咒语 i 与药水 j 组成一对，当且仅当二者强度之积不小于 success 时，这一对算成功。请分别统计每个咒语能与多少瓶药水组成成功对。

### 输入与输出

实现 `successfulPairs(spells, potions, success) -> List[int]`，返回长度等于 len(spells) 的列表，结果第 i 项对应原来的咒语 i。每瓶药水按其位置计数，相同强度的多瓶分别计入；每个咒语独立统计，不会消耗药水。

### 约束

- `1 <= len(spells), len(potions) <= 10^5`。
- `1 <= spells[i], potions[j] <= 10^5`。
- `1 <= success <= 10^10`；乘积及阈值可能超过32位整数范围。

### 示例

```text
输入：spells = [5,1,3], potions = [1,2,3,4,5], success = 7
输出：[4,0,3]
```

[LeetCode 原题](https://leetcode.com/problems/successful-pairs-of-spells-and-potions/description/)

## 解题思路与参考答案

## 题意

`spells` 长度 $n$，`potions` 长度 $m$，都是正整数。咒语 $i$ 和药水 $j$ 的乘积 `spells[i] * potions[j]` 不小于 `success` 就算一对成功。返回长度 $n$ 的数组，第 $i$ 个是咒语 $i$ 能与多少瓶药水成功配对。$n, m\le 10^5$，`success` 最大 $10^{10}$。

## 思路

我会把药水排序，再对每个咒语二分。固定咒语后，药水越强越容易成功，合格的药水正好是排序后的一段后缀，只要找到后缀起点就行。成功条件 $s\cdot p\ge success$ 等价于 $p\ge \lceil success/s\rceil$，整数上取整写成 `(success + s - 1) // s`，然后 `bisect_left` 找第一个不小于它的下标 `i`，答案是 $m-i$。

拿 `spells = [5, 1, 3]`、`potions = [1, 2, 3, 4, 5]`、`success = 7` 走一遍：咒语 5 需要强度至少 $\lceil 7/5\rceil=2$，从下标 1 起都行，4 瓶；咒语 1 需要 7，超过最大药水，0 瓶；咒语 3 需要 3，从下标 2 起，3 瓶。答案是 `[4, 0, 3]`。

阈值用整数算，避开浮点除法，免得在 $10^{10}$ 量级下出精度问题。暴力两重循环是 $O(nm)$，也就是 $10^{10}$ 次，会超时。

## 参考代码

```python
from bisect import bisect_left
from typing import List


def successfulPairs(spells: List[int], potions: List[int], success: int) -> List[int]:
    potions = sorted(potions)
    m = len(potions)
    ans = []
    for s in spells:
        need = (success + s - 1) // s
        ans.append(m - bisect_left(potions, need))
    return ans


if __name__ == "__main__":
    assert successfulPairs([5, 1, 3], [1, 2, 3, 4, 5], 7) == [4, 0, 3]
    assert successfulPairs([3, 1, 2], [8, 5, 8], 16) == [2, 0, 2]
    assert successfulPairs([1], [1], 1) == [1]
    assert successfulPairs([1], [1], 2) == [0]
    assert successfulPairs([10**5], [10**5], 10**10) == [1]
    assert successfulPairs([4, 4], [2, 2, 3, 3], 8) == [4, 4]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert successfulPairs([5, 1, 3], [1, 2, 3, 4, 5], 7) == [4, 0, 3]
assert successfulPairs([3, 1, 2], [8, 5, 8], 16) == [2, 0, 2]
assert successfulPairs([1], [1], 1) == [1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

排序 $O(m\log m)$，每个咒语一次二分 $O(\log m)$，总时间 $O((n+m)\log m)$。额外空间 $O(m)$ 存排序后的副本（不计答案）。

## 边界

- 乘积恰好等于 `success` 也算成功，所以用 `bisect_left`；用 `bisect_right` 会漏掉强度正好等于阈值的药水。
- 阈值大于最大药水时，`bisect_left` 返回 $m$，答案是 $0$。
- 阈值小于等于最小药水时返回 $0$，全部 $m$ 瓶都成功。

## 追问

**不用二分可以吗？**
可以，用双指针。把咒语也按值排序并记住原下标，咒语从小到大时阈值单调不增，药水指针从右往左只会左移。总共 $O(n\log n + m\log m)$，扫描部分是线性的。

```python
def successfulPairsTwoPointers(spells, potions, success):
    potions = sorted(potions)
    order = sorted(range(len(spells)), key=lambda i: spells[i])
    ans = [0] * len(spells)
    j = len(potions)
    for i in order:
        while j > 0 and spells[i] * potions[j - 1] >= success:
            j -= 1
        ans[i] = len(potions) - j
    return ans
```

**为什么不直接用浮点 `success / s`？**
边界容易差一。值到 $10^{10}$ 时浮点仍能精确表示，但除法结果可能有舍入，和整数比较时边界容易错。整数上取整，或者直接比较乘积，最稳。

---
id: lc-1431-kids-with-the-greatest-number-of-candies
section: array-string
order: 3
level: A
title: LC 1431 · 拥有最多糖果的孩子
quick: "先求原数组最大值 `mx`，再逐个判断 `candies[i] + extraCandies >= mx`。给一个孩子加糖时其他人不变，所以只用和原最大值比。时间 $O(n)$，不算答案额外空间 $O(1)$。"
tags:
  - Array
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1431. Kids With the Greatest Number of Candies
    url: https://leetcode.com/problems/kids-with-the-greatest-number-of-candies/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

有 n 个孩子，第 i 个孩子现在有 candies[i] 颗糖，另有 extraCandies 颗额外糖果。对每个孩子分别考虑：如果把所有额外糖果都给这个孩子，他的糖果数能否达到所有孩子中的最大值？并列最多也算满足。

### 输入与输出

实现 `kidsWithCandies(candies: List[int], extraCandies: int) -> List[bool]`。返回长度为 n、与孩子下标一一对应的布尔列表。每项是独立假设，不是把同一批额外糖果连续发给所有孩子，也不需要实际修改 candies。

### 约束

- `2 <= n <= 100`，`1 <= candies[i] <= 100`。
- `1 <= extraCandies <= 50`。

### 示例

```text
输入：candies = [2,3,5,1,3], extraCandies = 3
输出：[true,true,true,false,true]
```

## 解题思路与参考答案

## 题意

`candies[i]` 是第 $i$ 个孩子的糖果数，另有 `extraCandies` 颗额外糖果。对每个孩子判断：把额外糖果全给他后，他的糖果数是否不少于所有孩子（并列也算最多）。返回布尔数组。$2 \le n \le 100$。

## 思路

这题扫两遍就够：先求原数组的最大值 `mx`，再看每个孩子加上额外糖果后是否 `>= mx`。只和原最大值比，是因为给第 $i$ 个孩子加糖时，其他人的数量都没变。

用示例 `[2, 3, 5, 1, 3]`、`extraCandies = 3` 走一遍：`mx = 5`，每人加 3 之后是 5、6、8、4、6，只有 4 小于 5，所以答案是 `[True, True, True, False, True]`。

每个孩子都重新求一次「加完后的最大值」是 $O(n^2)$，没有必要。条件用 `>=`，因为并列也算最多。

## 参考代码

```python
from typing import List


def kidsWithCandies(candies: List[int], extraCandies: int) -> List[bool]:
    mx = max(candies)
    return [c + extraCandies >= mx for c in candies]


if __name__ == "__main__":
    assert kidsWithCandies([2, 3, 5, 1, 3], 3) == [True, True, True, False, True]
    assert kidsWithCandies([4, 2, 1, 1, 2], 1) == [True, False, False, False, False]
    assert kidsWithCandies([12, 1, 12], 10) == [True, False, True]
    assert kidsWithCandies([1, 1], 0) == [True, True]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert kidsWithCandies([2, 3, 5, 1, 3], 3) == [True, True, True, False, True]
assert kidsWithCandies([4, 2, 1, 1, 2], 1) == [True, False, False, False, False]
assert kidsWithCandies([12, 1, 12], 10) == [True, False, True]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，两遍扫描。除答案外额外空间 $O(1)$。

## 边界

`extraCandies` 为 $0$ 时，只有原本就等于最大值的孩子为真。

多个孩子并列最大，他们都为真，因为比较用的是 `>=`。

所有人糖果一样多，全部为真。

## 追问

**同一个数组要回答很多个不同的 `extra`，每次只问「有几个孩子能成为最多」，怎么办？**
先排序，再对每个 `extra` 二分。找到第一个 `c >= mx - extra` 的位置，个数就是 $n$ 减去这个位置。预处理 $O(n\log n)$，单次查询 $O(\log n)$。

```python
from bisect import bisect_left


def countKids(candies, extras):
    a = sorted(candies)
    mx = a[-1]
    return [len(a) - bisect_left(a, mx - e) for e in extras]
```

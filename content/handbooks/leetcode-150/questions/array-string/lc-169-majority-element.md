---
id: lc-169-majority-element
section: array-string
order: 5
level: S
title: LC 169 · 多数元素
quick: "Boyer-Moore 投票维护一个候选元素和计数：遇到相同元素加一，不同元素减一，归零时换候选。超过半数的元素抵消后一定留下。时间 $O(n)$，额外空间 $O(1)$；也可以排序或哈希计数。"
tags:
  - Array
  - Boyer-Moore
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 169. 多数元素
    url: https://leetcode.cn/problems/majority-element/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

数组里必有一个元素出现次数 $\gt \lfloor n/2 \rfloor$。找出它。

## 思路

Boyer-Moore：维护 `cand` 和 `cnt`。遇到相同票加一，不同减一；`cnt` 到 $0$ 就换候选人。多数元素的票数严格过半，对消后一定剩下它。

哈希计数 $O(n)$ 空间；排序后中位数就是答案，时间 $O(n\log n)$。白板一般先写投票，再补这两种。

## 参考代码

```python
from typing import List


def majorityElement(nums: List[int]) -> int:
    cand = 0
    cnt = 0
    for x in nums:
        if cnt == 0:
            cand = x
        cnt += 1 if x == cand else -1
    return cand


if __name__ == "__main__":
    assert majorityElement([3, 2, 3]) == 3
    assert majorityElement([2, 2, 1, 1, 1, 2, 2]) == 2
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。排序做法 $O(n\log n)$ 时间；$O(n)$ 哈希空间。

## 边界

- $n=1$：唯一元素就是多数。
- 多数在开头或结尾：投票照样能对消到它。
- 其余元素种类很多：只要每种都 $\le \lfloor n/2 \rfloor$，对消后仍留下多数。

## 追问

- **不保证存在多数元素？** Boyer-Moore 只保证「若存在则留下它」，不存在时 `cand` 可能是任意幸存者。扫完后必须再扫一遍数 `cand` 的出现次数，确认 $\gt \lfloor n/2 \rfloor$，否则返回「不存在」。时间仍 $O(n)$，额外空间 $O(1)$。本题题面保证存在，第二遍可以省。这块容易栽：把投票结果直接当答案。

```python
def majorityElement_check(nums):
    cand = cnt = 0
    for x in nums:
        if cnt == 0:
            cand = x
        cnt += 1 if x == cand else -1
    return cand if nums.count(cand) > len(nums) // 2 else None
```

- **找出现次数 $\gt n/3$ 的元素（LC 229）？** 最多两个。摩尔投票扩成两个候选人 `cand1`、`cand2` 和两个计数：相同则加，都不同则一起减，计数到 $0$ 再换人。结束后必须再扫一遍验证，因为「$\gt n/3$」不像过半那样能保证幸存者一定合法。时间 $O(n)$，额外空间 $O(1)$。这块容易栽：两个候选人要先判断是否等于再判断计数是否为 $0$，否则同一个值会占两个槽；以及不要忘了验证。不在 150 手册里。

```python
def majorityElement_n3(nums):
    c1 = c2 = None
    n1 = n2 = 0
    for x in nums:
        if x == c1:
            n1 += 1
        elif x == c2:
            n2 += 1
        elif n1 == 0:
            c1, n1 = x, 1
        elif n2 == 0:
            c2, n2 = x, 1
        else:
            n1 -= 1
            n2 -= 1
    ans = []
    for c in (c1, c2):
        if c is not None and nums.count(c) > len(nums) // 3:
            ans.append(c)
    return ans
```

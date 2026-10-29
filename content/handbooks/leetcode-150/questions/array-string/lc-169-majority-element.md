---
id: lc-169-majority-element
section: array-string
order: 5
level: S
title: LC 169 · 多数元素
quick: >-
  用 Boyer-Moore 投票：维护一个候选元素和计数，遇到相同元素加一、不同减一，归零就换候选。多数元素严格过半，两两抵消后一定剩下它。时间
  $O(n)$，额外空间 $O(1)$；也可以排序或哈希计数。
tags:
  - Array
  - Boyer-Moore
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 169. 多数元素
    url: 'https://leetcode.cn/problems/majority-element/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定非空整数数组 `nums`。其中存在一个元素，它出现的次数严格大于数组长度的一半，这个元素称为多数元素。请返回该元素的值。

### 接口与输出

实现 `majorityElement(nums: List[int]) -> int`。返回值是数组元素本身，不是出现次数或位置。

### 合法输入与约束

`1 <= len(nums) <= 50000`，`-10^9 <= nums[i] <= 10^9`。输入保证存在多数元素；“严格多于一半”不是“大于等于一半”。

### 示例

```text
输入：nums = [3,2,3]
输出：3
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/majority-element/description/)。

## 解题思路与参考答案

## 题意

数组里必有一个元素出现次数 $\gt \lfloor n/2 \rfloor$。找出它。

## 思路

我会用 Boyer-Moore 投票，一遍扫完，只用两个变量。维护 `cand` 和 `cnt`，遇到相同的票加一，不同的减一，`cnt` 到 $0$ 就换候选人。多数元素的票数严格过半，和其他元素两两对消之后一定还剩下它。

拿 `[2, 2, 1, 1, 1, 2, 2]` 走一遍：前两个 $2$ 把计数加到 $2$，接下来两个 $1$ 把它抵到 $0$；第五个数 $1$ 当上候选，又被下一个 $2$ 抵掉；最后一个 $2$ 成为候选，答案是 $2$。

哈希计数要 $O(n)$ 空间；排序后中位数就是答案，时间 $O(n\log n)$。白板上我一般先写投票，再补这两种。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert majorityElement([3, 2, 3]) == 3
assert majorityElement([2, 2, 1, 1, 1, 2, 2]) == 2
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

投票做法时间 $O(n)$，额外空间 $O(1)$。排序做法时间 $O(n\log n)$，哈希计数要 $O(n)$ 空间。

## Edge Cases

$n=1$ 时唯一元素就是多数。多数在开头或结尾，投票照样能对消到它。其他元素种类很多也没关系，只要每种都 $\le \lfloor n/2 \rfloor$，对消后仍会留下多数。

## 追问

**不保证存在多数元素呢？**
扫完要再扫一遍验证。Boyer-Moore 只保证「如果存在就留下它」，不存在时 `cand` 可能是任意一个幸存者，所以第二遍数一下 `cand` 的出现次数，确认 $\gt \lfloor n/2 \rfloor$，否则返回不存在。时间仍是 $O(n)$，额外空间 $O(1)$。本题题面保证存在，第二遍可以省，换成不保证的题就别把投票结果直接当答案。

```python
def majorityElement_check(nums):
    cand = cnt = 0
    for x in nums:
        if cnt == 0:
            cand = x
        cnt += 1 if x == cand else -1
    return cand if nums.count(cand) > len(nums) // 2 else None
```

**找出现次数 $\gt n/3$ 的元素呢（LC 229）？**
这样的元素最多两个，所以把投票扩成两个候选人 `cand1`、`cand2` 和两个计数：和某个候选相同就给它加，都不同就一起减，计数到 $0$ 再换人。结束后一定要再扫一遍验证，因为「$\gt n/3$」不像过半那样能保证幸存者一定合法。时间 $O(n)$，额外空间 $O(1)$。写的时候要先判断是否等于候选，再判断计数是否为 $0$，否则同一个值会占两个槽；最后的验证也别忘。这题不在 150 手册里。

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

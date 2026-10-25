---
id: lc-1207-unique-number-of-occurrences
section: hashmap
order: 2
level: A
title: LC 1207 · 独一无二的出现次数
quick: "先用哈希数出每个值的出现次数，再把这些次数放进集合；集合大小等于不同值的个数，就说明次数两两不同。时间 $O(n)$，额外空间 $O(n)$。"
tags:
  - Array
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1207. Unique Number of Occurrences
    url: https://leetcode.com/problems/unique-number-of-occurrences/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定整数数组 arr，分别统计每一种不同整数在数组中出现的次数。如果任意两种不同整数的出现次数都不同，则返回 True；只要有两种整数的频次相同，就返回 False。

### 接口与输出

实现 `uniqueOccurrences(arr: List[int]) -> bool`。比较的是不同值的出现次数是否唯一，不是判断数组元素本身是否各不相同。

### 合法输入与约束

`1 <= len(arr) <= 1000`，`-1000 <= arr[i] <= 1000`。只有一种不同整数时，它的频次自然满足唯一性。

### 示例

```text
输入：arr = [1,2,2,1,1,3]
输出：true
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/unique-number-of-occurrences/description/)。

## 解题思路与参考答案

## 题意

给整数数组 `arr`，如果每个不同的值出现的次数都互不相同，返回 `true`，否则 `false`。$1 \le n \le 1000$，值在 $[-1000, 1000]$。

## 思路

我用两层哈希。第一层 `Counter` 得到「值 $\to$ 次数」；第二层看这些次数有没有重复，把 `counts.values()` 放进 `set`，长度没变就说明没有两个值共用同一个次数。

拿 `[1,2,2,1,1,3]` 看：`1` 出现 3 次，`2` 出现 2 次，`3` 出现 1 次，次数集合是 $\{3,2,1\}$，大小 3，和不同值的个数一样，返回 `true`。换成 `[1,2]`，两个值都只出现 1 次，集合缩成 $\{1\}$，返回 `false`。

也可以把次数排序后看相邻是否相等，多一个 $\log$。

## 参考代码

```python
from collections import Counter
from typing import List


def uniqueOccurrences(arr: List[int]) -> bool:
    counts = Counter(arr)
    return len(set(counts.values())) == len(counts)


if __name__ == "__main__":
    assert uniqueOccurrences([1, 2, 2, 1, 1, 3]) is True
    assert uniqueOccurrences([1, 2]) is False
    assert uniqueOccurrences([-3, 0, 1, -3, 1, 1, 1, -3, 10, 0]) is True
    assert uniqueOccurrences([5]) is True
    assert uniqueOccurrences([7, 7, 8, 8]) is False
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

如果题目允许答案以任意顺序返回，先排序或转成集合再比较；只有题目保证没有重复结果时才适合直接用集合，否则还要检查重复次数。

```python
assert uniqueOccurrences([1, 2, 2, 1, 1, 3]) is True
assert uniqueOccurrences([1, 2]) is False
assert uniqueOccurrences([-3, 0, 1, -3, 1, 1, 1, -3, 10, 0]) is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。

## 边界

只有一个不同值时，一定是 `true`。

所有值各出现一次、而且不止一个值时，次数全是 $1$，返回 `false`。

负数当键没问题；如果换成数组计数，要做下标偏移。

## 追问

**最少删几个元素，能让出现次数两两不同（LC 1647 思路）？**
把次数从大到小排序，贪心往下压：每个次数不能超过上一个次数减一，也不能小于 $0$，压掉的差值就是要删的数量。排序后时间 $O(k \log k)$，$k$ 是不同值的个数。

```python
from collections import Counter

def minDeletions(arr):
    freqs = sorted(Counter(arr).values(), reverse=True)
    deleted, prev = 0, None
    for f in freqs:
        keep = f if prev is None else max(0, min(f, prev - 1))
        deleted += f - keep
        prev = keep
    return deleted
```

**不用 `Counter` 怎么写？**
值域只有 $2001$ 个，开数组 `cnt[x + 1000] += 1` 计数；次数最大是 $n$，再开一个长度 $n+1$ 的布尔数组查重，全程不碰哈希。

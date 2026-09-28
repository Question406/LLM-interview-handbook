---
id: lc-443-string-compression
section: array-string
order: 9
level: A
title: LC 443 · 压缩字符串
quick: >-
  读指针 `i` 找一段相同字符，写指针 `w` 先写字符，长度大于 $1$ 再逐位写数字。压缩后永远不比原段长，写指针不会追上读指针。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - String
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 443. String Compression
    url: https://leetcode.com/problems/string-compression/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给字符数组 `chars`，按连续相同字符分组：组长为 $1$ 只写字符，否则写字符加组长（组长 $\ge 10$ 时拆成多个数字字符）。结果原地写回 `chars` 开头，返回新长度。只能用常数额外空间。长度在 $[1, 2000]$。

## 思路

读指针 `i` 定位一组的起点，`j` 往右走到第一个不同字符，组长 $j - i$。写指针 `w` 先写 `chars[i]`，组长大于 $1$ 时把 `str(j - i)` 的每一位依次写入。然后 `i = j` 处理下一组。

原地安全：一组长 $L$ 压缩后占 $1$ 位（$L=1$）或 $1 + \text{digits}(L)$ 位，都不超过 $L$。所以写完这组时 `w <= j`，不会覆盖还没读的字符。

## 参考代码

```python
from typing import List


def compress(chars: List[str]) -> int:
    n = len(chars)
    w = i = 0
    while i < n:
        j = i
        while j < n and chars[j] == chars[i]:
            j += 1
        chars[w] = chars[i]
        w += 1
        if j - i > 1:
            for d in str(j - i):
                chars[w] = d
                w += 1
        i = j
    return w


if __name__ == "__main__":
    c = ["a", "a", "b", "b", "c", "c", "c"]
    assert compress(c) == 6 and c[:6] == ["a", "2", "b", "2", "c", "3"]
    c = ["a"]
    assert compress(c) == 1 and c[:1] == ["a"]
    c = ["a"] + ["b"] * 12
    assert compress(c) == 4 and c[:4] == ["a", "b", "1", "2"]
    c = ["a", "b", "c"]
    assert compress(c) == 3 and c[:3] == ["a", "b", "c"]
    c = ["z"] * 100
    assert compress(c) == 4 and c[:4] == ["z", "1", "0", "0"]
    print("ok")
```

## 复杂度

时间 $O(n)$，每个字符被读一次、最多写一次。额外空间 $O(1)$；`str(j - i)` 最多 $4$ 位，算常数。

## 边界

- 组长 $\ge 10$：要逐位写，`12` 写成 `"1"`、`"2"` 两个元素。
- 组长为 $1$：只写字符，不写 `"1"`。
- 全部不同：结果和原数组一样，返回 $n$。
- 同一字符分成不相邻的两段，如 `aabaa`：各算各的，写成 `a2ba2`。

## 追问

- **不想用 `str()` 转数字？** 先把组长的每一位按低位到高位写进去，再把这几位原地反转。和 `str` 版本一样是常数额外空间，只是展示了手写数位拆分。

```python
def writeCount(chars, w, cnt):
    start = w
    while cnt:
        chars[w] = chr(ord("0") + cnt % 10)
        cnt //= 10
        w += 1
    l, r = start, w - 1
    while l < r:
        chars[l], chars[r] = chars[r], chars[l]
        l += 1
        r -= 1
    return w
```

- **压缩后不更短就返回原串（CtCI 1.6 的变体）？** 先按同样规则算出压缩长度，不小于原长就直接返回原串，否则再真正写出。这里写的是新字符串，不涉及原地覆盖。

---
id: lc-443-string-compression
section: array-string
order: 9
level: A
title: LC 443 · 压缩字符串
quick: >-
  用读写双指针原地压缩：读指针 `i` 找出一段相同字符，写指针 `w` 先写字符，段长大于 $1$
  再逐位写数字。压缩结果永远不比原段长，写指针追不上读指针。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - String
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 443. String Compression
    url: 'https://leetcode.com/problems/string-compression/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定字符数组，把每一段连续相同字符压缩。段长为 1 时只写该字符；段长大于 1 时先写字符，再写段长的十进制数字，每个数字分别作为一个字符。必须把结果原地写回输入数组开头，不能把所有字符重新返回为另一个数组。

### 输入与输出

实现 `compress(chars) -> int`，返回压缩后有效前缀的长度。调用后的 `chars[:返回长度]` 就是压缩结果，后面剩余内容不作要求；字符原本也可能是数字或符号。

### 约束与约定

- `1 <= len(chars) <= 2000`。
- 每个元素为一个英文字母、数字或符号字符。
- 要求常数额外空间；段长达到 10 以上时需要写入多位数字字符。

### 示例

```text
输入：chars = ["a","a","b","b","c","c","c"]
输出：6
```

示例返回 6，同时 chars 的前六项必须为 ["a","2","b","2","c","3"]。

[官方原题与完整题面](https://leetcode.com/problems/string-compression/description/)。

## 解题思路与参考答案

## 题意

给字符数组 `chars`，按连续相同字符分组：组长为 $1$ 只写字符，否则写字符加组长（组长 $\ge 10$ 时拆成多个数字字符）。结果原地写回 `chars` 开头，返回新长度。只能用常数额外空间。长度在 $[1, 2000]$。

## 思路

我会用读写两个指针原地改写，因为压缩后每一段都不会变长，写的位置永远落在已经读过的地方。读指针 `i` 定位一组的起点，`j` 往右走到第一个不同字符，组长就是 $j - i$。写指针 `w` 先写 `chars[i]`，组长大于 $1$ 时把 `str(j - i)` 的每一位依次写进去。然后 `i = j`，处理下一组。

拿 `["a","a","b","b","c","c","c"]` 走一遍：第一组 `a` 长 2，写成 `a`、`2`；第二组 `b` 长 2，写成 `b`、`2`；第三组 `c` 长 3，写成 `c`、`3`，返回 6。

原地写为什么安全？一组长 $L$ 压缩后占 $1$ 位（$L=1$）或 $1 + \text{digits}(L)$ 位，都不超过 $L$。所以写完这组时 `w <= j`，不会覆盖还没读的字符。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
c = ["a", "a", "b", "b", "c", "c", "c"]
assert compress(c) == 6 and c[:6] == ["a", "2", "b", "2", "c", "3"]
c = ["a"]
assert compress(c) == 1 and c[:1] == ["a"]
c = ["a"] + ["b"] * 12
assert compress(c) == 4 and c[:4] == ["a", "b", "1", "2"]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，每个字符被读一次、最多写一次。额外空间 $O(1)$；`str(j - i)` 最多 $4$ 位，算常数。

## Edge Cases

- 组长 $\ge 10$ 时要逐位写，`12` 写成 `"1"`、`"2"` 两个元素。
- 组长为 $1$ 只写字符，不写 `"1"`。
- 全部字符都不同时，结果和原数组一样，返回 $n$。
- 同一字符分成不相邻的两段，比如 `aabaa`，各算各的，写成 `a2ba2`。

## 追问

**不想用 `str()` 转数字怎么办？**
先把组长的每一位按低位到高位写进去，再把这几位原地反转。和 `str` 版本一样是常数额外空间，只是展示了手写数位拆分。

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

**压缩后不更短就返回原串（CtCI 1.6 的变体）呢？**
先按同样规则算出压缩长度，不小于原长就直接返回原串，否则再真正写出来。这里写的是新字符串，不涉及原地覆盖。

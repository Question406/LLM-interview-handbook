---
id: lc-191-number-of-1-bits
section: bit
order: 3
level: S
title: LC 191 · 位1的个数
quick: 反复做 `n & (n - 1)`，每次清掉最低的那个 $1$，直到 $n=0$，循环次数就是汉明重量。时间与 $1$ 的个数成正比。
tags:
  - Bit
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 191. 位1的个数
    url: 'https://leetcode.cn/problems/number-of-1-bits/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一个正整数 n，返回它的二进制表示中数字 1 出现的次数，也称该整数的汉明重量。二进制表示左侧补多少个零都不影响结果。

### 输入与输出

实现 `hammingWeight(n: int) -> int`，输入是整数，返回 1 位的数量，不是二进制字符串的长度。

### 约束

- 官方当前输入范围为 `1 <= n <= 2^31-1`。

### 示例

```text
输入：n = 11
输出：3
```

11 的二进制表示是 `1011`，其中共有 3 个 1。

## 解题思路与参考答案

## 题意

返回一个无符号整数二进制表示里 $1$ 的个数，也叫汉明重量。

## 思路

我会用 `n & (n - 1)`，因为它每次正好清掉一个 $1$，循环次数就是答案。原理是 `n - 1` 会把最低的 $1$ 变成 $0$，并把它右边的 $0$ 都变成 $1$；和原数做 AND 后，右边这些位仍是 $0$，只有原来最低的那个 $1$ 被清掉了。

拿 $11$ 走一遍：`1011 & 1010 = 1010`，`1010 & 1001 = 1000`，`1000 & 0111 = 0000`，清了三次，答案是 $3$。

逐位右移也行，固定 $32$ 次，但更常被追问的是 `n & (n - 1)` 这条。Python 的 `n.bit_count()` 能过，手写也要会。

## 参考代码

```python
def hammingWeight(n: int) -> int:
    cnt = 0
    while n:
        n &= n - 1
        cnt += 1
    return cnt


if __name__ == "__main__":
    assert hammingWeight(11) == 3
    assert hammingWeight(128) == 1
    assert hammingWeight(0) == 0
    assert hammingWeight((1 << 32) - 1) == 32
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert hammingWeight(11) == 3
assert hammingWeight(128) == 1
assert hammingWeight(0) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(k)$，$k$ 是 $1$ 的个数，最坏 $O(32)$。额外空间 $O(1)$。

## Edge Cases

$n=0$ 时循环不进，答案 $0$。只有最高位是 $1$ 时，`n & (n-1)` 一次就清掉，答案 $1$。全是 $1$（$2^{32}-1$）时要循环 $32$ 次。

## 追问

**汉明距离（LC 461）怎么算？**
两数先异或，不同的比特会变成 $1$，再数 $1$ 的个数。时间和不同的位数成正比。

```python
def hammingDistance(x, y):
    n, cnt = x ^ y, 0
    while n:
        n &= n - 1
        cnt += 1
    return cnt
```

**区间 $[0,n]$ 里一共有多少个 $1$？**
别对每个数都调一遍本题。第 $b$ 位以 $2^{b+1}$ 为周期，每个周期前一半是 $0$、后一半是 $1$。对 $n+1$ 先数完整周期，再加上余下的部分。也可以用数位 DP。

```python
def countBitsRange(n):
    n += 1
    ans, b = 0, 1
    while b < n:
        cycle = b << 1
        ans += (n // cycle) * b + max(0, n % cycle - b)
        b <<= 1
    return ans
```

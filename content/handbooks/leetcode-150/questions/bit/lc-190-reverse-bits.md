---
id: lc-190-reverse-bits
section: bit
order: 2
level: A
title: LC 190 · 颠倒二进制位
quick: >-
  固定做 $32$ 轮：每轮 `ans` 左移一位，接上 `n` 的最低位，再把 `n` 右移。不按有效位数提前停，高位的 $0$ 也要占位。时间
  $O(1)$。
tags:
  - Bit
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 190. 颠倒二进制位
    url: 'https://leetcode.cn/problems/reverse-bits/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定整数 `n`，把它表示为恰好 32 个二进制位，不足 32 位的高位补零。将这 32 位整体左右颠倒，再把颠倒后的位串当作非负整数返回。颠倒的是比特次序，不是十进制数字顺序。

### 输入与输出

实现 `reverseBits(n) -> int`。例如最低位会移动到第 31 位，最高位会移动到第 0 位；返回数值，不返回二进制字符串。

### 约束

- 本题按32位宽度处理，前导零也参与颠倒。
- 当前官方题面快照给出的输入范围为 `0 <= n <= 2^31 - 2`，并保证 n 为偶数。

### 示例

```text
输入：n = 43261596
输出：964176192
```

[LeetCode 原题](https://leetcode.com/problems/reverse-bits/description/)

## 解题思路与参考答案

## 题意

把一个 $32$ 位无符号整数的比特整体颠倒，返回颠倒后的值。高位不足要补零，低位的 $1$ 会翻到高位。

## 思路

我会一位一位地搬：从 `n` 的低位往外取，往 `ans` 里从高到低装填。每轮做 `ans = (ans << 1) | (n & 1)`，然后 `n >>= 1`，固定做 $32$ 轮。不要按「有效比特」提前停，否则高位的 $0$ 就丢了。

拿 $n=1$ 看：第一轮把最低位的 $1$ 搬进 `ans`，后面 $31$ 轮 `n` 都是 $0$，`ans` 只是不断左移，最后得到 $2^{31}$。如果 `n` 一变成 $0$ 就停，结果会停在 $1$。

还有一种分治交换的写法，按 16、8、4、2、1 位成对交换，同样 $O(1)$，常数更小，提一句即可。

## 参考代码

```python
def reverseBits(n: int) -> int:
    ans = 0
    for _ in range(32):
        ans = (ans << 1) | (n & 1)
        n >>= 1
    return ans


if __name__ == "__main__":
    assert reverseBits(0) == 0
    assert reverseBits(1) == 1 << 31
    assert reverseBits(43261596) == 964176192
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert reverseBits(0) == 0
assert reverseBits(1) == 1 << 31
assert reverseBits(43261596) == 964176192
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

固定 $32$ 次循环，时间 $O(1)$，额外空间 $O(1)$。

## Edge Cases

$n=0$ 固定做完 $32$ 轮后仍是 $0$。最高位已经是 $1$ 时，它会翻到最低位；不要按有符号数提前停，高位的 $0$ 也要占位。

## 追问

**比特宽度不固定呢？**
先约定宽度 $w$（或者用 `n.bit_length()`），循环 $w$ 次，不再写死 $32$。宽度不足时左边补零，其余逻辑和本题相同。

```python
def reverseBitsVar(n, width=None):
    if width is None:
        width = max(n.bit_length(), 1)
    ans = 0
    for _ in range(width):
        ans = (ans << 1) | (n & 1)
        n >>= 1
    return ans
```

**要按字节翻转、反复调用很多次呢？**
把 $32$ 位拆成 $4$ 个字节，字节顺序反过来，每个字节内部用一张 $256$ 项的表翻转。这样 $32$ 次位移就收成了 $4$ 次查表，适合反复调用。

```python
TABLE = [int(f"{i:08b}"[::-1], 2) for i in range(256)]


def reverseBitsBytes(n):
    b0 = TABLE[n & 255]
    b1 = TABLE[(n >> 8) & 255]
    b2 = TABLE[(n >> 16) & 255]
    b3 = TABLE[(n >> 24) & 255]
    return (b0 << 24) | (b1 << 16) | (b2 << 8) | b3
```

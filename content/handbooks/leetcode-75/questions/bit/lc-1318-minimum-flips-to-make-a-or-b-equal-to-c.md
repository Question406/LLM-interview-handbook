---
id: lc-1318-minimum-flips-to-make-a-or-b-equal-to-c
section: bit
order: 3
level: A
title: LC 1318 · 或运算的最小翻转次数
quick: >-
  按位或没有进位，各位独立算再相加。$c$ 某位为 $1$ 时，$a,b$ 该位都是 $0$ 才翻 $1$ 次；$c$ 某位为 $0$ 时，$a,b$
  该位有几个 $1$ 就翻几次。一行写法是 $\mathrm{popcount}((a|b)\oplus
  c)+\mathrm{popcount}(a\,\&\,b\,\&\,\lnot c)$，时间 $O(\log C)$，额外空间 $O(1)$。
tags:
  - Bit
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 1318. Minimum Flips to Make a OR b Equal to c
    url: 'https://leetcode.com/problems/minimum-flips-to-make-a-or-b-equal-to-c/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定三个正整数 a、b、c，你可以在 a 或 b 的二进制表示中任选一位，将该位从 0 改为 1，或从 1 改为 0。每改变一个数的一位计一次操作，c 不允许改动。求使 a 按位或 b 的结果等于 c 所需的最少操作次数。

### 输入与输出

实现 `minFlips(a, b, c) -> int`，返回最小翻转次数。按位或记为 `a | b`，不是把二进制表示连接起来；高位不足时按前导零理解。

### 约束与约定

- `1 <= a,b,c <= 1000000000`。
- 一次操作只能改变 a 或 b 中的一个二进制位。

### 示例

```text
输入：a = 2, b = 6, c = 5
输出：3
```

示例需要三次位翻转才能让两个数的按位或等于 5。

[官方原题与完整题面](https://leetcode.com/problems/minimum-flips-to-make-a-or-b-equal-to-c/description/)。

## 解题思路与参考答案

## 题意

三个正整数 $a$、$b$、$c$（都不超过 $10^9$）。一次翻转是把 $a$ 或 $b$ 二进制里的某一位 $0\leftrightarrow 1$。求最少翻转几次，使 $a\,|\,b=c$。

## 思路

我会逐位算再相加，因为按位或没有进位，每一位互不影响，每位取最少翻转加起来就是全局最优。看第 $i$ 位，记 $x, y, z$ 为 $a, b, c$ 在这一位的值。$z=1$ 时，$x, y$ 有一个是 $1$ 就满足，两个都是 $0$ 就翻任意一个，代价 $1$。$z=0$ 时，$x, y$ 都必须是 $0$，代价是 $x+y$。一直扫到 $a, b, c$ 都变成 $0$，最多 $30$ 位。

拿 $a=2, b=6, c=5$ 走一遍，二进制分别是 `010`、`110`、`101`。最低位 $z=1$，$x, y$ 都是 $0$，翻 1 次；中间位 $z=0$，$x, y$ 都是 $1$，翻 2 次；最高位 $z=1$，$y$ 已经是 $1$，不用翻。总共 3 次。

也可以用位运算合并成一行。$(a|b)\oplus c$ 标出所有不符合的位，每位至少翻一次；其中 $c$ 为 $0$ 且 $a, b$ 都是 $1$ 的位要翻两次，用 $a\,\&\,b\,\&\,\lnot c$ 再补上。

## 参考代码

```python
def minFlips(a: int, b: int, c: int) -> int:
    flips = 0
    while a or b or c:
        x, y, z = a & 1, b & 1, c & 1
        if z:
            flips += 1 if x == 0 and y == 0 else 0
        else:
            flips += x + y
        a >>= 1
        b >>= 1
        c >>= 1
    return flips


if __name__ == "__main__":
    assert minFlips(2, 6, 5) == 3
    assert minFlips(4, 2, 7) == 1
    assert minFlips(1, 2, 3) == 0
    assert minFlips(1, 1, 1) == 0
    assert minFlips(7, 7, 0) == 6
    assert minFlips(8, 3, 5) == 3
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert minFlips(2, 6, 5) == 3
assert minFlips(4, 2, 7) == 1
assert minFlips(1, 2, 3) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log C)$，$C=\max(a,b,c)$，最多约 $30$ 轮。额外空间 $O(1)$。

## Edge Cases

- 已经满足 $a\,|\,b=c$ 时，每位代价都是 $0$。
- $c$ 的某位是 $0$ 而 $a, b$ 该位都是 $1$，要翻两次，只算 $1$ 是常见错误。
- 三个数位数不同时，循环条件用 `a or b or c`，保证较长那个数的高位也被检查。

## 追问

**不写循环，一行位运算怎么写？**
前一项数出所有不符合的位，后一项给要翻两次的位补一次。Python 里 `~c` 是负数，但和非负的 `a & b` 相与后结果非负，`bin().count` 没问题。

```python
def minFlipsOneLine(a, b, c):
    return bin((a | b) ^ c).count("1") + bin(a & b & ~c).count("1")
```

**改成 $a\,\&\,b=c$ 呢？**
同样逐位算。$z=1$ 时 $x, y$ 都要是 $1$，代价 $(1-x)+(1-y)$；$z=0$ 时只要有一个 $0$，两者都是 $1$ 才翻 $1$ 次。

---
id: lc-374-guess-number-higher-or-lower
section: binary-search
order: 1
level: A
title: LC 374 · 猜数字大小
quick: >-
  在 $[1, n]$ 上标准二分：`guess(mid)` 返回 $-1$ 说明猜大了，收右端；返回 $1$ 说明猜小了，收左端；返回 $0$
  就是答案。时间 $O(\log n)$，额外空间 $O(1)$。
tags:
  - Binary Search
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 374. Guess Number Higher or Lower
    url: 'https://leetcode.com/problems/guess-number-higher-or-lower/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

系统在 1 到 n 之间预先选定了一个整数 pick，你不能直接读取它，只能调用给定接口 guess(num) 进行比较：若 num 大于 pick 返回 -1，若 num 小于 pick 返回 1，相等返回 0。请找出系统选定的数。

### 输入与输出

实现 `guessNumber(n: int) -> int`，返回 pick。`guess` 由测试环境提供；示例里的 pick 用于说明和准备测试，不是 guessNumber 的额外参数。注意返回 -1 的含义是“你猜大了”。

### 约束

- `1 <= n <= 2^31-1`。
- `1 <= pick <= n`，一次查找过程中 pick 保持不变。

### 示例

```text
输入：n = 10, pick = 6
输出：6
```

## 解题思路与参考答案

## 题意

系统从 $1$ 到 $n$ 里选了一个数 `pick`。调用预定义接口 `guess(num)`：`num` 大于 `pick` 返回 $-1$，小于返回 $1$，相等返回 $0$。找出 `pick`。$n$ 最大到 $2^{31}-1$。

## 思路

这题就是标准二分，每猜一次扔掉一半。区间 $[lo, hi]$ 始终包含答案。每次猜 `mid`，返回 $-1$ 表示 `mid` 太大，令 `hi = mid - 1`；返回 $1$ 表示太小，令 `lo = mid + 1`。

最容易错的是返回值的方向。$-1$ 描述的是「你猜的数比答案大」，所以要往左收。我会先把这层含义跟面试官说清楚，再写分支。

拿 $n=10$、答案 6 走一遍：猜 5，返回 $1$，`lo=6`；猜 8，返回 $-1$，`hi=7`；猜 6，返回 $0$，结束。

从 $1$ 往上逐个猜是 $O(n)$，$n$ 到 $2^{31}$ 时不可接受。Python 整数不溢出，`(lo + hi) // 2` 直接写；Java/C++ 要写成 `lo + (hi - lo) / 2`。

## 参考代码

```python
PICK = 6


def guess(num: int) -> int:
    if num > PICK:
        return -1
    if num < PICK:
        return 1
    return 0


def guessNumber(n: int) -> int:
    lo, hi = 1, n
    while lo <= hi:
        mid = (lo + hi) // 2
        res = guess(mid)
        if res == 0:
            return mid
        if res < 0:
            hi = mid - 1
        else:
            lo = mid + 1
    return -1


if __name__ == "__main__":
    PICK = 6
    assert guessNumber(10) == 6
    PICK = 1
    assert guessNumber(1) == 1
    PICK = 1
    assert guessNumber(2) == 1
    PICK = 2
    assert guessNumber(2) == 2
    PICK = 2**31 - 1
    assert guessNumber(2**31 - 1) == 2**31 - 1
    for n in range(1, 60):
        for p in range(1, n + 1):
            PICK = p
            assert guessNumber(n) == p
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
PICK = 6
assert guessNumber(10) == 6
PICK = 1
assert guessNumber(1) == 1
PICK = 1
assert guessNumber(2) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log n)$，最多约 $31$ 次调用。额外空间 $O(1)$。

## Edge Cases

- $n=1$ 时一次猜中。
- 答案在两端（$1$ 或 $n$）时，闭区间写法能收敛到端点。
- $n = 2^{31}-1$ 且答案也是它时，别的语言里 `lo + hi` 会溢出，要用 `lo + (hi - lo) / 2`。

## 追问

**猜错要付钱，最坏情况下至少准备多少钱（LC 375）？**
这就要用区间 DP，二分解决不了。`dp[i][j]` 是在 $[i, j]$ 里保证猜中的最小花费，枚举第一次猜 $x$，花费是 $x+\max(dp[i][x-1], dp[x+1][j])$，取最小。时间 $O(n^3)$。

```python
def getMoneyAmount(n):
    dp = [[0] * (n + 2) for _ in range(n + 2)]
    for length in range(2, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            dp[i][j] = min(x + max(dp[i][x - 1], dp[x + 1][j]) for x in range(i, j + 1))
    return dp[1][n]
```

**和「二分答案」题是什么关系？**
框架相同，区别在判定函数要不要自己写。本题的判定函数就是 `guess`，直接给出方向；`lc-875-koko-eating-bananas` 要自己写判定「速度 $k$ 能否在 $h$ 小时内吃完」，再对 $k$ 二分。

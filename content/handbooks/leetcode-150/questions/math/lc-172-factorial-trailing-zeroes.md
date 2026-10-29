---
id: lc-172-factorial-trailing-zeroes
section: math
order: 3
level: A
title: LC 172 · 阶乘后的零
quick: >-
  尾零来自因子 $10=2\times 5$，而 $2$ 永远比 $5$ 多，所以数因子 $5$ 的个数就够了，也就是 $n/5 + n/25 +
  n/125+\cdots$。别真去算 $n!$。
tags:
  - Math
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 172. 阶乘后的零
    url: 'https://leetcode.cn/problems/factorial-trailing-zeroes/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定非负整数 n，求 n 的阶乘 n! 在十进制表示末尾连续出现多少个零。只统计最右端相连的零，中间位置的零不计入；约定 0!=1。

### 输入与输出

实现 `trailingZeroes(n: int) -> int`，返回末尾零的个数，不要求输出阶乘本身。

### 约束

- `0 <= n <= 10^4`。
- 进阶要求以对数级时间完成。

### 示例

```text
输入：n = 3
输出：0
```

3!=6，末尾没有零，因此返回 0；5!=120 的末尾有一个零。

## 解题思路与参考答案

## 题意

给定 $n$，返回 $n!$ 的十进制表示末尾有多少个 $0$。

## 思路

我直接数因子 $5$。尾零个数等于因子 $10$ 的个数，$10=2\times 5$，而 $[1,n]$ 里因子 $2$ 远多于 $5$，所以答案就是 $5$ 的指数和 $\lfloor n/5\rfloor + \lfloor n/25\rfloor + \lfloor n/125\rfloor+\cdots$。

拿 $n=25$ 算一下，$\lfloor 25/5\rfloor+\lfloor 25/25\rfloor=5+1=6$。$25=5^2$ 本身多贡献一个 $5$，所以要多计一次，$125$ 也是同样的道理。

写起来就是循环 `n //= 5` 并累加。别先算阶乘再数零，既会溢出也慢。

## 参考代码

```python
def trailingZeroes(n: int) -> int:
    ans = 0
    while n:
        n //= 5
        ans += n
    return ans


if __name__ == "__main__":
    assert trailingZeroes(3) == 0
    assert trailingZeroes(5) == 1
    assert trailingZeroes(0) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert trailingZeroes(3) == 0
assert trailingZeroes(5) == 1
assert trailingZeroes(0) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log_5 n)$，额外空间 $O(1)$。

## Edge Cases

$n=0$ 或 $n\lt 5$ 时没有因子 $5$，答案是 $0$。

## 追问

**为什么不数 $2$？**
因为 $5$ 才是短板。$[1,n]$ 里偶数远多于 $5$ 的倍数，每个尾零 $10=2\times 5$ 配对后，限制个数的是 $5$。数 $2$ 会得到更大的指数，那不是十进制尾零的个数。下面的代码只是对照演示 $2$ 更多，`trailingZeroes` 数的是 $5$。

```python
def count_factor(n, p):
    ans = 0
    while n:
        n //= p
        ans += n
    return ans


# count_factor(n, 2) > count_factor(n, 5) 对 n >= 5 成立
```

**二进制下的尾零呢？**
$n!$ 二进制末尾 $0$ 的个数就是因子 $2$ 的个数，$\lfloor n/2\rfloor+\lfloor n/4\rfloor+\cdots$。它也等于 $n$ 减去其二进制中 $1$ 的个数（每个 $1$ 对应一个奇数因子）。

```python
def trailingZeroesBase2(n):
    ans = 0
    m = n
    while m:
        m //= 2
        ans += m
    return ans  # 等价于 n - n.bit_count()
```

---
id: lc-172-factorial-trailing-zeroes
section: math
order: 3
level: A
title: LC 172 · 阶乘后的零
quick: >-
  尾零来自因子 $10=2\times 5$，$2$ 永远比 $5$ 多，数 $5$ 的个数即可。$n/5 + n/25 +
  n/125+\cdots$。别真去算 $n!$。
tags:
  - Math
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 172. 阶乘后的零
    url: https://leetcode.cn/problems/factorial-trailing-zeroes/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给定 $n$，返回 $n!$ 十进制表示里末尾有多少个 $0$。

## 思路

尾零等于因子 $10$ 的个数，$10=2\times 5$。$[1,n]$ 里因子 $2$ 远多于 $5$，答案就是 $5$ 的指数和：$\lfloor n/5\rfloor + \lfloor n/25\rfloor + \lfloor n/125\rfloor+\cdots$。

循环 `n //= 5`，累加即可。别先算阶乘再数零：溢出且慢。$25$、$125$ 要多计，因为各自多带一个 $5$。

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

## 复杂度

时间 $O(\log_5 n)$，额外空间 $O(1)$。

## 边界

- $n=0$ 或 $n\lt 5$：没有因子 $5$，答案 $0$。
- $n=25$：$\lfloor 25/5\rfloor+\lfloor 25/25\rfloor=5+1=6$，因为 $25=5^2$ 多贡献一个 $5$。

## 追问

- **为什么不用数 $2$？** $[1,n]$ 里偶数远多于 $5$ 的倍数，每个尾零 $10=2\times 5$ 配对后 $5$ 是短板。数 $2$ 会得到更大的指数，不是十进制尾零个数。对照：`trailingZeroes` 数 $5$，下面数 $2$ 只是演示「$2$ 更多」。

```python
def count_factor(n, p):
    ans = 0
    while n:
        n //= p
        ans += n
    return ans
# count_factor(n, 2) > count_factor(n, 5) 对 n >= 5 成立
```

- **二进制尾零？** $n!$ 二进制末尾 $0$ 的个数等于因子 $2$ 的个数：$\lfloor n/2\rfloor+\lfloor n/4\rfloor+\cdots$。也等于 $n$ 减去其二进制中 $1$ 的个数（每个 $1$ 对应一个奇数因子）。

```python
def trailingZeroesBase2(n):
    ans = 0
    m = n
    while m:
        m //= 2
        ans += m
    return ans  # 等价于 n - n.bit_count()
```

---
id: lc-69-sqrtx
section: math
order: 4
level: S
title: LC 69 · x 的平方根
quick: >-
  求 $\lfloor\sqrt{x}\rfloor$。在 $[1,x]$ 上二分：用 `mid <= x // mid` 判断
  `mid*mid <= x`，避免溢出。找到最大可行 `mid`。
tags:
  - Binary Search
  - Math
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 69. x 的平方根
    url: https://leetcode.cn/problems/sqrtx/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

非负整数 `x`，返回它的整数平方根，向下取整。不能用内置开方。

## 思路

答案在 $[0,x]$（$x\ge 2$ 时可缩到 $[1,x/2]$）。二分找最大的 `mid` 满足 `mid*mid <= x`。乘法在 32 位里会溢出，改写成 `mid <= x // mid`（`mid>0`）。

`mid` 可行则记下并往右找更大；否则往左。牛顿迭代也能做，面试主答二分。

## 参考代码

```python
def mySqrt(x: int) -> int:
    if x < 2:
        return x
    lo, hi = 1, x // 2
    ans = 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if mid <= x // mid:
            ans = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


if __name__ == "__main__":
    assert mySqrt(4) == 2
    assert mySqrt(8) == 2
    print("ok")
```

## 复杂度

时间 $O(\log x)$，额外空间 $O(1)$。

## 边界

- $x=0$ 或 $1$：答案就是 $x$，二分前单独返回。
- 完全平方：二分会精确命中 `mid == x // mid`。
- 非完全平方：找最大满足 `mid <= x // mid` 的 `mid`，如 $8\to 2$。

## 追问

- **溢出？** 32 位里 `mid * mid` 可能超过 `INT_MAX`。改写成 `mid <= x // mid`（`mid\gt 0`），整除向零，与「平方不超过 $x$」等价。别先转浮点再比较，精度会在大整数上翻车。

- **浮点牛顿？** 迭代 $r \leftarrow (r + x/r)/2$，从 $r=x$ 出发，直到 $r^2$ 足够接近 $x$。取整前要处理「算大了就减一」：浮点误差可能让 $\lfloor r\rfloor^2 \gt x$。整数牛顿同样可用 `r = (r + x//r)//2`，且无精度问题。

```python
def mySqrtNewton(x):
    if x < 2:
        return x
    r = x
    while r > x // r:
        r = (r + x // r) // 2
    return r
```

---
id: lc-69-sqrtx
section: math
order: 4
level: S
title: LC 69 · x 的平方根
quick: "求 $\\lfloor\\sqrt{x}\\rfloor$，在 $[1,x]$ 上二分，找最大的可行 `mid`。判断 `mid*mid <= x` 时写成 `mid <= x // mid`，避免溢出。"
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

## 题目描述

给定非负整数 x，返回它的平方根向下取整后的整数。也就是求一个非负整数 r，使 `r*r <= x`，同时 `(r+1)*(r+1) > x`。不能把浮点近似值直接作为输出。

### 输入与输出

实现 `mySqrt(x) -> int`。不允许调用内置平方根或乘方接口来完成开方，例如 sqrt、pow 或 `x ** 0.5`；x=0 的结果为 0。

### 约束

- `0 <= x <= 2^31 - 1`。
- 输出是精确的整数下界，而不是四舍五入的结果。

### 示例

```text
输入：x = 4
输出：2
```

[LeetCode 原题](https://leetcode.com/problems/sqrtx/description/)

## 解题思路与参考答案

## 题意

给一个非负整数 `x`，返回它的整数平方根，向下取整，不能用内置的开方。

## 思路

我用二分，找最大的 `mid` 满足 `mid*mid <= x`。答案在 $[0,x]$ 里，$x\ge 2$ 时可以缩到 $[1,x/2]$。`mid` 可行就记下来，再往右找更大的；不可行就往左。乘法在 32 位里会溢出，所以改写成 `mid <= x // mid`（`mid>0`）。

拿 $x=8$ 走一遍。区间是 $[1,4]$，`mid=2`，`2 <= 8 // 2` 成立，记下 2 往右；区间变成 $[3,4]$，`mid=3`，`3 <= 8 // 3` 不成立，往左；区间变空，答案是 2。

牛顿迭代也能做，面试我主答二分。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert mySqrt(4) == 2
assert mySqrt(8) == 2
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log x)$，额外空间 $O(1)$。

## 边界

- $x=0$ 或 $1$ 时答案就是 $x$，在二分前单独返回。
- 完全平方数时，二分会精确命中 `mid == x // mid`。
- 非完全平方数时，找的是最大的满足 `mid <= x // mid` 的 `mid`，比如 $8\to 2$。

## 追问

**怎么防溢出？**
32 位里 `mid * mid` 可能超过 `INT_MAX`，改写成 `mid <= x // mid`（`mid\gt 0`）就行。整除向零取整，和「平方不超过 $x$」等价。别先转浮点再比较，大整数上精度会出错。

**用牛顿法呢？**
浮点版迭代 $r \leftarrow (r + x/r)/2$，从 $r=x$ 出发，直到 $r^2$ 足够接近 $x$。取整前要处理算大了的情况，浮点误差可能让 $\lfloor r\rfloor^2 \gt x$，这时要减一。整数牛顿同样可用，`r = (r + x//r)//2`，没有精度问题。

```python
def mySqrtNewton(x):
    if x < 2:
        return x
    r = x
    while r > x // r:
        r = (r + x // r) // 2
    return r
```

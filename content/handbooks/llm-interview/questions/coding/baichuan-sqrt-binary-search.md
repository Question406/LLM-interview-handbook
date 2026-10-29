---
id: baichuan-sqrt-binary-search
section: coding
order: 183
level: B
title: 百川智能：求根号下的数，二分怎么写、bounds 怎么收？
quick: >-
  在一个保证套住根的区间上二分，比较 $\mathrm{mid}^2$ 和 $x$：整数版在 $[1,x/2]$ 上找 floor，用 `mid <= x
  // mid` 比较防溢出，$x=0,1$ 直接返回；浮点版区间取 $[0,\max(1,x)]$，因为 $x<1$ 时根比 $x$
  大，按绝对或相对误差停。
tags:
  - Baichuan
  - Binary Search
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 百川智能大模型实习一面 压力好大
    url: 'https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530'
    type: candidate-first-hand
---

## 题目描述

在不调用现成平方根函数的前提下，分别实现非负整数的平方根下取整，以及非负实数的近似平方根。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

`my_sqrt_int(x: int)` 接收非负整数；`my_sqrt(x: float, eps=1e-9)` 接收非负有限实数和正误差容限。

### 输出与约束

整数接口返回唯一整数 r，使 r²≤x<(r+1)²。实数接口返回平方根的近似值，误差应在 eps 的量级；支持 0 和小于 1 的正数。无需处理负数。

### 示例

```text
my_sqrt_int(8) -> 2
my_sqrt_int(9) -> 3
my_sqrt(0.25) -> 约 0.5
my_sqrt(0.0) -> 0.0
```

## 解题思路与参考答案

我会在一个保证套住根的区间上二分，每次比较 $\mathrm{mid}^2$ 和 $x$，丢掉不含根的那一半，不变量是答案始终在 $[lo,hi]$ 里。整数版返回 floor，比较时用除法防溢出；浮点版要记得 $x\lt 1$ 时根比 $x$ 大，上界得取 1。牛顿法更快，但面试先把二分讲清楚。

最常见的坑有两个，一是直接算 `mid * mid` 溢出，二是 $0\lt x\lt 1$ 时还把上界设成 $x$，比如 $x=0.25$，根是 0.5，压根不在 $[0,0.25]$ 里。

## 整数版：求 floor($\sqrt{x}$)，用除法比大小

这是 LeetCode 69 的写法。$x\in\{0,1\}$ 直接返回，否则在 $[1,x]$（或者 $[1,x/2]$）上二分：`mid <= x // mid` 说明 `mid` 还能更大，记下答案往右走，否则往左走。别拿 `mid * mid` 和 $x$ 比，32 位、64 位都会溢出。

```python
def my_sqrt_int(x: int) -> int:
    if x < 2:
        return x
    lo, hi, ans = 1, x // 2, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if mid <= x // mid:
            ans = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return ans
```

循环条件是 `lo <= hi`，更新 `ans` 的那一侧保证它是「仍然 $\le\sqrt{x}$」的最大整数。写完我会用 $0,1,8,9$ 口头跑一遍：8 得 2，9 得 3。

## 浮点版：$x\lt 1$ 时上界改成 1

求实数 $\sqrt{x}$ 时，区间取 $[0,\max(1,x)]$，因为 $x\in[0,1)$ 时 $\sqrt{x}\gt x$。停止条件可以是 `hi - lo < eps`，也可以是相对误差 $|mid^2-x|/x$。面试范围内 float64 上直接比 `mid*mid` 够用；$x$ 特别大时也可以改成 `mid < x/mid`，这时要小心 `mid=0`。

```python
def my_sqrt(x: float, eps: float = 1e-9) -> float:
    if x < 0:
        raise ValueError("x < 0")
    lo, hi = 0.0, 1.0 if x < 1 else float(x)
    while hi - lo > eps:
        mid = (lo + hi) / 2
        if mid * mid < x:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
```

牛顿法的迭代是 $x_{n+1}=\frac12(x_n+x/x_n)$，迭代次数少，但要讲清初值怎么取、怎么避免除零。二分的好处是不变量清楚，很容易证明不会死循环。同一场可能还会考 Attention，见 `baichuan-mha-handwrite`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

整数版测完全平方数和平方数之间的取整；浮点版测小于 1 的数，用容差比较。负输入应按浮点接口约定抛异常。

```python
import math

assert my_sqrt_int(0) == 0
assert my_sqrt_int(9) == 3
assert my_sqrt_int(8) == 2
assert math.isclose(my_sqrt(0.25), 0.5, abs_tol=1e-8)
try:
    my_sqrt(-1)
except ValueError:
    pass
else:
    raise AssertionError("negative input must fail")
print("simple tests passed")
```

## 追问

**为什么 $x\lt 1$ 时上界是 1？**
因为 $[0,x]$ 可能不包含 $\sqrt{x}$，比如 $x=0.25$，根是 0.5。

**整数版返回 floor 还是 round？**
题面只说「根号下的数」时先问清楚。算法岗默认返回 floor，比如 8 得 2。

**为什么有人写 `lo + (hi-lo)//2`？**
为了防止 `lo+hi` 溢出。Python 的 int 精度无限，用不着；C++ 里要这么写。

**同一场问的「梯度下降的二分」是什么？**
是另一题：沿一维方向做线搜索，不变量还是区间套住极小值。先把 $\sqrt{x}$ 写对。

**负数怎么办？**
实数题直接拒绝，或者转到复数；整数题的定义域本来就是 $x\ge 0$。

## 真题记录

这题来自牛客候选人原帖：百川智能大模型实习一面，原帖没写面试时间，帖子发布于 2026-02-12，可信度 B。原话是 **“算法题:求根号下的数(二分)”**。

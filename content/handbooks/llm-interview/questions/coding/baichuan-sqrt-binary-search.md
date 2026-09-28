---
id: baichuan-sqrt-binary-search
section: coding
order: 183
level: B
title: 百川智能：求根号下的数，二分怎么写、边界怎么收？
quick: >-
  在 $[0,x]$（或 $[0,1]$ 当 $x<1$）上二分，比较 $\mathrm{mid}^2$ 与 $x$。整数题返回 floor；浮点题用绝对 /
  相对误差停。注意溢出用除法比较，以及 $x=0/1$ 特判。
tags:
  - Baichuan
  - Binary Search
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面 压力好大
    url: https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530
    type: candidate-first-hand
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“算法题:求根号下的数(二分)”**

错法： `mid * mid` 溢出，以及 $0\lt x\lt 1$ 时把上界设成 $x$（根号反而更大）。不变量：答案始终在 $[lo,hi]$ 内，每次丢掉不含根的一半。牛顿更快，面试先把二分讲清。同面可能还有 Attention，见 `baichuan-mha-handwrite`。

## 整数：floor($\sqrt{x}$)，用除法比大小

LeetCode 69 风格。$x\in\{0,1\}$ 直接返回。否则在 $[1,x]$（或 $[1,x/2]$）上二分：若 `mid <= x // mid` 说明 `mid` 还能变大，记答案并右移，否则左移。禁止 `mid * mid` 与 $x$ 比，32/64 位都会溢。

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

循环条件 `lo <= hi`；更新 `ans` 的一侧是「仍然 $\le\sqrt{x}$」的最大整数。写完用 $0,1,8,9$ 口头跑：8→2，9→3。

## 浮点：上界在 $x\lt 1$ 时改成 1

对实数 $\sqrt{x}$，区间取 $[0,\max(1,x)]$：因为 $x\in[0,1)$ 时 $\sqrt{x}\gt x$。停机：`hi - lo < eps` 或相对误差 $|mid^2-x|/x$。比较 `mid*mid` 在 float64 上对面试范围足够；极大 $x$ 仍可改成 `mid < x/mid`（注意 `mid=0`）。

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

牛顿：$x_{n+1}=\frac12(x_n+x/x_n)$，迭代少，但要讲初值和除零。二分的价值是不变量清晰、易证不会死循环。

## 追问

- **为何 $x\lt 1$ 上界是 1？** $[0,x]$ 可能不含 $\sqrt{x}$（例如 $x=0.25$，根是 0.5）。
- **整数版返回 floor 还是 round？** 题面说「根号下的数」时先问清；算法岗默认 floor，如 8→2。
- **`lo + (hi-lo)//2`？** 防 `lo+hi` 溢出，Python int 无限精度不必要，C++ 要。
- **和梯度下降二分？** 同面「梯度下降的二分」是另一题：沿一维线搜索，不变量仍是区间套住极小。先把 $\sqrt{x}$ 写对。
- **负数？** 实数题拒绝或转复数；整数题定义域 $x\ge 0$。

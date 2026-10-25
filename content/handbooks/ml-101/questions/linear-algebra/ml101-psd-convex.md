---
id: ml101-psd-convex
section: linear-algebra
order: 5
level: A
title: "半正定矩阵和 Hessian 怎样判断凸性？"
quick: "对定义在开凸域上的二阶连续可微函数，整个域内 Hessian 都半正定，等价于函数凸。半正定表示任意方向的二阶曲率都不为负；只看一个点还不够，正定是更强的条件，严格凸函数也可能在个别点的 Hessian 为零。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Stanford MS&E211: Lecture Notes 4, Convex and Concave Functions"
    url: https://web.stanford.edu/class/msande211x/Lecture042023.pdf
    type: primary
---

判断一个二阶连续可微函数是否凸，要检查整个开凸定义域上的 Hessian 是否处处半正定。只在某一个点看到非负特征值，只能说明这个点的二阶曲率，不能推出全局凸。

先看矩阵。对实对称矩阵 $H$，半正定的定义是

$$
z^\top Hz\ge0\quad\text{对所有 }z\in\mathbb R^d.
$$

$z$ 表示任意方向。这个二次型不为负，等价于 $H$ 的所有特征值非负；若对所有非零 $z$ 都严格大于零，就是正定。例如 $H=\operatorname{diag}(2,0)$ 半正定但不正定，第二个坐标方向的曲率为零。

对函数 $f(x)$，Hessian $\nabla^2 f(x)$ 的第 $(i,j)$ 项是 $\partial^2f/\partial x_i\partial x_j$。沿方向 $z$ 看一维函数 $g(t)=f(x+tz)$，它在 $t=0$ 的二阶导数是 $z^\top\nabla^2f(x)z$。因此，整个域上每个方向都向上弯或平坦，就得到凸性。二次函数 $f(x)=\tfrac12x^\top Qx+b^\top x+c$ 在 $Q$ 对称时 Hessian 就是 $Q$，其中 $b$ 是线性项系数、$c$ 是常数。凸性与半正定的联系见 [Stanford MS&E211 讲义第 9 页](https://web.stanford.edu/class/msande211x/Lecture042023.pdf#page=9)。

例如 $f(x_1,x_2)=x_1^2$ 的 Hessian 是 $\operatorname{diag}(2,0)$，函数凸，但沿 $x_2$ 方向完全平坦，最小点可以不唯一。若一个凸函数在内部点梯度为零，这个点就是全局最小点；需要唯一性时，还要进一步讨论严格凸等条件。

## 追问

**Hessian 在驻点半正定，就能判断它是极小点吗？**
一般不能。例如 $f(x)=x^3$ 在 0 的一阶、二阶导数都是 0，但 0 不是极小点。若 Hessian 在该驻点正定，则可据此判断严格局部极小；半正定时可能需要更高阶信息。

**严格凸是否要求 Hessian 处处正定？**
不要求。例如 $f(x)=x^4$ 严格凸，但在 0 的二阶导数为 0。处处正定是二阶可微情形下严格凸的充分条件，不能把它误读成所有严格凸函数都必须满足的必要条件。

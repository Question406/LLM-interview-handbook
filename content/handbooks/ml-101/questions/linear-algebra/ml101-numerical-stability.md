---
id: ml101-numerical-stability
section: linear-algebra
order: 7
level: A
title: "为什么不直接计算矩阵逆来解线性回归？"
quick: "线性回归通常直接用 QR 或 SVD 求最小二乘，避免显式计算逆矩阵。形成 $X^\\top X$ 会把满列秩矩阵的二范数条件数平方，近共线时更容易放大数值问题；即使改用 solve，也没有消除形成 $X^\\top X$ 这一步的影响。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "SciPy: Linear Algebra, Solving a Linear System"
    url: https://docs.scipy.org/doc/scipy/tutorial/linalg.html
    type: primary
  - title: "NumPy: numpy.linalg.lstsq"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html
    type: primary
---

我会直接调用最小二乘求解器，通常通过 QR 或 SVD 得到系数，避免先求 $X^\top X$ 的逆再乘标签。逆矩阵是说明闭式解的数学写法，实际计算并不需要把整张逆矩阵求出来。

设 $X\in\mathbb R^{n\times d}$ 是设计矩阵，$y\in\mathbb R^n$ 是标签，目标是最小化 $\|Xw-y\|_2$。在 $X$ 列满秩时，正规方程给出

$$
X^\top Xw=X^\top y,
\qquad
w=(X^\top X)^{-1}X^\top y.
$$

问题有两层。求逆比直接解方程做了更多工作，还引入额外数值误差，SciPy 教程也建议线性系统优先用 `solve`，见 [官方说明](https://docs.scipy.org/doc/scipy/tutorial/linalg.html#solving-a-linear-system)。但把代码改成 `solve(X.T @ X, X.T @ y)`，仍然先形成了 $X^\top X$。对列满秩的 $X$，二范数条件数满足 $\kappa_2(X^\top X)=\kappa_2(X)^2$，因此接近线性相关的列会让数值问题更严重。

例如两个特征都是同一面积，只是其中一个多一点测量扰动，两列就几乎重复。它们的区别本来就很小，再构造 $X^\top X$，求解时更容易丢掉区分这两列所需的精度。

对 $n\ge d$ 且列满秩的情形，可以做经济型 QR：$X=QR$，其中 $Q\in\mathbb R^{n\times d}$ 的列正交归一，$R\in\mathbb R^{d\times d}$ 为上三角矩阵。随后解 $Rw=Q^\top y$，用回代即可。若秩不足或需要判断有效秩，SVD 可以按奇异值大小处理，并给出最小范数解。`numpy.linalg.lstsq` 支持这类最小二乘语义，见 [官方文档](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html)。

## 追问

**换成 QR 或 SVD，近共线就不影响结果了吗？**
仍会影响。稳定算法减少额外计算误差，却不能让数据中本来很弱的信息变强。系数仍可能对观测扰动敏感，需要结合特征处理或 regularization。

**什么时候直接用 solve？**
已经有一个可逆方阵系统 $Aw=b$ 时，可以用 `solve(A,b)`。普通回归的设计矩阵常是矩形，应使用最小二乘接口；不能为调用 solve 而忽略正规方程带来的条件数问题。

**加 Ridge 后还需要选数值算法吗？**
需要。Ridge 改善目标的条件性，但仍可以通过增广最小二乘来求解：对目标 $\|Xw-y\|_2^2+\lambda\|w\|_2^2$，把 $\sqrt\lambda I$ 追加到 $X$ 下方、把零向量追加到 $y$ 下方，其中 $I$ 是 $d$ 维单位矩阵。这样可以继续用 QR 或 SVD，无需显式求逆。

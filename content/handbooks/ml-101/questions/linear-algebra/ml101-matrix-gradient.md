---
id: ml101-matrix-gradient
section: linear-algebra
order: 6
level: A
title: "怎么推矩阵形式的最小二乘梯度？"
quick: "当损失为 $J(w)=\\|Xw-y\\|_2^2/(2n)$、$n$ 为样本数时，最小二乘梯度是 $X^\\top(Xw-y)/n$。令残差 $r=Xw-y$，这是先对残差求梯度 $r/n$，再乘回 $X^\\top$。实现时检查 $X$ 是 $n\\times d$、梯度是 $d$ 维，再用小例子或有限差分核对符号与缩放。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "SciPy: Linear Algebra, Linear Least Squares"
    url: https://docs.scipy.org/doc/scipy/tutorial/linalg.html
    type: primary
  - title: "NumPy: numpy.linalg.lstsq"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html
    type: primary
---

最小二乘的矩阵梯度是 $X^\top(Xw-y)/n$，前提是损失定义为平均平方误差的一半。推导时先把残差单独记下来，再用链式法则，比较不容易漏转置或弄反符号。

设 $X\in\mathbb R^{n\times d}$，每行是一个样本，$w\in\mathbb R^d$ 是参数，$y\in\mathbb R^n$ 是标签。预测误差记作 $r=Xw-y$，损失为

$$
J(w)=\frac{1}{2n}\|Xw-y\|_2^2
=\frac{1}{2n}r^\top r.
$$

这里 $n$ 是样本数，$d$ 是参数数。对参数做一个小变化 $dw$，残差变化为 $dr=X\,dw$，所以损失的微分是

$$
dJ=\frac{1}{n}r^\top dr
=\frac{1}{n}r^\top X\,dw
=\left(\frac{1}{n}X^\top r\right)^\top dw.
$$

按 $dJ=(\nabla_wJ)^\top dw$ 识别系数，就得到所需梯度。维度也对得上：$X^\top$ 是 $d\times n$，乘 $n$ 维残差，结果是 $d$ 维。最小二乘目标及求导后得到的正规方程，见 [SciPy 线性代数教程](https://docs.scipy.org/doc/scipy/tutorial/linalg.html#solving-linear-least-squares-problems-and-pseudo-inverses)。

用一个数值例子检查符号：$X=(1,2)^\top$，$y=(1,2)^\top$，$w=0$，此时残差是 $(-1,-2)^\top$，梯度为 $-5/2$。梯度下降减去梯度，会让 $w$ 往正方向走，预测从 0 向标签靠近，方向正确。

令梯度为零得到 $X^\top Xw=X^\top y$。这里不需要假设 $X^\top X$ 可逆才能求导；列满秩只在讨论最优系数是否唯一时才需要。实际求解可以用专门的最小二乘接口，见 [NumPy lstsq 文档](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html)。

## 追问

**损失没有前面的二分之一，梯度会怎样？**
会多一个 2。若写成 $J(w)=\|Xw-y\|_2^2/n$，梯度是 $2X^\top(Xw-y)/n$。先说清楚求和、求平均和二分之一的约定，再比较实现。

**加 L2 正则后怎么变？**
若目标增加 $\lambda\|w\|_2^2/2$，就再加 $\lambda w$，其中 $\lambda\ge0$ 控制惩罚强度。若截距不参与正则，对应梯度分量不加这项。

**怎么检查手推和实现一致？**
用有限差分。对第 $j$ 维比较 $[J(w+he_j)-J(w-he_j)]/(2h)$ 与解析梯度，其中 $e_j$ 是第 $j$ 个坐标方向，$h$ 是小步长。步长过大会有截断误差，过小又容易受舍入影响，可比较几个步长下的结果。

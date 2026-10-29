---
id: ml101-rank-nullspace
section: linear-algebra
order: 3
level: A
title: "矩阵秩和零空间怎样解释参数不可辨识？"
quick: "矩阵秩表示独立信息方向的数量，零空间则包含改变参数却不改变线性预测的方向。若设计矩阵 $X$ 的列不满秩，就存在非零 $v$ 使 $Xv=0$，因此 $w$ 和 $w+v$ 给出相同拟合，数据无法唯一确定系数；要删合重复信息或用额外约束选解。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "SciPy: scipy.linalg.null_space"
    url: https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.null_space.html
    type: primary
  - title: "NumPy: numpy.linalg.matrix_rank"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.matrix_rank.html
    type: primary
---

线性模型的参数能否由数据唯一确定，要看设计矩阵是否列满秩。比如两列特征完全相同，预测只依赖两个系数的和；把一个系数加 1、另一个减 1，所有训练预测都不变。

设 $X\in\mathbb R^{n\times d}$，每行是一条样本、每列是一个特征，模型预测为 $Xw$，$w\in\mathbb R^d$ 是参数。矩阵的秩是独立列方向的数量，零空间定义为

$$
\mathcal N(X)=\{v\in\mathbb R^d:Xv=0\},
\qquad
\dim\mathcal N(X)=d-\operatorname{rank}(X).
$$

若秩小于 $d$，就能找到非零的 $v$。于是 $X(w+tv)=Xw$ 对任意实数 $t$ 都成立：沿这个方向移动参数，数据看不到变化，这就是线性预测里的参数不可辨识。普通最小二乘损失也不会改变，因此最优系数不唯一。

例如 $X=\begin{pmatrix}1&1\\2&2\end{pmatrix}$ 的秩是 1，$v=(1,-1)^\top$ 在零空间中。参数 $(3,0)^\top$ 和 $(1,2)^\top$ 都预测 $(3,6)^\top$。SciPy 用 SVD 构造零空间的正交基，见 [null_space 文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.null_space.html)。

我会先检查特征定义，删除或合并重复测量。若要保留全部特征，可以增加约束或用 regularization 选出一个解；这增加了建模选择，没有让数据突然提供区分这些参数的新信息。若只是接近线性相关，系数可能仍唯一，但会对噪声敏感。

## 追问

**样本比参数多，就一定能唯一确定系数吗？**
不能。$n\ge d$ 只是列满秩的必要条件，两列完全重复时，增加同类样本也不能消除零空间。还要检查列之间是否独立。

**浮点计算中怎么判断秩？**
通常看奇异值是否大于容差，而不直接比较是否等于零。NumPy 的 `matrix_rank` 就使用这种方法，容差考虑矩阵尺寸、最大奇异值和浮点精度，见 [官方说明](https://numpy.org/doc/stable/reference/generated/numpy.linalg.matrix_rank.html)。实际观测噪声更大时，还要按测量精度选择阈值。

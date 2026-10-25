---
id: ml101-eigen-svd
section: linear-algebra
order: 4
level: A
title: "特征值分解和 SVD 有什么区别？"
quick: "特征值描述方阵中方向不变、只被缩放的向量；SVD 则把任意实矩阵拆成两组正交方向和非负伸缩量。一般方阵不一定能做特征值对角化，但任何实矩阵都有 SVD；分析对称矩阵的曲率常用特征值，做低秩近似或求解最小二乘常用 SVD。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "NumPy: numpy.linalg.eig"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.eig.html
    type: primary
  - title: "NumPy: numpy.linalg.svd"
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html
    type: primary
---

特征值分解主要回答「哪些方向经过方阵后仍在同一条线上」，SVD 则描述一个矩阵在输入、输出空间之间怎样旋转或反射并伸缩。矩形矩阵也能做 SVD，一般方阵却不保证有足够的特征向量来对角化。

对方阵 $A\in\mathbb R^{d\times d}$，特征向量 $v\ne0$ 满足

$$
Av=\lambda v.
$$

$\lambda$ 是对应特征值，表示该方向上的缩放，负值还会反向。若能找到 $d$ 个线性独立的特征向量，把它们排成可逆矩阵 $P$，才有 $A=P\Lambda P^{-1}$，其中 $\Lambda$ 的对角线存特征值。实对称矩阵可以用正交特征向量分解，普通实矩阵则可能出现复特征值。见 [NumPy eig 文档](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eig.html)。

对任意 $A\in\mathbb R^{m\times n}$，完整 SVD 是

$$
A=U\Sigma V^\top.
$$

这里 $U$ 为 $m\times m$ 正交矩阵，$V$ 为 $n\times n$ 正交矩阵，$\Sigma$ 为 $m\times n$ 的矩形对角矩阵，对角线上的奇异值 $\sigma_i\ge0$。先用 $V^\top$ 换输入坐标，再由 $\Sigma$ 伸缩，最后用 $U$ 换到输出坐标。NumPy 还支持缩小中间维度的经济型输出，见 [SVD 文档](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html)。

一个能分清两者的例子是 $A=\begin{pmatrix}0&1\\0&0\end{pmatrix}$。它的特征值全是 0，却不是零矩阵，也没有两个线性独立的特征向量，不能对角化；它的奇异值是 1 和 0，仍能正确描述这个变换。

## 追问

**奇异值就是特征值的绝对值吗？**
对实对称矩阵成立，一般矩阵不成立。一般关系是 $A^\top A=V\Sigma^\top\Sigma V^\top$，所以非零奇异值的平方恰好是 $A^\top A$ 的非零特征值；比较完整的谱时，还要按矩阵维度补上零特征值。

**做 PCA 时应该选哪种分解？**
两种都可以：对中心化数据矩阵直接做 SVD，或对协方差矩阵做特征值分解。直接 SVD 可以省去显式形成协方差矩阵；主方向来自右奇异向量，解释的方差与奇异值平方成比例。

---
id: ml101-conditioning
section: linear-algebra
order: 8
level: A
title: 条件数大为什么会让训练和系数不稳定？
quick: >-
  条件数大表示不同方向的伸缩差异很大，输入或标签的小扰动可能引起很大的系数变化。对满列秩设计矩阵，二范数条件数是最大与最小奇异值之比，平方损失 Hessian
  的条件数还是它的平方；可检查尺度、共线性和 regularization，但要区分数值算法与问题本身的敏感性。
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'NumPy: numpy.linalg.cond'
    url: 'https://numpy.org/doc/stable/reference/generated/numpy.linalg.cond.html'
    type: primary
  - title: 'Cornell CS4787/5777: Lecture 5, Conditioning'
    url: 'https://www.cs.cornell.edu/courses/cs4787/2025fa/lectures/lecture5.html'
    type: primary
---

条件数大时，模型在某些方向上反应很强，在另一些方向上几乎不动：前者限制学习率，后者让迭代推进缓慢，求出的系数也可能对数据扰动敏感。这里要区分设计矩阵的条件数和训练目标 Hessian 的条件数，它们相关但数值不相同。

对列满秩的实矩阵 $X$，二范数条件数为

$$
\kappa_2(X)=\frac{\sigma_{\max}(X)}{\sigma_{\min}(X)}.
$$

$\sigma_{\max}$ 与 $\sigma_{\min}$ 分别是最大、最小奇异值，衡量矩阵在不同方向的伸缩量。最小奇异值趋近零，某个方向上的信息就很弱；恰好为零时失去列满秩，可以把这一逆问题的条件数视为无穷。NumPy 的 `cond` 默认用 SVD 计算二范数条件数，见 [官方定义](https://numpy.org/doc/stable/reference/generated/numpy.linalg.cond.html)。

一个具体例子是 $X=\operatorname{diag}(1,10^{-6})$，条件数为 $10^6$。解 $Xw=y$ 时，只把第二个标签分量增加 $10^{-6}$，第二个系数就会增加 1，因为这一方向被矩阵缩小了百万倍。这说明微小的数据变化可能对应明显的参数变化；是否达到最坏情况，取决于扰动的方向。

对损失 $J(w)=\|Xw-y\|_2^2/(2n)$，Hessian 是 $H=X^\top X/n$，其中 $n$ 是样本数。若 $X$ 列满秩，就有 $\kappa_2(H)=\kappa_2(X)^2$。这个二次目标的等高线会很狭长，普通梯度下降需要照顾最大曲率，低曲率方向却收敛得慢。条件性与优化速度的关系见 [Cornell CS4787 第 5 讲](https://www.cs.cornell.edu/courses/cs4787/2025fa/lectures/lecture5.html)。

我会先检查特征单位和重复信息。尺度差异可以通过缩放改善，近共线则可能需要合并特征或 regularization。对正定 $H$ 加 $\lambda I$ 后，各特征值都增加 $\lambda$，条件数变为 $(\lambda_{\max}(H)+\lambda)/(\lambda_{\min}(H)+\lambda)$，其中 $\lambda>0$ 是 L2 惩罚对应的系数。不过 regularization 也改变了估计目标，要用验证数据选强度。

## 追问

**条件数大，预测也一定不稳定吗？**
不一定。某个方向上的系数可以大幅变化，但乘回训练矩阵后变化很小。新样本若仍沿原来的相关关系分布，预测可能稳定；若进入训练数据很少约束的方向，风险就更大。

**用更高浮点精度就能解决吗？**
只能减少舍入误差。它不能消除标签噪声、特征测量误差或参数不可辨识。稳定求解器、数据处理和 regularization 分别处理不同来源的问题。

**standardization 能保证条件数小吗？**
不能。两列即使都缩放到单位方差，也可能几乎相同。standardization 能处理单位差异，但不会消除它们之间的线性依赖。

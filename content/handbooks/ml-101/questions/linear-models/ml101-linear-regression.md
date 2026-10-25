---
id: ml101-linear-regression
section: linear-models
order: 1
level: S
title: "线性回归的最小二乘解怎么推？"
quick: "线性回归用特征的线性组合预测连续值，最小二乘选择让残差平方和最小的参数。对目标求导得到正规方程；设计矩阵列满秩时解唯一，秩不足时用伪逆或正则化，数值实现通常优先用 QR 或 SVD。"
tags:
  - Machine Learning
  - linear-models
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Dive into Deep Learning: Linear Regression"
    url: https://d2l.ai/chapter_linear-regression/linear-regression.html
    type: primary
---

线性回归学习每个输入特征的系数，使预测值尽量接近真实值。比如用面积和房龄预测价格，面积的系数表示在模型中保持其他特征不变时，面积每增加一个单位，预测价格变化多少。

把 $n$ 个样本和 $d$ 个特征写成矩阵 $X\in\mathbb{R}^{n\times d}$，将截距并入一列常数 1，目标向量记作 $y$，系数记作 $w$。最小化：

$$J(w)=\frac12\lVert Xw-y\rVert_2^2.$$

对 $w$ 求导得 $\nabla J=X^\top(Xw-y)$。令梯度为零，得到 $X^\top Xw=X^\top y$。$X$ 列满秩时，理论上有 $w=(X^\top X)^{-1}X^\top y$。

实际计算一般直接解最小二乘问题，不显式求逆。特征高度相关时，$X^\top X$ 会加重数值不稳定；QR、SVD 或 Ridge 更合适。拟合最小二乘并不要求误差必须服从正态，正态假设用于某些概率解释和推断。

## 面试追问

**线性回归只能拟合直线吗？**
它要求对参数线性。把平方项、交互项等变成固定特征后，仍可使用线性回归，输入到输出的关系可以是曲线。

**特征比样本多会怎样？**
无正则解可能不唯一，训练误差也可能很低。可以用最小范数解或正则化，并通过独立验证控制泛化风险。

---
id: ml101-pca
section: unsupervised
order: 4
level: S
title: "PCA 为什么能降维？怎么从 SVD 得到主成分？"
quick: "PCA 在中心化数据中寻找方差最大的正交方向，保留前几个方向，用较少维度近似原始数据。对中心化矩阵做 SVD，右奇异向量就是主成分方向；PCA 不使用标签，保留高方差不保证保留最有预测价值的信息。"
tags:
  - Machine Learning
  - unsupervised
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Principal component analysis"
    url: https://scikit-learn.org/stable/modules/decomposition.html
    type: primary
---

PCA 把多个相关特征重新组合成正交坐标，优先保留数据变化最大的方向。在固定维度的线性正交投影中，这也对应最小化平方重建误差。

例如身高的厘米值和英寸值几乎描述同一个变化方向，两列可以用一个坐标近似表示。若不同列单位差很多，要先决定是否标准化，因为单位会影响谁拥有较大方差。

设中心化后的数据矩阵 $X\in\mathbb{R}^{n\times d}$，做分解 $X=U\Sigma V^\top$。取 $V$ 的前 $k$ 列为 $V_k$，低维表示是：

$$Z=XV_k=U_k\Sigma_k.$$

$V_k$ 的列是主方向，$\Sigma$ 的奇异值平方与各方向解释方差成比例。选择 k 可以参考解释方差与重建误差，也要验证下游任务表现。

PCA 本身只中心化，不自动保证各原始特征同方差。预处理和主方向都应在训练数据拟合，再用于验证与新样本，避免测试分布参与选择。

## 面试追问

**主成分不相关就代表独立吗？**
不代表。零协方差只排除线性相关，一般分布仍可能有更复杂依赖；联合高斯等特殊条件下才可从不相关推出独立。

**解释方差达到 95% 就不会损失分类信息吗？**
不能保证。标签可能恰好由一个低方差方向决定，PCA 没有使用标签，不知道哪个方向对分类最重要。

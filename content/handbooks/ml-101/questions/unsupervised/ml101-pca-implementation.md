---
id: ml101-pca-implementation
section: unsupervised
order: 12
level: A
title: 用中心化与 SVD 实现 PCA，验证投影、重构和误差
quick: 先用训练集均值中心化，对中心化矩阵做 SVD，取前 K 个右奇异向量作为主轴。新数据减同一个训练均值后投影，乘回主轴再加均值即可重构。重构平方误差等于被丢弃奇异值的平方和；主轴符号可能翻转，验证时应比较重构或子空间，不能要求每个向量元素完全相同。
tags: [ML Fundamentals, Linear Algebra, Coding]
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-23
sources:
  - title: NumPy linalg.svd
    url: https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html
    type: primary
  - title: scikit-learn PCA
    url: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

仅用 NumPy 实现中心化 PCA，提供拟合、降维投影与从低维表示近似重建的接口，不自动按特征标准差缩放。

### 输入与接口

实现 SmallPCA，提供 fit(X,k)、transform(X)、`inverse_transform`(Z)。拟合X为N×D有限矩阵，N≥2，D≥1，1≤k≤min(N,D)；transform输入M×D，inverse_transform输入M×k。

### 输出与约束

fit 返回self并保存 mean(D)、components(k×D，按奇异值降序排列的正交主轴)、`singular_values`(min(N,D)，包含全部奇异值)、`explained_variance`(k)、`explained_variance_ratio`(k)。方差以N-1为分母；比例以所有方向方差之和为分母，总方差为0时比例返回全0。

投影必须使用拟合时的mean，transform返回M×k；inverse_transform返回M×D并加回mean。主轴正负号均可，重根对应的正交基也可不同；评估投影/重建和子空间等价性，不要求逐元素复现某个SVD库的符号。拟合、投影均不修改调用者输入。

### 示例

```text
X=[[-1,-1],[0,0],[1,1]]，k=1
mean -> [0,0]
一种合法components -> [[1/sqrt(2),1/sqrt(2)]]
transform(X) -> [[-sqrt(2)],[0],[sqrt(2)]]
inverse_transform(transform(X)) -> X
explained_variance -> [2]，explained_variance_ratio -> [1]
```

## 解题思路与参考答案

PCA 可以通过中心化矩阵的 SVD 实现。这里手写的是 PCA 的数据处理与投影流程，使用 NumPy 完成 SVD 数值分解，不重新实现分解算法。

训练矩阵 X 有 n 行、d 列，均值为 $\mu$。令 $X_c=X-\mu=USV^T$，选 $V^T$ 的前 K 行作为主轴 C，则投影 $Z=X_cC^T$，重构 $\hat X=ZC+\mu$。样本协方差在这些方向上的方差为 $s_j^2/(n-1)$。

本练习要求 n≥2、d≥1，K 为 1 到 min(n,d) 的整数；只中心化，不自动按列标准化，不做 whitening。新数据必须复用训练均值，不能在测试集上重新拟合。常量数据的总方差为零时，把解释方差比例设为零；主轴本身没有可辨认的方差信息。

```python
import numpy as np


class SmallPCA:
    def fit(self, X, k):
        X = np.asarray(X, dtype=float)
        if X.ndim != 2 or X.shape[0] < 2 or X.shape[1] < 1 or not np.isfinite(X).all():
            raise ValueError("X must be finite with at least two rows")
        if type(k) is not int or not 1 <= k <= min(X.shape):
            raise ValueError("invalid k")
        self.mean = X.mean(axis=0)
        centered = X - self.mean
        _, singular_values, vt = np.linalg.svd(centered, full_matrices=False)
        self.components = vt[:k].copy()
        self.singular_values = singular_values.copy()
        all_variances = singular_values ** 2 / (len(X) - 1)
        self.explained_variance = all_variances[:k]
        total = all_variances.sum()
        self.explained_variance_ratio = self.explained_variance / total if total > 0 else np.zeros(k)
        return self

    def transform(self, X):
        if not hasattr(self, "mean"):
            raise ValueError("fit PCA first")
        X = np.asarray(X, dtype=float)
        if X.ndim != 2 or X.shape[1] != len(self.mean) or not np.isfinite(X).all():
            raise ValueError("prediction features must match training")
        return (X - self.mean) @ self.components.T

    def inverse_transform(self, Z):
        if not hasattr(self, "components"):
            raise ValueError("fit PCA first")
        Z = np.asarray(Z, dtype=float)
        if Z.ndim != 2 or Z.shape[1] != len(self.components) or not np.isfinite(Z).all():
            raise ValueError("projected dimension must match")
        return Z @ self.components + self.mean
```

例如 X=[[−1,−1],[0,0],[1,1]]，均值为零，所有点在一条直线上。K=1 已能保留全部非零方差，重构应与原数据相同。主轴可以是 $(1,1)/\sqrt2$，也可以整体取负；只要投影与逆变换采用同一主轴，重构结果相同。

在平方欧氏误差下，保留前 K 个主轴得到最佳 K 维线性重构。对训练集，$\lVert X-\hat X\rVert_F^2=\sum_{j>K}s_j^2$。这个等式很适合检验实现；它说的是输入重构，不保证下游分类指标最好。

薄 SVD 主要计算成本约为 $O(nd\min(n,d))$，投影新数据约为 $O(n_{new}dK)$。实现还保存薄分解相关数组与中心化数据，空间不是只有 K×d 主轴；大规模问题可考虑随机化或增量方法，再验证近似误差。

**为什么不能直接比较两次的主轴元素？**
除符号不唯一外，重复奇异值对应的子空间还可以选择不同正交基。应比较重构、投影矩阵或子空间；若 K 刚好截断一个重复值空间，选出的 K 维子空间也可能不同，但训练重构误差相同。

**特征标准化应该放在哪里？**
若不同单位不应主导 PCA，可以先用训练集统计量缩放，再拟合 PCA。该选择改变了优化的距离和方差目标；不能把标准化版与仅中心化版的结果当成实现应该完全一致。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

三个点完全落在一条直线上，保留一维就应能重建原数据，解释方差比例为 1。主成分正负号都合法，因此比较重建结果，避免直接要求某个向量符号。

```python
import numpy as np
X = np.array([[-1., -1.], [0., 0.], [1., 1.]])
model = SmallPCA().fit(X, 1)
np.testing.assert_allclose(model.inverse_transform(model.transform(X)), X, atol=1e-12)
np.testing.assert_allclose(model.explained_variance_ratio, [1])
np.testing.assert_allclose(model.components @ model.components.T, [[1]])
print("simple tests passed")
```

---
id: ml101-batchnorm-backward
section: neural-networks
order: 11
level: A
title: 手写 BatchNorm 的训练前向、推理与 backward
quick: >-
  训练时按特征计算 batch 均值和方差，standardization 后用 gamma、beta
  缩放平移；反向要把均值和方差对所有样本的依赖一起算进去。推理使用累计统计量，不再根据当前 batch 重算。练习实现明确使用除以 N 的 batch
  方差和旧统计量保留率，不能直接混用其他框架的 momentum 或 running variance 约定。
tags:
  - ML Fundamentals
  - Backpropagation
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-23T00:00:00.000Z
sources:
  - title: Batch Normalization original paper
    url: 'https://arxiv.org/abs/1502.03167'
    type: primary
  - title: PyTorch BatchNorm1d documentation
    url: 'https://docs.pytorch.org/docs/stable/generated/torch.nn.BatchNorm1d.html'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

仅用 NumPy 实现二维 BatchNorm 的训练前向、推理前向，以及训练前向对应的 backpropagation，不调用自动微分。

### 输入与接口

实现 BatchNorm1D(features,*,momentum=0.9,eps=0.00001)，其 forward(X,*,training=True) 返回 (output,cache)；实现 `batchnorm_backward`(upstream,cache)。features=D≥1；X 为 N×D 有限矩阵且 N≥1；eps>0；0≤momentum<1；upstream 与 output 同形。

### 输出与约束

每列独立计算 batch 均值和除以 N 的方差，normalization 后乘 gamma、加 beta。初始化 gamma=全1、beta=全0、`running_mean`=全0、`running_var`=全1，均为 D 维。训练时 running 统计量更新为 momentum×旧值+(1-momentum)×当前 batch 统计量，保存 backward 所需 cache。

推理只使用 running 统计量，不修改它们，cache 返回 None。这里 `running_var` 也使用除以 N 的方差，不做无偏修正。backward 只接收训练 cache，返回 (dx,dgamma,dbeta)，形状分别为 N×D、D、D；梯度针对标量目标与给定 upstream 的链式关系，不再按 batch 平均，不更新 gamma/beta。

### 示例

```text
layer=BatchNorm1D(2)
out,cache=layer.forward([[4,8]])
out -> [[0,0]]
batchnorm_backward([[2,3]],cache)
-> (dx=[[0,0]],dgamma=[0,0],dbeta=[2,3])
此后 running_mean -> [0.4,0.8]，running_var -> [0.9,0.9]
```

## 解题思路与参考答案

训练态 BatchNorm 的一个输出依赖整列样本，因为均值和方差都是从这一列算出来的。反向时只把上游梯度乘 gamma 再除标准差，会漏掉这两条依赖路径。

本题只处理 N×D 的二维输入，每列独立 normalization。对一列有 $\mu=\sum_i x_i/N$、$v=\sum_i(x_i-\mu)^2/N$、$\hat x_i=(x_i-\mu)/\sqrt{v+\epsilon}$，输出 $y_i=\gamma\hat x_i+\beta$。若上游梯度为 g，则 $d\beta=\sum_i g_i$、$d\gamma=\sum_i g_i\hat x_i$，输入梯度可写为

$$
dx_i=\frac{\gamma}{N\sqrt{v+\epsilon}}\left(Ng_i-\sum_jg_j-\hat x_i\sum_jg_j\hat x_j\right).
$$

通用练习约定：N≥1、D≥1；epsilon>0；momentum 表示保留多少旧统计量。训练时和 running variance 的更新都采用除以 N 的方差，未做无偏修正。这个教学约定与 PyTorch 的 running variance 更新不完全相同；PyTorch 训练 normalization 用有偏方差，累计方差更新使用 unbiased estimate，其 momentum 还表示新统计量权重。

```python
import numpy as np


class BatchNorm1D:
    def __init__(self, features, *, momentum=0.9, eps=1e-5):
        if type(features) is not int or features < 1:
            raise ValueError("features must be positive")
        if not 0 <= momentum < 1 or not np.isfinite(eps) or eps <= 0:
            raise ValueError("invalid momentum or eps")
        self.gamma = np.ones(features)
        self.beta = np.zeros(features)
        self.running_mean = np.zeros(features)
        self.running_var = np.ones(features)
        self.momentum, self.eps = momentum, eps

    def forward(self, X, *, training=True):
        X = np.asarray(X, dtype=float)
        if (
            X.ndim != 2
            or X.shape[0] == 0
            or X.shape[1] != len(self.gamma)
            or not np.isfinite(X).all()
        ):
            raise ValueError("X must be a finite N by D matrix")
        if training:
            mean = X.mean(axis=0)
            variance = ((X - mean) ** 2).mean(axis=0)
            m = self.momentum
            self.running_mean = m * self.running_mean + (1 - m) * mean
            self.running_var = m * self.running_var + (1 - m) * variance
        else:
            mean, variance = self.running_mean, self.running_var
        inverse_std = 1 / np.sqrt(variance + self.eps)
        normalized = (X - mean) * inverse_std
        cache = (normalized, inverse_std, self.gamma.copy()) if training else None
        return normalized * self.gamma + self.beta, cache


def batchnorm_backward(upstream, cache):
    if cache is None:
        raise ValueError("this backward requires a training cache")
    normalized, inverse_std, gamma = cache
    g = np.asarray(upstream, dtype=float)
    if g.shape != normalized.shape or not np.isfinite(g).all():
        raise ValueError("gradient shape must match the cached output")
    n = len(g)
    dbeta = g.sum(axis=0)
    dgamma = (g * normalized).sum(axis=0)
    dx = gamma * inverse_std / n * (n * g - dbeta - normalized * dgamma)
    return dx, dgamma, dbeta
```

例如一列输入 [1,3]，gamma=1、beta=0，训练均值为 2，方差为 1，输出约为 [−1,1]。若上游梯度全为 1，输入梯度为零，beta 梯度为 2：standardization 后这列输出的和不随整体输入平移而改变。

前向、反向均需 $O(ND)$ 时间；训练缓存主要是 standardization 输入，占 $O(ND)$ 空间，参数与累计统计量为 $O(D)$。调用者负责在计算梯度后更新 gamma、beta；running 统计量没有作为参数参与这个 backward。

**一个样本能训练吗？**
这份二维练习允许 N=1，此时 batch 方差为零，输出等于 beta，输入梯度为零，学习信号退化。框架可能直接限制这种情况，不能把本练习的 edge-case conventions 当成所有库的默认行为。

**推理为何不能继续用当前 batch？**
同一个样本的输出会随一起送入的其他样本变化，单样本时还可能退化。冻结累计统计量后，输出只依赖该样本与固定参数；其质量仍取决于累计统计量是否代表推理数据。

**怎样做数值梯度检查？**
固定输入与任意上游矩阵，对标量输出内积做中心差分，分别检查 X、gamma 和 beta。每次训练前向都会更新 running 统计量，但训练输出不使用这些累计量；检查推理路径时则应固定状态。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

单个样本 normalization 后为零，输入梯度和 gamma 梯度也为零，beta 梯度等于上游梯度。再用两样本均值为 2 的例子检查输出正负对称。

```python
import numpy as np

layer = BatchNorm1D(2)
out, cache = layer.forward([[4, 8]])
dx, dgamma, dbeta = batchnorm_backward([[2, 3]], cache)
np.testing.assert_allclose(out, 0)
np.testing.assert_allclose(dx, 0)
np.testing.assert_allclose(dgamma, 0)
np.testing.assert_allclose(dbeta, [2, 3])
out, _ = BatchNorm1D(1).forward([[1], [3]])
np.testing.assert_allclose(out[:, 0], [-1, 1], atol=1e-5)
print("simple tests passed")
```

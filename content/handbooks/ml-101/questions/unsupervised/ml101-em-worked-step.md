---
id: ml101-em-worked-step
section: unsupervised
order: 11
level: A
title: 对一维高斯混合模型，手算并实现一次 EM 更新
quick: E 步用当前混合权重和高斯密度计算每个样本属于各成分的责任度，M 步把责任度当权重更新混合比例、均值和方差。一次迭代先算完全部责任度，再统一更新参数；稳定实现用 log-sum-exp 归一化，并对方差设置明确下界。EM 通常只找到局部解，需要检查观测数据的似然。
companies: [google]
tags: [Machine Learning, EM, Coding]
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: Google MLE L5 候选人面经：EM 主题
    url: https://www.1point3acres.com/interview/thread/894226
    type: secondary
  - title: scikit-learn Gaussian mixture models and EM
    url: https://scikit-learn.org/stable/modules/mixture.html
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

针对一维高斯混合模型，实现概率评分和一次完整 EM 参数更新。混合分量数量固定，不做模型选择。

### 输入与接口

实现 `gmm_scores`(x,weights,means,variances,*,`var_floor`=1e-6) 与 `gmm_em_step`(...)，后者参数相同。x为N维非空有限观测；其他三个数组均为K维非空有限向量；weights严格为正且和为1；variances≥`var_floor`>0。合法数据保证各分量的数值责任度和为正。

### 输出与约束

`gmm_scores` 返回 (responsibility,loglik)：前者形状N×K，表示每个观测属于每个分量的后验概率，每行和为1；后者是所有观测在混合密度下的自然对数似然之和。计算须避免直接指数化很小概率引起的下溢。

`gmm_em_step` 计算一次基于旧参数的责任度，再用它更新混合权重、均值、方差；方差使用以更新后均值为中心的加权平方偏差，并截到至少 `var_floor`，不做无偏修正。返回字典 weights、means、variances、responsibility、`loglik_before`、`loglik_after`；responsibility 对应更新前参数，after 对应新参数。不修改输入，也不额外迭代至收敛；分量顺序不重排。

### 示例

```text
x=[0,2]，weights=[0.5,0.5]，means=[0,2]，variances=[1,1]
r=1/(1+exp(-2))≈0.880797
responsibility -> [[r,1-r],[1-r,r]]
new weights -> [0.5,0.5]
new means -> [0.238406,1.761594]（约值）
new variances -> [0.419974,0.419974]（约值）
```

## 解题思路与参考答案

EM 把“不知道每个点来自哪个成分”的问题拆成两步：先用旧参数估计归属概率，再按这些概率重新拟合参数。高斯混合模型中，这些软归属称为责任度。

面经只确认问过 EM，没有指定分布、数据或手算要求。以下一维 GMM 是手册重构练习，便于完整走过公式和代码。设有 n 个数 $x_i$、K 个成分，权重 $\pi_k>0$ 且和为 1，各成分参数为均值 $\mu_k$ 和方差 $v_k>0$。E 步计算

$$
r_{ik}=\frac{\pi_k\mathcal N(x_i;\mu_k,v_k)}{\sum_j\pi_j\mathcal N(x_i;\mu_j,v_j)}.
$$

M 步令 $N_k=\sum_i r_{ik}$，更新

$$
\pi_k'=N_k/n,\qquad \mu_k'=\frac{\sum_i r_{ik}x_i}{N_k},\qquad
v_k'=\frac{\sum_i r_{ik}(x_i-\mu_k')^2}{N_k}.
$$

方差使用新的均值。若在遍历样本时不断覆盖旧均值，再继续算后续责任度，就混合了两轮参数，不再是这套 EM 更新。

取 x=[0,2]，初始权重各 0.5，均值为 0 和 2，方差均为 1。x=0 对第一成分的责任度是 $1/(1+e^{-2})\approx0.880797$，x=2 的责任度对称。两成分有效样本数都是 1，新均值约为 0.238406、1.761594，新方差约为 0.419974，权重保持各 0.5。

```python
import numpy as np


def gmm_scores(x, weights, means, variances, *, var_floor=1e-6):
    x, weights, means, variances = [np.asarray(v, dtype=float)
                                    for v in (x, weights, means, variances)]
    if any(v.ndim != 1 or len(v) == 0 or not np.isfinite(v).all()
           for v in (x, weights, means, variances)):
        raise ValueError("inputs must be nonempty finite vectors")
    if not (weights.shape == means.shape == variances.shape):
        raise ValueError("component parameter shapes must match")
    if not np.isfinite(var_floor) or var_floor <= 0:
        raise ValueError("var_floor must be positive")
    if (weights <= 0).any() or not np.isclose(weights.sum(), 1):
        raise ValueError("weights must be positive and sum to one")
    if (variances < var_floor).any():
        raise ValueError("initial variances must respect var_floor")
    weights = weights / weights.sum()
    with np.errstate(over="raise", invalid="raise"):
        log_joint = (np.log(weights)[None, :] - 0.5 *
                     (np.log(2 * np.pi) + np.log(variances)[None, :] +
                      (x[:, None] - means[None, :]) ** 2 / variances[None, :]))
    maximum = log_joint.max(axis=1, keepdims=True)
    log_total = maximum + np.log(np.exp(log_joint - maximum).sum(axis=1, keepdims=True))
    responsibility = np.exp(log_joint - log_total)
    return responsibility, float(log_total.sum())


def gmm_em_step(x, weights, means, variances, *, var_floor=1e-6):
    responsibility, before = gmm_scores(x, weights, means, variances,
                                         var_floor=var_floor)
    x = np.asarray(x, dtype=float)
    effective = responsibility.sum(axis=0)
    if (effective <= 0).any():
        raise ValueError("component has zero numerical responsibility")
    new_weights = effective / len(x)
    new_means = (responsibility * x[:, None]).sum(axis=0) / effective
    new_variances = (responsibility * (x[:, None] - new_means) ** 2).sum(axis=0) / effective
    new_variances = np.maximum(new_variances, var_floor)
    _, after = gmm_scores(x, new_weights, new_means, new_variances,
                          var_floor=var_floor)
    return {"weights": new_weights, "means": new_means, "variances": new_variances,
            "responsibility": responsibility, "loglik_before": before,
            "loglik_after": after}
```

`gmm_scores` 在 log 域计算联合密度，通过减去行最大值做稳定归一化。方差按练习约定限制在不小于 var_floor 的范围内；这相当于一维方差下界约束，不是给估计式随意加上一个常数。若某成分的数值责任度已经全为零，代码要求调用者重新初始化等明确处理。

对一维 K 成分，E 步和 M 步都需要 $O(nK)$ 时间，责任度矩阵占 $O(nK)$ 空间。可以用分批累积充分统计量减少内存，但不能在一个 E 步内随样本更新参数。

**为什么要看似然而不是只看均值变化？**
观测数据的目标是 $\sum_i\log\sum_k\pi_k\mathcal N(x_i;\mu_k,v_k)$。按上述固定约束完成精确 E、M 步，目标应在数值误差范围内不下降；明显下降可以提示实现错误。即使目标稳定，也不证明找到全局最优。

**怎样验证这一轮？**
检查每行责任度和为 1，权重和为 1，方差不小于下界；用上面的对称例子核对均值和方差，再在多轮迭代中观察似然单调性。成分编号互换不改变混合密度，比较两组结果时应考虑编号置换。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

对称的两个样本与两个高斯分量可以手算 responsibility，且权重保持各 0.5。每行责任度之和应为 1，单步更新后对数似然不下降。

```python
import numpy as np
import math
result = gmm_em_step([0, 2], [0.5, 0.5], [0, 2], [1, 1])
r = 1 / (1 + math.exp(-2))
np.testing.assert_allclose(result["responsibility"], [[r, 1-r], [1-r, r]])
np.testing.assert_allclose(result["weights"], [0.5, 0.5])
assert result["loglik_after"] >= result["loglik_before"] - 1e-10
print("simple tests passed")
```

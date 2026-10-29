---
id: p3a-anthropic-mech-interp-take-home
section: anthropic
order: 632
level: S
title: Anthropic：机制可解释性：复现样本维度双下降
quick: >-
  我会固定线性模型的参数量和数据生成方式，扫描训练样本数相对参数量的比例，同时记录训练和测试误差。重点检查插值阈值附近的峰，用多个种子、奇异值谱和 ridge
  对照，判断峰是不是来自噪声被放大。
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · Anthropic · mech-interp-take-home
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/mech-interp-take-home
    type: secondary
---

## 题目描述

实现一个可重复的线性回归实验：改变训练样本量，记录训练与独立测试误差，并比较无正则与 ridge 回归。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `experiment(sample_sizes, features=20, noise=0.2, seeds=(0, 1, 2), ridge=0.0)`：对每个训练样本量，在每个 seed 上生成数据并拟合线性模型，返回一个列表，每项是 `{"n": ..., "train_mse": ..., "test_mse": ...}`，误差是多个 seed 的平均值。
- 数据生成：每个 seed 固定一组真实权重和一份 2000 条的独立测试集，真实权重各维独立服从标准正态后除以 `sqrt(features)`，特征各维独立服从标准正态；标签是 $y = x \cdot w^* + \varepsilon$，$\varepsilon$ 是标准差为 `noise` 的高斯噪声。
- 拟合：`ridge == 0` 时用最小范数最小二乘，`ridge > 0` 时采用使训练残差平方和加 `ridge * ||w||²` 最小的权重。
- `features` 和 `sample_sizes` 中每个样本量至少为 1，`noise` 和 `ridge` 非负，`seeds` 不能为空。`features` 不超过 100，样本数不超过 500。
- 交付的是可运行的实验和结果。小样本、少种子时不保证一定出现双下降，所以要和 `ridge > 0` 的结果对照。

### 输入输出示例

```text
experiment([15, 19, 20, 21, 40], features=20)
  n=15  train_mse≈0      test_mse≈0.45
  n=19  train_mse≈0      test_mse≈0.73
  n=20  train_mse≈0      test_mse≈5.13   # N = D，测试误差的峰
  n=21  train_mse≈0.001  test_mse≈2.44
  n=40  train_mse≈0.027  test_mse≈0.08

experiment([15, 19, 20, 21, 40], features=20, ridge=1)
  n=20  test_mse≈0.16    # ridge 把峰压平
```

以上数字是这份参考实现在默认三个 seed 下的输出。同一个 seed 内，各档样本量依次从同一个随机数生成器取数据，所以换种子或改动 `sample_sizes` 列表，具体数字都会变，但峰通常仍出现在 $N = D$ 附近。

## 解题思路与参考答案

## 题目

这是一道 take-home：用小模型做实验，复现 double descent（双下降）现象，解释它为什么出现，并提出缓解办法。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理；`realInterview` 只表示网站把它收录为面经题型。下面的接口、约束和测试是手册补的练习约定。

## 思路

我会先复现样本维度的双下降：固定线性模型的参数量 D，改变训练样本数 N，观察测试误差。这样变量少，也方便把插值阈值附近的变化和设计矩阵联系起来。

实验要先做到可复现：固定数据生成过程和随机种子，每个种子用同一组真实权重和一份独立的测试集。然后扫描 N/D 的比例，训练误差和测试误差分别画出来。

现象和原因：

- $N < D$ 时方程欠定，最小范数最小二乘解可以完全拟合训练集，训练误差为 0；
- $N \approx D$ 时，设计矩阵最小的奇异值接近 0，解要用很大的权重去拟合标签噪声，测试误差冲出一个峰；
- $N$ 继续变大，估计重新稳定，测试误差再次下降。

所以要专门检查插值阈值附近的病态程度（比如看设计矩阵的奇异值谱），以及噪声大小对峰高的影响。缓解办法是加 ridge 正则，或者调整模型容量，让它离开 $N = D$ 这个点。

单次曲线的形状可能只是随机波动，要用多个种子重复实验，看平均值和分布，再下结论。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `experiment(sample_sizes, features=20, noise=0.2, seeds=(0, 1, 2), ridge=0.0)`：对每个训练样本量，在每个 seed 上生成数据并拟合线性模型，返回一个列表，每项是 `{"n": ..., "train_mse": ..., "test_mse": ...}`，误差是多个 seed 的平均值。
- 数据生成：每个 seed 固定一组真实权重和一份 2000 条的独立测试集，标签是 $y = x \cdot w^* + \varepsilon$，$\varepsilon$ 是标准差为 `noise` 的高斯噪声。
- 拟合：`ridge == 0` 时用最小范数最小二乘，`ridge > 0` 时用 ridge 闭式解。
- `features`、`sample_sizes` 至少为 1，`noise` 和 `ridge` 非负，`seeds` 不能为空，否则抛 `ValueError`。`features` 不超过 100，样本数不超过 500。
- 交付的是可运行的实验和结果。小样本、少种子时不保证一定出现双下降，所以要和 `ridge > 0` 的结果对照。

### 输入输出示例

```text
experiment([15, 19, 20, 21, 40], features=20)
  n=15  train_mse≈0      test_mse≈0.45
  n=19  train_mse≈0      test_mse≈0.73
  n=20  train_mse≈0      test_mse≈5.13   # N = D，测试误差的峰
  n=21  train_mse≈0.001  test_mse≈2.44
  n=40  train_mse≈0.027  test_mse≈0.08

experiment([15, 19, 20, 21, 40], features=20, ridge=1)
  n=20  test_mse≈0.16    # ridge 把峰压平
```

以上数字是这份参考实现在默认三个 seed 下的输出。同一个 seed 内，各档样本量依次从同一个随机数生成器取数据，所以换种子或改动 `sample_sizes` 列表，具体数字都会变，但峰通常仍出现在 $N = D$ 附近。

### 解题思路与正确性

`np.linalg.lstsq` 在欠定时返回最小范数解，这正是双下降分析里假设的插值解。ridge 解 $(X^\top X + \lambda I)^{-1} X^\top y$ 在每个奇异值方向的分母上加了 $\lambda$，小奇异值方向不再被放大，所以插值阈值附近的峰会被压下去。

每个 seed 内部，测试集和真实权重对所有 N 都相同，不同 N 之间只有训练集不同，比较才公平。结果是固定种子下的确定值，重跑完全一致。

这只是合成线性设定下的观察，必须结合多个 seed 的分布和奇异值谱来解释，不能把一次曲线的形状当成理论证明。

### 完整参考实现（Python 3）

```python
import numpy as np

TEST_SIZE = 2000


def fit_linear(x, y, ridge):
    """ridge == 0 时用 lstsq 求最小范数最小二乘解；否则解 (XᵀX + λI) w = Xᵀy。"""
    if ridge == 0:
        return np.linalg.lstsq(x, y, rcond=None)[0]
    features = x.shape[1]
    return np.linalg.solve(x.T @ x + ridge * np.eye(features), x.T @ y)


def sample_data(rng, truth, n, noise):
    """生成 y = x · truth + 高斯噪声，x 形状 (n, D)。"""
    x = rng.normal(size=(n, len(truth)))
    y = x @ truth + rng.normal(scale=noise, size=n)
    return x, y


def experiment(sample_sizes, features=20, noise=0.2, seeds=(0, 1, 2), ridge=0.0):
    """对每个训练样本量，在多个 seed 上拟合线性模型，返回平均 train/test MSE。

    每个 seed 固定一组真实权重和一份独立的测试集。
    """
    if features < 1:
        raise ValueError("features must be >= 1")
    if noise < 0 or ridge < 0:
        raise ValueError("noise and ridge must be non-negative")
    if not seeds:
        raise ValueError("need at least one seed")
    if any(n < 1 for n in sample_sizes):
        raise ValueError("sample sizes must be >= 1")

    errors = {n: [] for n in sample_sizes}  # n -> [(train_mse, test_mse), ...]
    for seed in seeds:
        rng = np.random.default_rng(seed)
        truth = rng.normal(size=features) / np.sqrt(features)
        x_test, y_test = sample_data(rng, truth, TEST_SIZE, noise)
        for n in sample_sizes:
            x_train, y_train = sample_data(rng, truth, n, noise)
            weights = fit_linear(x_train, y_train, ridge)
            train_mse = np.mean((x_train @ weights - y_train) ** 2)
            test_mse = np.mean((x_test @ weights - y_test) ** 2)
            errors[n].append((train_mse, test_mse))

    rows = []
    for n in sample_sizes:
        train_mse, test_mse = np.mean(errors[n], axis=0)
        rows.append(
            {"n": n, "train_mse": float(train_mse), "test_mse": float(test_mse)}
        )
    return rows
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert first == second` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
# 同样的 seed 结果完全相同
first = experiment([3, 5, 10], features=5, seeds=(0, 1))
second = experiment([3, 5, 10], features=5, seeds=(0, 1))
assert first == second
assert len(first) == 3

# 所有误差有限且非负
assert all(np.isfinite(row["test_mse"]) for row in first)
assert all(row["train_mse"] >= 0 for row in first)

# n = 3 < D = 5：最小范数解能完全插值训练集
assert first[0]["train_mse"] < 1e-20

# ridge > 0 时也能正常运行
ridge_rows = experiment([3, 5], 5, seeds=(0,), ridge=1)
assert all(np.isfinite(row["test_mse"]) for row in ridge_rows)

# 这组固定 seed 下，n = D = 20 处测试误差出现峰值，ridge 能把峰压下去
plain = [row["test_mse"] for row in experiment([15, 20, 40], features=20)]
ridged = [row["test_mse"] for row in experiment([15, 20, 40], features=20, ridge=1)]
assert plain[1] > plain[0]
assert plain[1] > plain[2]
assert ridged[1] < plain[1]
```

### 复杂度与追问

设训练样本数为 N、特征数为 D、测试集大小为 $N_{test}$。每次 `lstsq` 约为 O($\min(ND^2, N^2D)$)，ridge 求解是 O($ND^2 + D^3$)，测试预测是 O($N_{test} \cdot D$)。总开销再乘以种子数和样本量档位数。

- 这个结果能解释大语言模型的 double descent 吗？不能直接解释。它只验证了合成线性设定下的现象；要研究更大的模型，还需要分别控制模型容量、正则强度和数据噪声，再看峰的位置和高度怎么变。
- 怎么证明峰来自标签噪声？把 `noise` 设成 0 重跑，$N \ge D$ 之后测试误差几乎为 0，峰完全消失；再画出每个 N 下设计矩阵的最小奇异值，可以看到它在 $N = D$ 附近最接近 0。

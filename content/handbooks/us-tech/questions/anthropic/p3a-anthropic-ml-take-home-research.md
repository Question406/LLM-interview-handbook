---
id: p3a-anthropic-ml-take-home-research
section: anthropic
order: 634
level: S
title: "Anthropic：ML Take-home：实验、代码与现场复盘"
quick: "我会先交付能稳定重跑的简单基线，再围绕明确假设做少量实验。数据切分、随机种子和资源开销都要记录，失败尝试也要保留，现场才能解释结果从哪里来。"
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
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · ml-take-home-research"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/ml-take-home-research
    type: secondary
---

## 题目描述

完成一个可复现的二分类训练与评估练习：使用给定数值特征训练带 L2 正则的逻辑回归，预测新样本并报告指标；另根据独立可信校准集筛选标注员，再汇总其投票。训练、校准和测试数据必须各司其职，不能用测试标签选择标注员或估计特征统计量。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `fit(x, y, steps=1000, lr=0.1, l2=0.01)`：`x` 是 $N \times D$ 的有限数值矩阵，`y` 是 0/1 标签。返回训练集的均值、标准差和权重 `(mean, std, weights)`。
- `predict(model, x)`：只能用 `fit` 返回的统计量做标准化，预测概率不低于 0.5 判为 1。
- `metrics(y_true, y_pred)`：返回 accuracy、precision、recall、F1，分母为 0 时记为 0。
- `select_annotators(votes, trusted, min_accuracy=0.7)`：`votes` 形状为 $N \times A$，只用一份独立的可信校准集，返回准确率不低于阈值的标注员下标。
- `vote(votes, selected)`：只用选中的标注员做多数票，生成训练标签，平票取 0；假定至少有一个可用标注员。
- 输入不含缺失值，类别特征要在上游编码好。测试集不能用来筛选标注员。$N \le 5000$，$D \le 100$。

- `mean`、`std` 形状为 `[D]`，按训练集总体标准差标准化，常数列的标准差记为 1；权重形状为 `[D+1]`，最后一项是偏置。训练从零权重开始，完成 `steps` 次全批量梯度下降，目标为平均二元交叉熵加 `l2/2 * sum(weights[:-1]^2)`，偏置不受正则。`lr` 为正，`steps` 为非负整数。
- `predict` 返回 `[M]` 的 0/1 整数数组；`metrics` 返回按 `accuracy`、`precision`、`recall`、`f1` 命名的字典。校准投票和可信标签均为 0/1，标注员下标从 0 开始，按升序返回。
### 示例

```text
model = fit([[-2], [-1], [1], [2]], [0, 0, 1, 1])
predict(model, [[-2], [-1], [1], [2]])                        -> [0, 0, 1, 1]
select_annotators([[0, 1], [0, 1], [1, 0], [1, 0]], [0, 0, 1, 1]) -> [0]
vote([[1, 0]], [0, 1])                                        -> [0]
```

## 解题思路与参考答案

## 题目

独立完成一个 ML 实验作为 take-home，之后在现场展示结果并回答追问。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

我会先把一个简单基线做成别人能重跑的实验，再逐个验证改进假设。比如要检验「加正则会减少过拟合」，就围绕这个假设安排对照，并记清数据切分、随机种子和计算资源。实验数量控制在能解释清楚的范围内。

交付物要让别人能直接重跑，并且把失败的尝试也写进去，现场复盘时这些往往是追问的重点。

允许用哪些工具、时长多少，要以当次任务说明为准，不能从历史面经推断。

## 完整编程练习（手册重构版）

这份练习把题目落到一个可以手写、可以测试的二分类基线上：NumPy 逻辑回归、评估指标，以及用可信校准集筛选标注员。

### 题面、接口与约束

- `fit(x, y, steps=1000, lr=0.1, l2=0.01)`：`x` 是 $N \times D$ 的有限数值矩阵，`y` 是 0/1 标签。返回训练集的均值、标准差和权重 `(mean, std, weights)`。
- `predict(model, x)`：只能用 `fit` 返回的统计量做标准化，预测概率不低于 0.5 判为 1。
- `metrics(y_true, y_pred)`：返回 accuracy、precision、recall、F1，分母为 0 时记为 0。
- `select_annotators(votes, trusted, min_accuracy=0.7)`：`votes` 形状为 $N \times A$，只用一份独立的可信校准集，返回准确率不低于阈值的标注员下标。
- `vote(votes, selected)`：只用选中的标注员做多数票，生成训练标签，平票取 0；没有可用标注员时抛 `ValueError`。
- 输入不含缺失值，类别特征要在上游编码好。测试集不能用来筛选标注员。$N \le 5000$，$D \le 100$。

### 输入输出示例

```text
model = fit([[-2], [-1], [1], [2]], [0, 0, 1, 1])
predict(model, [[-2], [-1], [1], [2]])                        -> [0, 0, 1, 1]
select_annotators([[0, 1], [0, 1], [1, 0], [1, 0]], [0, 0, 1, 1]) -> [0]
vote([[1, 0]], [0, 1])                                        -> [0]
```

第二个标注员在校准集上每一条都标反，所以被排除；最后一行一票 1、一票 0，平票取 0。

### 解题思路与正确性

`fit` 先用训练集的均值和标准差把特征标准化，标准差为 0 的常数列不缩放。然后拼一列 1 作为偏置，用全批量梯度下降最小化平均逻辑损失加 L2 正则。逻辑损失对权重的梯度是 $X^\top(\sigma(Xw) - y) / N$，L2 只加在非偏置的维度上。`predict` 复用训练时的统计量，测试数据的分布信息就不会漏进模型。

sigmoid 写成 `exp(-logaddexp(0, -z))`，数学上等于 $1 / (1 + e^{-z})$，但 $z$ 很大或很小时都不会溢出。

筛选标注员用的是独立的可信数据。如果拿待评估的模型自己的误差去判断哪些标签是错的，模型学偏的地方会被算成标注员的错，结论就成了循环论证。

这份参考用 NumPy 把训练过程写出来，方便看清梯度。scikit-learn 岗位可以换成 `Pipeline(StandardScaler(), LogisticRegression())`，切分和防泄漏的约定保持不变。

### 完整参考实现（Python 3）

```python
import numpy as np


def sigmoid(z):
    """数值稳定的 sigmoid：1 / (1 + e^{-z}) = exp(-log(1 + e^{-z}))，大 |z| 不会溢出。"""
    return np.exp(-np.logaddexp(0, -z))


def add_bias(features):
    """在 (N, D) 特征右侧拼一列 1，得到 (N, D + 1)，最后一维权重就是偏置。"""
    return np.column_stack([features, np.ones(len(features))])


def fit(x, y, steps=1000, lr=0.1, l2=0.01):
    """全批量梯度下降训练逻辑回归，返回 (mean, std, weights)。

    mean、std 只用训练集估计，predict 必须复用它们。
    """
    x = np.asarray(x, dtype=float)  # (N, D)
    y = np.asarray(y, dtype=float)  # (N,)
    if x.ndim != 2 or len(x) == 0:
        raise ValueError("x must be a non-empty 2-D array")
    if y.shape != (len(x),):
        raise ValueError("y must have shape (N,)")
    if not np.all(np.isin(y, [0, 1])):
        raise ValueError("y must contain only 0 and 1")
    if not np.all(np.isfinite(x)):
        raise ValueError("x must be finite")

    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std = np.where(std > 0, std, 1.0)  # 常数列不缩放，避免除以 0
    design = add_bias((x - mean) / std)  # (N, D + 1)
    weights = np.zeros(design.shape[1])

    for _ in range(steps):
        gradient = design.T @ (sigmoid(design @ weights) - y) / len(design)
        penalty = l2 * weights
        penalty[-1] = 0  # 偏置不加 L2
        weights -= lr * (gradient + penalty)
    return mean, std, weights


def predict(model, x):
    """用训练时的 mean/std 标准化，概率 >= 0.5 判为 1。"""
    mean, std, weights = model
    x = np.asarray(x, dtype=float)
    design = add_bias((x - mean) / std)
    return (sigmoid(design @ weights) >= 0.5).astype(int)


def safe_divide(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def metrics(y_true, y_pred):
    """返回 accuracy、precision、recall、F1；分母为 0 时记为 0。"""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if y_true.shape != y_pred.shape or len(y_true) == 0:
        raise ValueError("y_true and y_pred must be non-empty and the same shape")

    true_pos = int(((y_true == 1) & (y_pred == 1)).sum())
    false_pos = int(((y_true == 0) & (y_pred == 1)).sum())
    false_neg = int(((y_true == 1) & (y_pred == 0)).sum())
    precision = safe_divide(true_pos, true_pos + false_pos)
    recall = safe_divide(true_pos, true_pos + false_neg)
    return {
        "accuracy": float((y_true == y_pred).mean()),
        "precision": precision,
        "recall": recall,
        "f1": safe_divide(2 * precision * recall, precision + recall),
    }


def select_annotators(votes, trusted, min_accuracy=0.7):
    """votes 形状 (N, A)，trusted 形状 (N,)：返回在可信校准集上准确率达标的标注员下标。"""
    votes = np.asarray(votes)
    trusted = np.asarray(trusted)
    if votes.ndim != 2 or len(votes) != len(trusted) or len(votes) == 0:
        raise ValueError("calibration votes must be (N, A) and match trusted labels")
    accuracy = (votes == trusted[:, None]).mean(axis=0)  # (A,)
    return np.flatnonzero(accuracy >= min_accuracy)


def vote(votes, selected):
    """只用 selected 标注员做多数票；平票取 0。"""
    votes = np.asarray(votes)
    if len(selected) == 0:
        raise ValueError("no reliable annotators")
    return (votes[:, selected].mean(axis=1) > 0.5).astype(int)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.array_equal(predict(model, x), y)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")

# 一维可分数据：训练后全部预测正确
x = np.array([[-2.0], [-1.0], [1.0], [2.0]])
y = np.array([0, 0, 1, 1])
model = fit(x, y)
assert np.array_equal(predict(model, x), y)
assert metrics(y, predict(model, x))["f1"] == 1
mean, std, weights = model
assert np.allclose(mean, [0])
assert np.isfinite(weights).all()

# 标注员 0 全对，标注员 1 全部反标，应被排除
votes = np.column_stack([y, 1 - y])
selected = select_annotators(votes, trusted=y)
assert selected.tolist() == [0]
assert np.array_equal(vote(votes, selected), y)

# 平票取 0
assert vote([[1, 0]], [0, 1]).tolist() == [0]

# 没有预测正例时 precision 记为 0
assert metrics([0, 0], [0, 0])["precision"] == 0

# 常数特征不会除以 0
assert np.isfinite(fit(np.ones((4, 2)), y)[2]).all()

# 非法输入
expect_value_error(fit, x, [0, 1, 2, 1])
expect_value_error(vote, votes, [])
```

### 复杂度与追问

设样本数为 N、特征维度为 D、标注员数为 A。训练是 O(steps · ND) 时间、O(ND) 空间；预测是 O(ND)；筛选标注员是 O(NA)。

- 真实数据有类别变量和缺失值时，在训练集上拟合 one-hot 编码和缺失值填充，再原样应用到验证集和测试集。放进同一个 Pipeline 最不容易出错。
- 同一员工、同一用户有多条记录，或者数据有时间顺序时，要按实体或按时间切分，否则同一个实体会同时出现在训练集和测试集里，指标偏乐观。
- 类别不平衡时，报告 precision、recall 和 PR 曲线，并按业务代价调阈值，不要只看准确率。

这份练习只处理数值输入，不涵盖完整的业务分析，比如 HR 场景里离职原因的因果解释。

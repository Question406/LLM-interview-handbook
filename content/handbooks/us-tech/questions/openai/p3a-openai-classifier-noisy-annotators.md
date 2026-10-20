---
id: p3a-openai-classifier-noisy-annotators
section: openai
order: 605
level: S
title: "OpenAI：标注员噪声：找出低质量标注并验证改进"
quick: "训练数据来自多个标注员时，用一份独立的可信校准集评估每个标注员，排除准确率不达标的人，再在固定验证集上比较过滤前后的分类器指标。"
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · classifier-noisy-annotators"
    url: https://www.1point3acres.com/interview/problems/company/openai/classifier-noisy-annotators
    type: secondary
---

## 题目

训练数据来自多个标注员，其中一些人的标注质量很差。要找出这些低质量的标注员，并证明把他们的标签去掉之后，训练出来的分类器确实变好了。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

先固定一份独立的验证集，它不参与标注员筛选，也不参与训练。然后逐个看标注员：每人标了多少样本、标出来的类别分布、在不同类别或难度分层上的误差。一个标注员错得多，可能只是分到了更难的样本，所以要分层比较，避免把困难样本误判成坏标注。

判断标签质量需要一个不依赖被评估标签的参照，可以是人工复核过的可信集，也可以用交叉拟合：用其他折训练的模型去给这一折的标签打分。过滤之后，在相同的训练预算下比较过滤前后的指标，并给出置信区间，确认提升不是随机波动。

最容易犯的错是把验证标签和被筛选的训练标签混在一起，这样验证结果本身就被污染了。

动手前可以和面试官确认：有没有可信的复核集，每个样本有几个人标，以及「变好」用哪个指标衡量。

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

---
id: ml101-decision-stump-implementation
section: ensemble
order: 12
level: A
title: 实现决策树的一次最佳分裂，比较 Gini 与信息增益
quick: 对每个数值特征枚举相邻不同值之间的阈值，计算父节点不纯度减去左右子节点按样本数加权的不纯度，选择增益最大的合法分裂。先明确最小叶子样本数和平票规则；纯节点、常量特征或无正增益时保留为叶子。参考实现只构造一层分类树，不处理缺失、类别特征或样本权重。
tags: [ML Fundamentals, Trees, Coding]
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-23
sources:
  - title: scikit-learn Decision Trees, mathematical formulation
    url: https://scikit-learn.org/stable/modules/tree.html
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

训练一个只允许分裂一次的分类决策树，并用得到的模型预测新样本。支持 Gini 和以2为底的熵两种不纯度。

### 输入与接口

实现 `best_stump`(X,y,*,criterion="gini",`min_leaf`=1) 和 `stump_predict`(X,model)。训练 X 为 n×d 非空有限数值矩阵；y 为长度n的整数类别向量。criterion 为 gini 或 entropy；`min_leaf` 为正整数。预测 X 为 m×d 有限矩阵。

### 输出与约束

候选阈值取某特征相邻不同训练值的中点，左侧条件为值≤阈值；浮点中点不能区分两值时用较小值。候选分裂的两侧都至少 `min_leaf` 个样本。比较父节点不纯度减去按两侧样本数加权的不纯度。

`best_stump` 返回字典：叶子模型含 feature=None、label、gain=0、`n_features`；分裂模型含 feature、threshold、gain、`left_label`、`right_label`、`n_features`。没有超过1e-12的正增益时保留叶子。增益在1e-12内视为平票，优先特征编号小、阈值小者；叶子多数票平票选择较小标签。predict 返回长度m的整数标签数组。

### 示例

```text
X=[[0],[1],[2],[3]]，y=[0,0,1,1]
best_stump(X,y) -> {feature:0,threshold:1.5,gain:0.5,left_label:0,right_label:1,n_features:1}
stump_predict([[1],[2]],model) -> [0,1]
best_stump([[0],[1]],[3,3]) 的 feature -> None，label -> 3
```

## 解题思路与参考答案

一次分裂要比较的是左右子节点的加权不纯度。只把两个子节点的 Gini 或熵直接相加，会忽略它们的样本量差异。

设父节点有 n 个样本，某分裂得到 $n_L,n_R$ 个样本。不纯度为 I 时，增益是 $I(parent)-n_LI(left)/n-n_RI(right)/n$。分类比例为 $p_c$ 时，Gini 为 $1-\sum_c p_c^2$，熵为 $-\sum_{c:p_c>0}p_c\log_2p_c$；熵下降就是信息增益。

本题约定输入为有限数值矩阵与整数类别，1≤min_leaf；左侧使用 ≤ 阈值。增益在 1e−12 内视为平票，优先特征编号小、阈值小的分裂；叶子票数相同时选较小类别。没有正增益则不分裂。它是通用教学练习，没有公司真题归属。

```python
import numpy as np


def best_stump(X, y, *, criterion="gini", min_leaf=1):
    X, y = np.asarray(X, dtype=float), np.asarray(y)
    if X.ndim != 2 or min(X.shape) == 0 or not np.isfinite(X).all():
        raise ValueError("X must be a nonempty finite matrix")
    if y.shape != (len(X),) or not np.issubdtype(y.dtype, np.integer):
        raise ValueError("y must be an integer vector matching X")
    if criterion not in ("gini", "entropy") or type(min_leaf) is not int or min_leaf < 1:
        raise ValueError("invalid criterion or min_leaf")
    classes, encoded = np.unique(y, return_inverse=True)
    n, d = X.shape

    def impurity(labels):
        counts = np.bincount(labels, minlength=len(classes))
        p = counts[counts > 0] / len(labels)
        return 1 - np.sum(p ** 2) if criterion == "gini" else -np.sum(p * np.log2(p))

    def majority(labels):
        return int(classes[np.bincount(labels, minlength=len(classes)).argmax()])

    parent = impurity(encoded)
    best = {"feature": None, "label": majority(encoded), "gain": 0.0, "n_features": d}
    for feature in range(d):
        values = np.unique(X[:, feature])
        for low, high in zip(values[:-1], values[1:]):
            threshold = low / 2 + high / 2
            if not low <= threshold < high:
                threshold = low
            left = X[:, feature] <= threshold
            nl = int(left.sum())
            if nl < min_leaf or n - nl < min_leaf:
                continue
            gain = parent - (nl * impurity(encoded[left]) +
                             (n-nl) * impurity(encoded[~left])) / n
            if gain > best["gain"] + 1e-12:
                best = {"feature": feature, "threshold": float(threshold), "gain": float(gain),
                        "left_label": majority(encoded[left]),
                        "right_label": majority(encoded[~left]), "n_features": d}
    return best


def stump_predict(X, model):
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[1] != model["n_features"] or not np.isfinite(X).all():
        raise ValueError("prediction feature shape must match")
    if model["feature"] is None:
        return np.full(len(X), model["label"], dtype=int)
    left = X[:, model["feature"]] <= model["threshold"]
    return np.where(left, model["left_label"], model["right_label"])
```

取特征 [0,1,2,3]，类别 [0,0,1,1]。阈值 1.5 后两边都是纯节点，Gini 从 0.5 降到 0，增益为 0.5；若使用以 2 为底的熵，增益为 1 bit。这两个数的尺度不同，不能跨 criterion 直接比较大小来判断模型优劣。

重复值之间没有合法阈值；阈值只是用来确定训练样本分区。浮点中点若因舍入等于较大值，代码回退到较小值，保持相同分区。预测落在两个训练值之间的结果会依赖具体阈值约定。

每个特征最多 O(n) 个候选，参考代码每个候选重新扫描样本并计数，因此时间主要为 $O(Dn^2)$，再加排序成本；额外工作空间约为 $O(n+C)$，C 为类别数。优化时可以在排序后维护左右计数和不纯度统计，避免每个阈值都从头统计。

**为什么最优单层分裂不一定得到最优整棵树？**
当前增益只衡量这一层的目标，后续可用的分裂会受到它限制。贪心选择可能错过需要先做低增益分裂才能显现的关系，例如 XOR；本题无正增益就停，因此也不会自动发现这类结构。

**预测阶段还需要训练标签吗？**
不需要。单层模型保存特征、阈值和两侧输出标签即可；无分裂时保存一个叶子标签。若要输出概率，应额外保留各叶子的类别计数，并考虑叶子样本量与校准。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

[0,1] 为类 0、[2,3] 为类 1，最优阈值应为 1.5 且分类全对。再测纯标签数据退化为叶节点，避免产生没有收益的分裂。

```python
import numpy as np
X, y = [[0], [1], [2], [3]], [0, 0, 1, 1]
model = best_stump(X, y)
assert model["feature"] == 0 and model["threshold"] == 1.5
np.testing.assert_array_equal(stump_predict(X, model), y)
leaf = best_stump([[0], [1]], [3, 3])
assert leaf["feature"] is None
np.testing.assert_array_equal(stump_predict([[0], [1]], leaf), [3, 3])
print("simple tests passed")
```

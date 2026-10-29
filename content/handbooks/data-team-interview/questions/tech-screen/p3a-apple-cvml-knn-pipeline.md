---
id: p3a-apple-cvml-knn-pipeline
section: tech-screen
order: 72
level: A
title: Apple CVML 面经：手写 kNN end-to-end，standardization 在哪里 fit？
quick: >-
  只用 training set 拟合均值与标准差，再对查询应用同一变换，按距离稳定选邻居并投票。距离平票、投票平票和零方差都要提前定义；把
  validation set 一起拟合预处理会 leakage 分布，调 k 也只能用 development set。
companies:
  - apple
tags:
  - 一亩三分地继续检索
  - Apple
  - 一亩三分地
  - 真实面经
  - 完整编程练习
  - NumPy
  - AFM 专项 2026-10
  - 2026-10 论坛核对第二批
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: 2026-10-26T00:00:00.000Z
sources:
  - title: 水果cvml全套（2025-05-21）
    url: 'https://www.1point3acres.com/bbs/thread-1129820-1-1.html'
    type: interview
  - title: scikit-learn StandardScaler
    url: >-
      https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
    type: primary
---

## 题目描述

原帖说明 CVML 店面要求手写简单 kNN，且需要 end-to-end solution，但没有披露 standardization、平票或接口。以下均为手册补全的练习约定。建议限时 25 分钟。

### 输入与接口

实现 `standardized_knn(train_x, train_y, query_x, k)`。train_x 为 `[N,D]`、query_x 为 `[M,D]` 的有限 NumPy 浮点数组，N/D 为正，M 可以为 0；train_y 为 `[N]` 非负整数标签，1<=k<=N。输入数值在普通范围，不考虑浮点溢出。

### 输出与约束

仅在 train_x 上按每维拟合均值与总体标准差，即 ddof=0；标准差等于 0 时用 1 替代。对训练与查询应用同一 standardization，按平方欧氏距离选 k 个邻居。距离相同时选原训练下标较小的样本；多数投票平票时选标签数值较小者。返回 `[M]` 的整数 NumPy 数组，不修改输入，禁止调用现成分类器。不得用 query_x 拟合预处理。距离计算使用 float64。

### 示例

```text
train_x=[[0,0],[0,2],[10,0],[10,2]], train_y=[0,0,1,1]
query_x=[[1,1],[9,1]], k=1 -> [0,1]
```

### 来源核对范围

采集日期 2026-10-26，Chrome 直接读取主楼。发帖时间 2025-05-21 10:23:20，经历字段标 2024 年第四季度，页面时区未推断。此题用于练习数据处理与 ML coding，不能由一篇帖推断该题在 AFM 的出现概率。

## 解题思路与参考答案

先拟合训练预处理，再逐条查询计算距离，避免一次创建 `[M,N,D]` 巨大中间 tensor。稳定排序使相等距离保持原训练顺序；`np.unique` 返回排序标签，因此票数并列时 argmax 取到最小标签。

```python
import numpy as np


def standardized_knn(train_x, train_y, query_x, k):
    train = np.asarray(train_x, dtype=np.float64)
    query = np.asarray(query_x, dtype=np.float64)
    labels = np.asarray(train_y)
    mean = train.mean(axis=0)
    scale = train.std(axis=0, ddof=0)
    scale = np.where(scale == 0.0, 1.0, scale)
    train_scaled = (train - mean) / scale
    query_scaled = (query - mean) / scale
    predictions = []
    for row in query_scaled:
        distances = ((train_scaled - row) ** 2).sum(axis=1)
        neighbors = np.argsort(distances, kind="stable")[:k]
        values, counts = np.unique(labels[neighbors], return_counts=True)
        predictions.append(values[counts.argmax()])
    return np.asarray(predictions, dtype=labels.dtype)
```

时间为 $O(ND+MD+M(ND+N\log N))$，此实现每条查询做完整排序，便于实现严格平票约定。中间距离与差 matrix 按单条查询构造，但 standardization 后的训练/查询仍分别占 $O(ND)$ 和 $O(MD)$。更大数据可分块，或用 nearest neighbors 索引；高维时 nearest neighbors 质量与速度都要实际测量。

## 简单测试怎么写

将实现与以下测试保存为 `solution.py`，运行 `python3 solution.py`，需要 NumPy。先检查二维例子，再独立检查距离平票、投票平票、训练 standardization、零方差与空查询。

```python
train = np.array([[0.0, 0.0], [0.0, 2.0], [10.0, 0.0], [10.0, 2.0]])
labels = np.array([0, 0, 1, 1])
before = train.copy()
assert standardized_knn(
    train, labels, np.array([[1.0, 1.0], [9.0, 1.0]]), 1
).tolist() == [0, 1]
assert np.array_equal(train, before)
# 距离相同且k=1，优先下标0；k=2票数相同，选更小标签3。
tie_x, tie_y = np.array([[0.0], [2.0]]), np.array([8, 3])
assert standardized_knn(tie_x, tie_y, np.array([[1.0]]), 1).tolist() == [8]
assert standardized_knn(tie_x, tie_y, np.array([[1.0]]), 2).tolist() == [3]
# standardization 后第一维尺度约8.16，第二维约0.47，查询[8,0]最近是[0,0]。
scaled = standardized_knn(
    np.array([[0.0, 0.0], [10.0, 1.0], [20.0, 0.0]]),
    np.array([0, 1, 2]),
    np.array([[8.0, 0.0]]),
    1,
)
assert scaled.tolist() == [0]
# 同批其他query不能影响第一条预测，抓把query一起fit的泄漏。
with_outlier = standardized_knn(
    np.array([[0.0, 0.0], [10.0, 1.0], [20.0, 0.0]]),
    np.array([0, 1, 2]),
    np.array([[8.0, 0.0], [0.0, 1000000.0]]),
    1,
)
assert with_outlier[0] == scaled[0] == 0
constant = standardized_knn(
    np.array([[0.0, 5.0], [2.0, 5.0], [4.0, 5.0]]),
    np.array([2, 1, 1]),
    np.array([[0.0, 5.0]]),
    1,
)
assert constant.tolist() == [2]
empty = standardized_knn(train, labels, np.empty((0, 2)), 1)
assert empty.shape == (0,) and np.issubdtype(empty.dtype, np.integer)
```

## 面试追问

**为什么不用 test set 一起算标准差？** 会让训练方案利用测试分布，破坏独立评价。交叉验证时每个训练折也要单独 fit 预处理，不能先在全量数据 fit 再分折。

**standardization 一定更好吗？** 不保证。它隐含不同维度按方差 normalization 的度量假设。对已 normalization embedding、某些物理量或稀疏特征应重新判断；题中只要求实现指定规则。

**怎样构成真正的 end-to-end？** 面试代码外还应说明数据/标签检查、按实体或时间划分、只在 development set 选 k、最终测试和延迟/内存。不能在报告最终测试表现后继续调 k。

---
id: ml101-knn-implementation
section: classical-models
order: 11
level: A
title: 不调用机器学习库，怎样实现 KNN 分类并处理边界情况？
quick: 对查询计算它与各训练样本的平方欧氏距离，取最近 K 个后投票。先约定距离相同和票数相同的处理方式，再校验 K、特征维数与数值是否合法。完整排序的参考实现每次查询需要 O(nd + n log n) 时间；平方距离保持邻居顺序，可以省去开平方。
companies:
  - google
tags:
  - Machine Learning
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: Google L5 MLE 候选人面经：实现 KNN
    url: https://www.1point3acres.com/interview/thread/1116207
    type: secondary
  - title: scikit-learn Nearest Neighbors
    url: https://scikit-learn.org/stable/modules/neighbors.html
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

不调用机器学习库，实现一次 KNN 分类预测：依据查询点的最近 k 个训练样本，使用均匀投票决定类别。

### 输入与接口

实现 `knn_predict`(X,y,query,k)。X 是非空 n×d 有限实数列表，n、d 均至少1；y 为 n 个整数标签，query 有 d 个有限实数特征；k 为1到n的整数。输入数值的平方距离在浮点可表示范围内。

### 输出与约束

返回一个整数类别标签。距离为欧氏距离，每位邻居权重相同。函数不修改 X、y 或 query，不自行进行标准化。

距离相同的训练样本按原始输入顺序选入；票数相同时选择数值较小的类别。重复训练样本作为不同样本分别计票。训练数据与查询的缩放由调用者预先一致处理。

### 示例

```text
knn_predict([[0],[2],[3]],[0,1,1],[1.8],2) -> 1
knn_predict([[0],[2]],[1,0],[1],1) -> 1
knn_predict([[0],[2]],[1,0],[1],2) -> 0
```

## 解题思路与参考答案

先计算距离，再选邻居并投票。下面用完整排序实现，便于在面试时说明正确性和检查平票行为；数据大时可以再替换为堆或选择算法。

面经只披露要求实现 KNN，没有给接口和边界规则。下面是手册重构练习：X 为非空的 n×d 有限实数列表，d 至少为 1；y 为 n 个整数标签；query 有 d 个特征；K 为 1 到 n 的整数。使用均匀投票。距离相同时按训练输入顺序选邻居，票数相同时选较小的标签。调用者负责在训练集上拟合缩放，并对查询应用相同变换。

```python
from collections import Counter
from math import isfinite


def knn_predict(X, y, query, k):
    n = len(X)
    if n == 0 or len(y) != n:
        raise ValueError("X must be nonempty and match y")
    if type(k) is not int or not 1 <= k <= n:
        raise ValueError("k must be an integer in [1, n]")
    d = len(query)
    if d == 0 or any(len(row) != d for row in X):
        raise ValueError("feature dimensions must match and be positive")
    if any(type(label) is not int for label in y):
        raise ValueError("labels must be integers")
    if not all(isfinite(v) for row in X for v in row):
        raise ValueError("training features must be finite")
    if not all(isfinite(v) for v in query):
        raise ValueError("query features must be finite")

    distances = []
    for i, row in enumerate(X):
        try:
            distance = sum((a - b) ** 2 for a, b in zip(row, query))
        except OverflowError as error:
            raise ValueError("squared distance overflow; rescale features") from error
        if not isfinite(distance):
            raise ValueError("squared distance overflow; rescale features")
        distances.append((distance, i))
    distances.sort()
    votes = Counter(y[i] for _, i in distances[:k])
    return min(votes, key=lambda label: (-votes[label], label))
```

平方函数在非负距离上保持大小关系，所以选到的邻居与欧氏距离一致。排序键同时保存样本下标，让同距离邻居的顺序明确。投票只统计前 K 个，最后比较负票数和标签，落实练习约定。

例如 X 为 [[0], [2], [3]]，标签为 [0, 1, 1]，查询为 [1.8]，K=2。平方距离分别是 3.24、0.04、1.44，最近两个样本都属 1 类，输出 1。对 [[0], [2]]、标签 [1, 0] 和查询 [1]，K=1 时按输入顺序得到 1；K=2 时票数相同，得到标签 0。

计算全部距离耗时 $O(nd)$，排序耗时 $O(n\log n)$；额外保存距离、下标与投票结果需要 $O(n)$ 空间，训练数据自身为 $O(nd)$。代码采用列表保存全部距离，适合讲清算法，不能把复杂度说成堆版本的 $O(n\log K)$。

**怎样验证程序？**
检查 K=1、K=n、距离相同、投票相同、多维查询、重复样本、非法 K、维数不匹配和非有限数值。再用随机小数据，与按相同规则编写的逐邻居参考解核对；和库函数比较时避开未统一的平票规则。

**K 很小而 n 很大，如何改进？**
保留一个大小为 K 的最大堆，可以把选邻居的时间降到 $O(n\log K)$，仍要计算所有距离。树索引或近似近邻还能改变查询成本，但需要单独说明维度条件和近似误差。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

一维小数据方便手算距离。普通查询最近两点都属于类 1；距离平票时 K=1 按输入顺序，K=2 票数平票时取较小标签。最后检查非法 K。

```python
assert knn_predict([[0], [2], [3]], [0, 1, 1], [1.8], 2) == 1
assert knn_predict([[0], [2]], [1, 0], [1], 1) == 1
assert knn_predict([[0], [2]], [1, 0], [1], 2) == 0
try:
    knn_predict([[0]], [0], [1], 0)
except ValueError:
    pass
else:
    raise AssertionError("k=0 must fail")
print("simple tests passed")
```

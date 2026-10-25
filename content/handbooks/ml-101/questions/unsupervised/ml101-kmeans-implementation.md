---
id: ml101-kmeans-implementation
section: unsupervised
order: 10
level: A
title: 用 NumPy 实现 K-means，怎样处理初始化、空簇和停止条件？
quick: 先选 K 个初始中心，反复把样本分给最近中心，再把各中心更新为簇内均值。实现前要约定距离平票、空簇和停止规则；参考实现按中心位移停止，空簇保留原中心，结束后重新分配标签。多次初始化能比较不同局部解，空簇策略也不保证最终一定有 K 个非空簇。
companies: [google]
tags: [Machine Learning, Coding]
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: Google MLE 候选人面经：实现 K-means 与抄袭检测追问
    url: https://www.1point3acres.com/interview/thread/824942
    type: secondary
  - title: scikit-learn Clustering, K-means
    url: https://scikit-learn.org/stable/modules/clustering.html#k-means
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

仅用 NumPy 实现欧氏距离 K-means，返回最终中心、分配与每轮目标值，能够复现初始化和明确处理空簇。

### 输入与接口

实现 kmeans(X,k,*,init=None,seed=0,tol=1e-6,`max_iter`=100)。X为n×d非空有限矩阵，1≤k≤n；init若提供则为k×d有限初始中心；tol≥0，max_iter为正整数。合法数值保证平方距离不溢出。

### 输出与约束

返回字典 centers(k×d)、labels(n维整数，范围0到k-1)、inertia(到所属中心的平方距离总和)、history、`n_iter`。history 首项为初始中心下的 inertia，此后每次中心更新并重新分配后追加一项，因此长度为 `n_iter+1`。

未给init时，用 np.random.`default_rng`(seed).choice(n,k,replace=False) 选取样本行作为中心，原样保留选取顺序。距离平票选编号较小中心；非空簇新中心为成员均值，空簇保留旧中心。一次更新中最大中心欧氏位移≤tol时停止，最多更新max_iter次；返回labels必须对应最终centers。不修改X或init。

### 示例

```text
kmeans([[0],[2],[8],[10]],2,init=[[0],[10]])
centers -> [[1],[9]]
labels -> [0,0,1,1]
inertia -> 4
history -> [8,4,4]，n_iter -> 2
```

## 解题思路与参考答案

K-means 的实现就是交替执行最近中心分配和簇内均值更新。先确定每一步的规则，才能解释程序遇到空簇、重复点和迭代上限时会返回什么。

原帖只确认实现 K-means，并追问如何用于抄袭检测。下面是手册重构接口：X 为非空的 n×d 有限数值矩阵，d>0，1≤K≤n；计算平方欧氏距离。可以传初始中心，也可按固定种子随机选 K 个样本下标。同距离选编号小的中心；空簇保留旧中心；最大中心位移不超过 tol 时停止，也设置迭代上限。运算应处于 float64 可表示范围内。

```python
import numpy as np


def kmeans(X, k, *, init=None, seed=0, tol=1e-6, max_iter=100):
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or min(X.shape) == 0 or not np.isfinite(X).all():
        raise ValueError("X must be a nonempty finite matrix")
    n, d = X.shape
    if type(k) is not int or not 1 <= k <= n:
        raise ValueError("k must be an integer in [1, n]")
    if type(max_iter) is not int or max_iter < 1:
        raise ValueError("max_iter must be a positive integer")
    if not np.isfinite(tol) or tol < 0:
        raise ValueError("tol must be finite and nonnegative")
    if init is None:
        ids = np.random.default_rng(seed).choice(n, k, replace=False)
        centers = X[ids].copy()
    else:
        centers = np.asarray(init, dtype=float).copy()
        if centers.shape != (k, d) or not np.isfinite(centers).all():
            raise ValueError("init must have shape (k, d) and be finite")

    def assign(current):
        with np.errstate(over="raise", invalid="raise"):
            distances = ((X[:, None, :] - current[None, :, :]) ** 2).sum(axis=2)
        labels = distances.argmin(axis=1)
        return labels, float(distances[np.arange(n), labels].sum())

    labels, inertia = assign(centers)
    history = [inertia]
    for iteration in range(1, max_iter + 1):
        updated = centers.copy()
        for c in range(k):
            members = X[labels == c]
            if len(members):
                updated[c] = members.mean(axis=0)
        shift = np.linalg.norm(updated - centers, axis=1).max()
        centers = updated
        labels, inertia = assign(centers)
        history.append(inertia)
        if shift <= tol:
            break
    return {"centers": centers, "labels": labels, "inertia": inertia,
            "history": history, "n_iter": iteration}
```

取 X=[[0],[2],[8],[10]]，指定中心 [[0],[10]]。第一次分配得到左右各两个点，中心变为 1 和 9，平方距离和从 8 降到 4；下一轮中心不变，返回标签 [0,0,1,1]。`history` 记录每次重新分配后的目标，可以验证它在浮点误差范围内不增。

固定分组时，非空簇的均值最小化平方距离和；空簇没有样本项，保留旧中心不会增加该步目标。再按新中心重新分配，每个点的距离也不会增加。到达迭代上限时，返回标签与最终中心的最近关系仍一致，但中心未必已经是最终标签分组的均值，因此要区分“有返回值”和“已收敛”。

每轮距离计算主要耗时 $O(nKd)$。本实现为讲清向量化，临时构造 n×K×d 差值数组，需要 $O(nKd)$ 临时空间；大数据可分块计算距离，避免一次存下全部差值。中心和输出标签分别占 $O(Kd)$ 与 $O(n)$。

**随机抽了不同下标，为什么仍有空簇？**
不同下标可以对应相同坐标。重复初始中心会让平票样本都选前一个中心。若业务要求更多有效簇，可以重新初始化空中心，但也要检查数据本身是否只有少量不同位置。

**K-means 怎样用于抄袭检测？**
可以用文本表示聚类来产生候选，再对候选做更细的相似性或原文核验。两篇文章主题相同，也可能没有抄袭；同簇不足以直接判定。整句复用可以另检查词 N-gram 或句子片段，这些具体流程是练习方案，原帖未给唯一标准答案。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

四个一维点以 0 和 10 初始化，最终两簇中心应为 1 和 9，平方误差为 4。固定初始中心避免把随机初始化差异误认为实现错误。

```python
import numpy as np
result = kmeans([[0], [2], [8], [10]], 2, init=[[0], [10]])
np.testing.assert_allclose(result["centers"], [[1], [9]])
np.testing.assert_array_equal(result["labels"], [0, 0, 1, 1])
assert abs(result["inertia"] - 4) < 1e-10
assert np.all(np.diff(result["history"]) <= 1e-10)
print("simple tests passed")
```

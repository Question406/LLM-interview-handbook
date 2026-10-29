---
id: dt-p3a-kfold-indices
section: tech-screen
order: 82
level: A
title: Apple DS 原帖：手写 K-fold CV，余数与预处理 leakage 怎么处理？
quick: >-
  先生成一次可复现排列，把余数分给前几折；每个样本恰好一次进入 validation
  set，训练索引为该折的补集。执行模型比较时，每折重新拟合预处理与模型，不能在全数据上先 standardization 再交叉验证。
companies:
  - apple
tags:
  - 一亩三分地继续检索
  - Apple
  - 一亩三分地原帖核对
  - AFM 专项 2026-10
  - 一亩三分地追加第二批
  - 完整编程练习
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: 果子电面+昂赛，候选人原帖，Chrome核对2026-10-26
    url: 'https://www.1point3acres.com/bbs/thread-1158691-1-1.html'
    type: interview
  - title: scikit-learn KFold
    url: >-
      https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.KFold.html
    type: primary
  - title: 'scikit-learn Common pitfalls: data leakage'
    url: 'https://scikit-learn.org/stable/common_pitfalls.html'
    type: primary
---

## 题目描述

### 原帖核对与练习约定

- 来源：[果子电面+昂赛](https://www.1point3acres.com/bbs/thread-1158691-1-1.html)，Chrome 页面显示 2025-12-19 13:58:52；采集日期 2026-10-26。
- 主楼及作者回复实际可见，明确写到手写 K-fold CV。岗位为分析/数据科学类，不当作 AFM data team 已确认题目。
- 原帖未说明是写划分器还是包含整个训练循环，也未给参数、打乱方式和分层要求。以下为**手册接口约定**：先实现普通 K 折索引，训练循环与 leakage 问题在追问讨论。建议限时 20 分钟。

### 输入与接口

实现 `kfold_indices(n,k,shuffle=False,seed=0)`，n 为样本数且至少为 2，2<=k<=n。shuffle 为 bool；seed 为整数，仅在 shuffle=True 时使用独立 `random.Random(seed)` 打乱 `list(range(n))`。

### 输出与约束

返回长度为 k 的列表，每项 `(train_ids, valid_ids)` 为两个整数列表。各折 validation set 是排列中连续的、不重叠的区间：前 n%k 折大小为 n//k+1，其余为 n//k。train_ids 为该排列去掉当前验证区间后的拼接，顺序不另排序。所有样本恰好一次出现在 validation set，训练和验证无交集。不使用 sklearn 的划分器，不修改全局随机数状态。

### 示例

```text
n=5,k=3,shuffle=False
[([2,3,4],[0,1]), ([0,1,4],[2,3]), ([0,1,2,3],[4])]
```

## 解题思路与参考答案

先确定唯一的样本排列，再沿它累计切分位置。每折训练索引是验证片段的补集，返回大小自然是 n 减该折大小。尾部余数必须明确，否则有些实现会丢最后几个样本。

```python
import random


def kfold_indices(n, k, shuffle=False, seed=0):
    ids = list(range(n))
    if shuffle:
        random.Random(seed).shuffle(ids)
    folds = []
    start = 0
    for fold in range(k):
        size = n // k + int(fold < n % k)
        stop = start + size
        folds.append((ids[:start] + ids[stop:], ids[start:stop]))
        start = stop
    return folds
```

因为显式返回每折训练索引，输出和总构造时间为 $O(kn)$；内部排列为 $O(n)$。若只需顺序消费，可返回生成器降低同时保存全部训练索引的峰值空间，但总输出规模仍相同。

## 简单测试怎么写

实现和测试保存为 `solution.py`，运行 `python3 solution.py`，不需第三方库。先手算余数分配，再检查 validation set 覆盖、补集和固定 seed。

```python
expected = [([2, 3, 4], [0, 1]), ([0, 1, 4], [2, 3]), ([0, 1, 2, 3], [4])]
assert kfold_indices(5, 3) == expected
folds = kfold_indices(11, 4, True, 7)
assert folds == kfold_indices(11, 4, True, 7)
assert [len(valid) for _, valid in folds] == [3, 3, 3, 2]
assert sorted(i for _, valid in folds for i in valid) == list(range(11))
for train, valid in folds:
    assert not set(train) & set(valid)
    assert sorted(train + valid) == list(range(11))
assert kfold_indices(2, 2) == [([1], [0]), ([0], [1])]
state = random.getstate()
kfold_indices(8, 3, True, 9)
assert random.getstate() == state
```

## 面试追问

**能先在全数据上拟合 standardization 吗？** 不能。每折独立拟合 scaler、填补器、特征选择和模型，仅用训练折统计量变换验证折。即使变换不使用 y，也可能 leakage 验证分布。

**类别极不平衡怎么办？** 普通 K-fold 不保证每折都有两类。考虑分层划分，并在数据不足时调整折数；不能在本题偷偷加入分层导致违反明确接口。

**同用户、多轮对话或相邻视频帧呢？** 应先定义独立单位，按用户、会话或视频划分；时间预测问题还需尊重先后关系。行级随机切分会高估迁移表现。

**选超参后的交叉验证均值能当最终结果吗？** 反复选超参会对验证结果适配，需独立 test set 或嵌套交叉验证。还应给各折指标与样本量，不只报最好一折。

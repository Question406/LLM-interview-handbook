---
id: dt-cluster-bootstrap-code
section: tech-screen
order: 44
level: S
title: CoderPad：按任务家族做配对 bootstrap，如何避免模板多的家族支配结论？
quick: >-
  先计算同一任务上新旧模型的差，再在家族内取均值、对家族等权。bootstrap 时 resampling
  家族而非单行，以保持组内相关结构；这种指标评价的是家族平均收益，不是流量平均收益。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - AFM 加练第二批
  - 完整编程练习
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-27'
sources:
  - title: Python random
    url: 'https://docs.python.org/3/library/random.html'
    type: primary
  - title: Evaluating Large Language Models Trained on Code
    url: 'https://arxiv.org/abs/2107.03374'
    type: primary
---

## 题目描述

原创评测编程题；建议限时 25 分钟。evaluation set 中同一家族有不同数量的模板变体，你需要计算家族等权的新旧模型成功率差和 bootstrap 区间。

### 输入与接口

实现 `family_bootstrap(rows, repeats=1000, seed=0)`。rows 是非空列表，每项为 `(family: str, old: int, new: int)`，old/new 均为 0 或 1，代表同一任务的两次结果；repeats 为正整数。

### 输出与约束

家族按名字排序。先对每个家族的 `new-old` 求均值，point 为这些家族均值的等权平均。使用独立 `random.Random(seed)`；每轮有放回抽取 G 个家族均值再平均，重复 repeats 次。排序得到 draws，lo 和 hi 分别为下标 `int(0.025*(repeats-1))` 与 `int(0.975*(repeats-1))` 的元素，不插值。返回 `(point,lo,hi)`，均为 float，不修改输入。

### 可手算的完整返回示例

`family_bootstrap([('only',0,1),('only',1,1)],repeats=5,seed=0)` 返回 `(0.5,0.5,0.5)`。这里只有一个 family，其 pair differences 为 1 和 0，family mean 为 0.5；每次 resampling 仍只能得到这个 family。返回的是 improvement fraction，0.5 表示提高 50 个 percentage points，不是 0.5 个点。

### 示例

```text
rows=[('a',0,1),('a',1,1),('b',1,0)]
家族a差值平均0.5，家族b差值-1，point=-0.25。
若只有一个家族，bootstrap每轮均相同，lo=point=hi。
```

## 解题思路与参考答案

先配对做差，避免把新旧结果独立 resampling 破坏同一任务的对应关系。再以家族为 resampling 单位，让大量近似变体不被当成独立证据。

```python
import random


def family_bootstrap(rows, repeats=1000, seed=0):
    groups = {}
    for family, old, new in rows:
        groups.setdefault(family, []).append(new - old)
    effects = [sum(groups[g]) / len(groups[g]) for g in sorted(groups)]
    point = sum(effects) / len(effects)
    rng = random.Random(seed)
    draws = sorted(
        sum(rng.choice(effects) for _ in effects) / len(effects) for _ in range(repeats)
    )
    lo = draws[int(0.025 * (repeats - 1))]
    hi = draws[int(0.975 * (repeats - 1))]
    return float(point), float(lo), float(hi)
```

复杂度为 $O(N+RG+R\log R)$，R 为重复次数，G 为家族数。这里先固定每个家族的观测均值，再 bootstrap 家族；不包含家族内部样本量有限带来的额外不确定性。家族非常少时，区间覆盖不可靠，即使代码正确也不能过度解释。

## 简单测试怎么写

实现与测试放进 `solution.py`，运行 `python3 solution.py`。先手算 point estimate，再检查家族变体重复不改变家族等权目标，以及固定 seed 的复现。

```python
rows = [('a', 0, 1), ('a', 1, 1), ('b', 1, 0)]
result = family_bootstrap(rows, 1000, 7)
assert result[0] == -0.25
assert result[1:] == (-1.0, 0.5)
assert family_bootstrap(rows, 1000, 7) == result
assert family_bootstrap([('a', 0, 1)], 50, 2) == (1.0, 1.0, 1.0)
# 整个a家族观测重复一遍，家族均值仍为0.5。
assert family_bootstrap(rows + rows[:2], 1000, 7) == result
assert family_bootstrap([('a', 1, 1), ('b', 0, 0)], 5, 0) == (0.0, 0.0, 0.0)
assert rows == [('a', 0, 1), ('a', 1, 1), ('b', 1, 0)]
```

## 面试追问

**区间不跨零就能上线吗？** 不能。还要检查效应大小、风险 evaluation slices、多重比较和指标是否事先确定；训练团队反复挑选最好结果会增加乐观偏差。

**如何估计真实流量收益？** 需要有依据的任务或家族流量权重，并匹配相应 sampling 设计。本题固定等权，不能把其 point 称为流量加权收益。

**为什么不逐行 bootstrap？** 同一家族变体相关，逐行 resampling 通常夸大独立证据量。若家族之间也不独立，还需要更高层的 resampling 单位。

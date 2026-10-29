---
id: dt-token-budget-batch-code
section: tech-screen
order: 41
level: S
title: CoderPad：按 padding 后 token 预算组 batch，遇到超长样本怎么办？
quick: >-
  预算按 batch 内最大长度乘样本数计算，不能只累加真实长度。顺序扫描，加入下一条会超预算时先交付当前
  batch；单条超长样本单独记录为拒收，其他样本不丢失、不重排。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - AFM 加练第二批
  - 完整编程练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: PyTorch Dataset and DataLoader
    url: 'https://docs.pytorch.org/docs/2.14/data.html'
    type: primary
---

## 题目描述

原创练习；建议限时 20 分钟。你要为变长序列构造 batch，每个 batch 采用右侧 padding，显存预算用 padding 后 token 数近似。

### 输入与接口

实现 `budget_batches(lengths, max_tokens, max_examples)`。lengths 为正整数列表，可为空；另外两个参数为正整数。样本身份为其原始下标。

### 输出与约束

返回 `(batches, rejected)`。batches 为下标列表的列表，按原始顺序贪心组批；每批最多 max_examples 条，且 `max(lengths[i]) * len(batch) <= max_tokens`。若加入下一条合格样本会超任一预算，先提交当前批再开新批。长度本身大于 max_tokens 的样本只加入 rejected，不截断，不触发当前批提交。rejected 按输入顺序排列。最终非空尾批也要返回；输入不变。

### 示例

```text
lengths=[3,5,2,12,4], max_tokens=10, max_examples=3
batches=[[0,1],[2,4]], rejected=[3]
```

## 解题思路与参考答案

当前 batch 维护最大长度和样本数。候选成本必须重新用新最大长度计算；把长度相加会低估 padding。

```python
def budget_batches(lengths, max_tokens, max_examples):
    batches, rejected = [], []
    current, longest = [], 0
    for i, length in enumerate(lengths):
        if length > max_tokens:
            rejected.append(i)
            continue
        next_longest = max(longest, length)
        if current and (
            len(current) == max_examples
            or next_longest * (len(current) + 1) > max_tokens
        ):
            batches.append(current)
            current, longest = [], 0
        current.append(i)
        longest = max(longest, length)
    if current:
        batches.append(current)
    return batches, rejected
```

时间为 $O(N)$，输出之外只保存一个 batch。该启发式保留顺序，不能保证 throughput 最优；长度分桶可以减少 padding，但会改变混合顺序。

## 简单测试怎么写

保存实现与以下测试为 `solution.py`，运行 `python3 solution.py`，不需要第三方库。示例先手算 padding 成本，再检查超长拒收、条数上限、空输入及尾批。

```python
lengths = [3, 5, 2, 12, 4]
batches, rejected = budget_batches(lengths, 10, 3)
assert batches == [[0, 1], [2, 4]]
assert rejected == [3]
assert lengths == [3, 5, 2, 12, 4]
assert budget_batches([6, 5], 10, 9) == ([[0], [1]], [])
assert budget_batches([1, 1, 1], 100, 2) == ([[0, 1], [2]], [])
assert budget_batches([], 10, 3) == ([], [])
assert budget_batches([20, 30], 10, 3) == ([], [0, 1])
assert budget_batches([2, 99, 2], 4, 2) == ([[0, 2]], [1])
assert all(max(lengths[i] for i in b) * len(b) <= 10 for b in batches)
```

## 面试追问

**token 预算等于真实显存吗？** 不等于。attention、激活、图像 token、optimizer 状态和实现方式都会影响显存，应通过测量 calibration；本题只是近似成本模型。

**能直接在 DDP 中使用不同批数吗？** 不宜直接搬用。各进程必须协调训练步与集合通信；还要明确尾批、空批和有效 token 的全局 normalization。

**超长样本都丢弃会怎样？** 会改变长度与任务分布。记录拒收 token 和 capability slices，再考虑分段、长序列专用队列或另设预算，而不是悄悄丢弃。

---
id: dt-passk-estimator-code
section: tech-screen
order: 48
level: S
title: CoderPad：从 n 次生成估计 pass@k，为什么不能直接用成功率的幂？
quick: >-
  对同一任务的 n 个候选及 c 个成功，使用1减去抽 k
  个全部失败的组合比例，再对任务等权平均。它估计至少一个候选成功，不代表模型能识别并选中那个正确候选。
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
  - title: Evaluating Large Language Models Trained on Code
    url: 'https://arxiv.org/abs/2107.03374'
    type: primary
---

## 题目描述

原创评测实现题，参考代码生成评测中的 pass@k 估计；建议限时 20 分钟。

### 输入与接口

实现 `estimate_pass_k(counts, k)`。counts 为非空列表，每项 `(n,c)` 表示一个任务生成了 n 个候选、其中 c 个通过验证。n、k 为正整数，0<=c<=n，且每项 n>=k。允许各任务 n 不同。

### 输出与约束

单任务估计为 `1-C(n-c,k)/C(n,k)`，失败候选不足 k 个时该比例为 0。返回各任务估计的等权平均 Python float。不修改输入，不实际枚举候选组合，不使用先估计 c/n 再代入 `1-(1-c/n)**k` 的替代式。参考实现应避免创建巨大阶乘。

### 示例

```text
counts=[(4,2)], k=2 -> 5/6
counts=[(4,0),(4,4)], k=2 -> 0.5
```

## 解题思路与参考答案

k 个中至少一个成功是全部失败事件的补集。组合比例可改写为 k 项连乘，不需要阶乘。当失败总数小于 k 时直接返回 1。

```python
def estimate_pass_k(counts, k):
    total = 0.0
    for n, c in counts:
        if n - c < k:
            total += 1.0
            continue
        failure = 1.0
        for i in range(k):
            failure *= (n - c - i) / (n - i)
        total += 1.0 - failure
    return total / len(counts)
```

时间为 $O(Mk)$、额外空间为 $O(1)$，M 为任务数。对极大的 n、极小的成功概率，最后的 `1-failure` 可能有消减误差，可改用 log1p/expm1；本练习按常规评测规模使用。

## 简单测试怎么写

将实现与测试保存为 `solution.py`，运行 `python3 solution.py`。先用组合数手算 4 选 2 的六种情况，其中五种含成功候选，再测试两端和任务等权。

```python
import math

assert math.isclose(estimate_pass_k([(4, 2)], 2), 5 / 6)
assert estimate_pass_k([(4, 0), (4, 4)], 2) == 0.5
assert estimate_pass_k([(10, 0)], 3) == 0.0
assert estimate_pass_k([(10, 10)], 3) == 1.0
assert estimate_pass_k([(4, 2)], 4) == 1.0
assert math.isclose(estimate_pass_k([(10, 2)], 1), 0.2)
# 每题等权，不能因第二题生成得更多就把它权重放大。
assert estimate_pass_k([(2, 0), (100, 100)], 1) == 0.5
counts = [(4, 2)]
estimate_pass_k(counts, 2)
assert counts == [(4, 2)]
```

## 面试追问

**这个估计何时可解释为生成策略的 pass@k？** 候选应按所声明的固定 sampling 协议产生。针对验证结果自适应选择候选或共享搜索状态会改变统计解释，需要另报搜索预算和评测方式。

**pass@k 高能证明上线更好吗？** 不够。它假设知道某个候选成功，真实系统还要有可靠选择器；应同时报告首个答案质量、选择后质量与总成本。

**增加 k 后涨分是训练收益吗？** 不是独立的训练证据。新旧模型应匹配 sampling、推理 token 和执行预算，避免把测试时计算增加当作数据干预收益。

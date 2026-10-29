---
id: tml-batch-invariant-rmsnorm-reference
section: thinking-machines
order: 900
level: A
title: "Thinking Machines 机制练习：Batch-invariant RMSNorm"
quick: "我会先区分重复跑同一个 batch 与改变 batch 后保持同一行结果。后者要求 reduction 组织不受其他请求影响，固定 seed 本身无法保证。"
companies:
  - thinking-machines
tags:
  - "Frontier Coding 2026-10-28"
  - 完整编程练习
  - "公开机制练习"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "Thinking Machines Lab：Defeating Nondeterminism in LLM Inference"
    url: "https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/"
    type: primary
---

## 题目描述

来源类别：官方研究文章衍生的编程练习。参考 Horace He 等人的 Defeating Nondeterminism in LLM Inference，练习逐行固定 reduction order 与 batch invariance。

### 输入、接口与规则

实现 `fixed_order_rmsnorm(x,weight,eps=1e-6)`。x 为 `[B,D]` floating array，B 可为 0，D 为 1..100000；weight 为 `[D]`。输入 finite，x 与 weight 的绝对值不超过 1e6，eps finite 且在 `[1e-12,1]`。返回 float64 `[B,D]`，不修改输入。

每行输出为该行 x 除以 `sqrt(mean(x*x)+eps)`，再逐元素乘 weight。每行平方和必须以 feature index 从小到大的固定顺序、float64 累加；不能依赖该行处于哪个 batch position。允许 Python reference loops，本题关注可验证语义。

测试同一行单独计算、置换 batch 顺序、加入其他行后，输出是否逐位相同。还需用两个不同浮点加法顺序展示 non-associativity。实现仅为 CPU reference；性能 kernel 的 tiling 与硬件验证另行讨论。

### 输入输出示例

```text
x=[[3,4],[0,0]], weight=[1,2], eps=1e-6。
第一行返回 [3,8]/sqrt(12.5+eps)，第二行返回 [0,0]。
拆成两个单行 batch 后，拼回输出应与原 batch 完全相等。
```

## 回答思路

> **输入与任务：** 固定输入 row，改变 batch composition，检查同一行的结果。  
> **做法与原因：** Reduction 顺序只由 feature index 决定，再逐行进行 RMSNorm。  
> **正确性检查：** 除数值容差参考外，单独测试 bitwise equality 与浮点加法顺序。

## 解题思路与参考答案

我会先区分重复跑同一个 batch 与改变 batch 后保持同一行结果。后者要求 reduction 组织不受其他请求影响，固定 seed 本身无法保证。

这份 reference 对每行按固定 feature 顺序累加，用来建立清楚的正确性基准。它不声称 Python loops 是高性能 inference kernel；后续优化仍要用相同的 batch-composition 测试验证。

### 完整参考实现

```python
import numpy as np


def fixed_order_rmsnorm(x, weight, eps=1e-6):
    values = np.asarray(x, dtype=np.float64)
    scale = np.asarray(weight, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] == 0 or scale.shape != values.shape[1:]:
        raise ValueError("expected x[B,D], weight[D], D > 0")
    if (
        not np.isfinite(values).all()
        or not np.isfinite(scale).all()
        or not np.isfinite(eps)
        or eps <= 0
    ):
        raise ValueError("finite inputs and positive epsilon required")
    output = np.empty_like(values)
    for row in range(values.shape[0]):
        squares = np.float64(0)
        for feature in range(values.shape[1]):
            squares = squares + values[row, feature] * values[row, feature]
        inverse = 1 / np.sqrt(squares / values.shape[1] + eps)
        output[row] = values[row] * inverse * scale
    return output
```

## 简单测试怎么写

将实现与下面测试按顺序保存为 `solution.py`，使用安装 NumPy/PyTorch 的 Python 运行 `python solution.py`。先核对题面的手算输出，再执行下列 assertions。

```python
x = np.array([[3.0, 4.0], [0.0, 0.0]])
w = np.array([1.0, 2.0])
expected = x / np.sqrt(np.mean(x * x, axis=1, keepdims=True) + 1e-6) * w
np.testing.assert_allclose(fixed_order_rmsnorm(x, w), expected, atol=1e-14)
rng = np.random.default_rng(15)
x, w = rng.normal(size=(9, 33)), rng.normal(size=33)
whole = fixed_order_rmsnorm(x, w)
for row in range(len(x)):
    assert np.array_equal(whole[row], fixed_order_rmsnorm(x[row : row + 1], w)[0])
permutation = rng.permutation(len(x))
assert np.array_equal(whole[permutation], fixed_order_rmsnorm(x[permutation], w))
extra = np.concatenate([np.full((1, 33), 1e4), x, np.full((1, 33), -1e4)])
assert np.array_equal(whole, fixed_order_rmsnorm(extra, w)[1:-1])
assert fixed_order_rmsnorm(np.empty((0, 33)), w).shape == (0, 33)
a, b, c = np.float32(1e8), np.float32(-1e8), np.float32(1.0)
assert np.float32(np.float32(a + b) + c) == 1
assert np.float32(a + np.float32(b + c)) == 0
print("Thinking Machines mechanism: batch-invariant RMSNorm passed")
```

## 复杂度与追问

时间 `O(BD)`，输出空间 `O(BD)`；本题不测 GPU 性能。独立 kernel 的 batch invariance 也不能单独证明整个 LLM serving pipeline 已满足相同保证。

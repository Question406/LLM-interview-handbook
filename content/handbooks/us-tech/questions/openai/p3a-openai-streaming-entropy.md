---
id: p3a-openai-streaming-entropy
section: openai
order: 617
level: S
title: "OpenAI：流式熵：logits 在线累积与数值稳定"
quick: "流式计算 softmax 熵时只维护最大 logit、相对最大值的指数和、以及按指数加权的 logit 偏移和，遇到更大的最大值时把后两项一起重新标定，熵等于 log 配分函数减去 logit 的期望。"
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
  - title: "1Point3Acres · OpenAI · streaming-entropy"
    url: https://www.1point3acres.com/interview/problems/company/openai/streaming-entropy
    type: secondary
---

## 题目

给一组 logits，先计算 softmax 分布的熵；再改成流式版本，logits 逐个到达，不能保存全部历史；最后支持把两个分块的结果合并。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

softmax 的熵可以写成 log 配分函数减去 logit 在这个分布下的期望：

$$H = \log Z - \mathbb{E}_p[x], \quad Z = \sum_i e^{x_i}$$

直接算 $e^{1000}$ 会溢出，所以所有量都相对当前最大 logit $m$ 来存。流式状态只需要三个数：

- $m$：目前见过的最大 logit；
- $z = \sum_i e^{x_i - m}$；
- $r = \sum_i e^{x_i - m}(x_i - m)$。

代入后熵等于 $\log z - r / z$，$m$ 在式子里正好消掉。

难点在最大值变化的时候。新来一个更大的 logit，最大值从 $m$ 变成 $m'$，每一项的权重都要乘 $e^{m - m'}$，同时每一项里的偏移 $x_i - m$ 也变成了 $x_i - m'$，多出一个 $m - m'$。所以 $r$ 的更新是 $r' = e^{m - m'}\,(r + z\,(m - m'))$。只缩放 $r$、漏掉 $z\,(m - m')$ 这一项，是这道题最常见的错误。

分块合并是同一个操作：把两边都换算到共同的最大值上，再把 $z$ 和 $r$ 分别相加。单个 logit 本身就是一个 $(m, z, r) = (x, 1, 0)$ 的小分块，所以 `add` 可以直接复用合并逻辑。

验证时用整批的 logsumexp 结果做对照，覆盖极大的 logits、只有一个元素、以及不同的分块方式。

相关题：[[openai-entropy-l1]]（手册里已有的同类题；本条来源用于补充对照，两份题面契约不一致时分别标注，不混在一起）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Entropy()`：空的流式状态。
- `add(logit)`：加入一个有限的 logit，返回自身，方便链式调用；非有限值抛 `ValueError`。
- `merge(other)`：把另一个 `Entropy` 的状态合并进来，返回自身。
- `value()`：返回当前 softmax 分布的自然对数熵；空流抛 `ValueError`。只有一个 logit 时熵为 0。
- 不保存全部 logits，空间 O(1)。浮点误差允许到 $10^{-10}$。

### 输入输出示例

```text
Entropy().add(1000).add(1000).value()  -> log(2) ≈ 0.6931
Entropy().add(5).value()               -> 0.0
```

把 `[1000, 999, -1000, 1001]` 逐个加入，或者拆成两块分别累积再合并，结果都应该和整批计算一致。

### 解题思路与正确性

状态始终满足不变量：$z$ 和 $r$ 都是相对于当前 $m$ 的和。合并时先取 $m' = \max(m_1, m_2)$，用上面的公式把两边的 $r$ 和 $z$ 换算到 $m'$，再相加，不变量对合并后的集合依然成立。所以无论逐项加入还是任意分块合并，最后得到的 $(m, z, r)$ 在数学上相同，熵也相同。

因为所有指数都是 $x - m \le 0$，不会溢出；只会有很小的项下溢成 0，它们对熵的贡献本来就可以忽略。用相对量还避免了两个约 1000 的大数相减带来的精度损失。

### 完整参考实现（Python 3）

```python
import math


class Entropy:
    """流式计算 softmax(logits) 的自然对数熵，只保存三个数，支持分块合并。

    设 m = max(x)，z = Σ exp(x - m)，r = Σ exp(x - m) · (x - m)，
    则熵 H = log z - r / z。
    """

    def __init__(self):
        self.max_logit = -math.inf
        self.z = 0.0
        self.r = 0.0

    def _absorb(self, max_logit, z, r):
        """把另一份 (m, z, r) 合并进来；两边先换算到共同的最大值上。"""
        if z == 0:
            return self
        if self.z == 0:
            self.max_logit, self.z, self.r = max_logit, z, r
            return self
        new_max = max(self.max_logit, max_logit)
        own_r = self._rescaled_r(self.max_logit, self.z, self.r, new_max)
        incoming_r = self._rescaled_r(max_logit, z, r, new_max)
        self.r = own_r + incoming_r
        self.z = self.z * math.exp(self.max_logit - new_max) + z * math.exp(max_logit - new_max)
        self.max_logit = new_max
        return self

    @staticmethod
    def _rescaled_r(old_max, z, r, new_max):
        # 每项权重乘 scale，同时 (x - old_max) 变成 (x - new_max)，多出 (old_max - new_max)。
        # 只缩放 r 而漏掉 z · (old_max - new_max) 这一项，结果会错。
        scale = math.exp(old_max - new_max)
        return scale * (r + z * (old_max - new_max))

    def add(self, logit):
        if not math.isfinite(logit):
            raise ValueError(f"logit must be finite: {logit!r}")
        # 单个 logit 的状态：m = x，z = 1，r = 0
        return self._absorb(logit, 1.0, 0.0)

    def merge(self, other):
        return self._absorb(other.max_logit, other.z, other.r)

    def value(self):
        if self.z == 0:
            raise ValueError("entropy of an empty stream is undefined")
        return math.log(self.z) - self.r / self.z
```

### 可执行测试

```python
import numpy as np

def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")

def reference_entropy(logits):
    probs = np.exp(np.array(logits) - max(logits))
    probs /= probs.sum()
    return -sum(p * math.log(p) for p in probs if p > 0)

logits = [1000.0, 999.0, -1000.0, 1001.0]
expected = reference_entropy(logits)

# 逐项累积，与整批计算一致（logit 很大也不溢出）
whole = Entropy()
for logit in logits:
    whole.add(logit)
assert np.isclose(whole.value(), expected)

# 拆成两块再合并，结果相同
left = Entropy()
right = Entropy()
for logit in logits[:2]:
    left.add(logit)
for logit in logits[2:]:
    right.add(logit)
assert np.isclose(left.merge(right).value(), expected)

# 两个相同 logit 的熵是 log 2；单个 logit 的熵是 0
assert np.isclose(Entropy().add(1000).add(1000).value(), math.log(2))
assert Entropy().add(5).value() == 0

# 和空流合并不改变结果
assert np.isclose(Entropy().merge(whole).value(), expected)

# 空流和非有限 logit
expect_value_error(Entropy().value)
expect_value_error(Entropy().add, math.inf)
```

### 复杂度与追问

每次 `add` 和 `merge` 都是 O(1) 时间，状态空间 O(1)。

- 不同的合并顺序结果一样吗？数学上一样，浮点运算的末几位可能不同，所以测试用 `isclose` 比较。
- 空流为什么报错？没有任何 logit 时不构成概率分布，熵没有定义，返回 0 会掩盖调用方的错误。

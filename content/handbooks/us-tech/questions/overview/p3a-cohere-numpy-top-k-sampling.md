---
id: p3a-cohere-numpy-top-k-sampling
section: overview
order: 803
level: A
title: "Cohere：NumPy Top-K Sampling 与 Top-P 追问"
quick: "先选出最大的 k 个 logits 作为候选，在候选上减最大值做 softmax，再用传入的 rng 采样并返回原 token id；k = 1 就是 greedy，top-p 则按累计概率决定候选个数。"
companies:
  - cohere
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - cohere
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Cohere：NumPy Top-K Sampling 与 Top-P 追问"
    url: https://www.1point3acres.com/interview/problems/7a3c568d-c54a-53a3-bd89-85dca674313d
    type: secondary
---

## 题目

用 NumPy 实现 top-k 采样：给一组 logits，只在最大的 k 个里按 softmax 概率随机选一个 token。要检查 k 的取值范围，并能解释它和 greedy 解码、top-p 采样的关系。

> 来源：一亩三分地题目详情页（2026-10-18 读取），题面是网站从面经整理的，没有逐条核对原帖；网站收录不等于公司官方确认。另一条同类目录来源 [Implement top-k sampling using NumPy](https://www.1point3acres.com/interview/problems/40f31787-1af2-4520-ad46-1bac12bd39ae) 本次只读了标题，暂时合并为同一题的线索。下面的接口、约束和测试是手册补的练习约定。

## 思路

分三步：先选出 logit 最大的 k 个 token 作为候选；再只在候选上做 softmax；最后用调用方传入的 `rng` 按概率采样，并把结果映射回原词表的 token id。

几个容易错的细节：

- 必须先截断再归一化。如果先对整个词表做 softmax 再把非候选置零，还要重新归一化，否则概率之和不是 1。
- 做 softmax 前减去候选里的最大值。这不改变概率比例，但能避免 logit 很大时 `exp` 溢出。
- 返回的是原词表里的 token id，不是候选数组里的位置。
- 随机数生成器由外部传入，测试才能固定种子、结果可复现。

k = 1 时只剩一个候选，就退化成 greedy 解码。固定的 k 不能适应分布的形状：分布很尖锐时，k 个候选里大多是概率极低的 token；分布很平时，k 又可能太小。top-p 改为按累计概率选集合：把 token 按概率降序排，取累计概率刚好达到 p 的最短前缀，所以候选个数随分布自动变化。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `sample(logits, k, rng) -> int`：`logits` 是一维有限数组，`k` 是 $[1, V]$ 内的整数，`rng` 是 NumPy `Generator`。只保留最大的 k 个 logits，logit 相同时 token id 小的优先进入候选。返回采到的原词表 token id。
- 输入不是一维、含 `inf`/`nan`、或 k 越界时抛 `ValueError`。
- 词表大小 $V \le 10^5$。

### 输入输出示例

```text
sample([1, 2, 3, 4], k=1, rng) -> 3          # 永远是最大的那个
sample([1, 2, 3, 4], k=2, rng) -> 2 或 3
sample([0, 0, 0],    k=1, rng) -> 0          # 并列时取 id 小的
```

### 解题思路与正确性

候选是先确定的，归一化只在候选上做，所以被截掉的 token 概率严格为 0，不会因为浮点误差被采到。减去最大值后，每个候选的概率仍然正比于 $e^{x_i}$，分布不变。

为了让并列规则确定，参考实现用 `np.lexsort` 做了全排序。用 `np.argpartition` 可以把选候选降到平均 O(V)，但它不保证第 k 名附近的并列元素按 id 取舍，需要额外处理恰好落在边界上的并列值。

### 完整参考实现（Python 3）

```python
import numpy as np


def sample(logits, k, rng):
    """只在最大的 k 个 logits 里按 softmax 概率采样，返回原词表里的 token id。"""
    logits = np.asarray(logits, dtype=float)  # [V]
    if logits.ndim != 1:
        raise ValueError(f"logits must be 1-D, got shape {logits.shape}")
    if not np.all(np.isfinite(logits)):
        raise ValueError("logits must be finite")
    if type(k) is not int or not 1 <= k <= len(logits):
        raise ValueError(f"k must be an int in [1, {len(logits)}], got {k!r}")

    # lexsort 以最后一个键为主键：先按 logit 降序，并列时按 token id 升序
    order = np.lexsort((np.arange(len(logits)), -logits))
    candidates = order[:k]  # [k]，原词表 id

    # 稳定 softmax：减去候选里的最大值不改变概率比，只防止 exp 溢出
    shifted = logits[candidates] - logits[candidates].max()
    probs = np.exp(shifted)
    probs /= probs.sum()
    return int(rng.choice(candidates, p=probs))
```

### 可执行测试

```python
def expect_value_error(*args):
    try:
        sample(*args)
    except ValueError:
        return
    raise AssertionError(f"sample{args[:2]} should raise ValueError")

rng = np.random.default_rng(1)

# k = 1 退化成 greedy
assert sample([1, 2, 3, 4], 1, rng) == 3

# 被截掉的 token 永远采不到
assert {sample([1, 2, 3, 4], 2, rng) for _ in range(1000)} == {2, 3}

# 并列时按 token id 升序进入候选
assert sample([0, 0, 0], 1, rng) == 0

# 极端 logits 不溢出
assert sample([1000.0, -1000.0, 999.0], 2, rng) in {0, 2}

# 等概率候选的经验频率接近 0.5
rng = np.random.default_rng(2)
draws = [sample([0, 0], 2, rng) for _ in range(10000)]
assert abs(sum(draws) / len(draws) - 0.5) < 0.03

# 同一个种子结果可复现
first = [sample([1, 2, 3], 3, np.random.default_rng(7)) for _ in range(5)]
second = [sample([1, 2, 3], 3, np.random.default_rng(7)) for _ in range(5)]
assert first == second

# 非法输入
expect_value_error([1, 2], 0, rng)
expect_value_error([1, 2], 3, rng)
expect_value_error([1, float("inf")], 1, rng)
expect_value_error([[1, 2]], 1, rng)
```

### 复杂度与追问

设词表大小为 V。参考实现的全排序是 O(V log V) 时间、O(V) 空间；候选上的 softmax 和采样是 O(k)。

- 换成 top-p 怎么写？对全部 logits 做稳定 softmax，按概率降序排序后求累计和，保留累计和第一次达到 p 之前（含这一项）的 token，再在这些 token 上重新归一化后采样。它和 top-k 的区别是候选个数随分布变化，并不是把 k 换成一个固定的概率阈值逐项过滤。
- 加上 temperature 怎么办？在选候选之前把 logits 除以温度 T。T 不改变排序，所以不影响 top-k 选哪些 token，只改变候选之间的概率差距。
- 批量采样时，可以对 `[B, V]` 的 logits 沿最后一维做同样的操作，用 `rng.random(B)` 和累计概率做逆变换采样，避免 Python 循环。

## 相关题

- [[coding-topk-nucleus]]：PyTorch 版本，温度、top-k、top-p 一起写，$T=0$ 和 $p=0$ 的边界都要覆盖。
- [[apple-topk-sample]]：同一套温度、top-k、nucleus 实现，追问端侧为什么偏爱候选数固定的 top-k。
- [[coding-gumbel-max]]：另一种在候选上抽样的写法，不用累计概率做逆变换。

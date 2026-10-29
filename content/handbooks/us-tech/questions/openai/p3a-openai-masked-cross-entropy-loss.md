---
id: p3a-openai-masked-cross-entropy-loss
section: openai
order: 621
level: S
title: OpenAI：NumPy cross entropy：mask、label smoothing 与 KL
quick: >-
  先用 logsumexp 得到 log-softmax，与平滑后的 one-hot 目标计算 cross entropy，再按有效行数平均。梯度是
  softmax 减目标，乘 mask 后用同一分母归约；全部被 mask 时返回 0 和零梯度。
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
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · OpenAI · masked-cross-entropy-loss
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/masked-cross-entropy-loss
    type: secondary
---

## 题目描述

用 NumPy 实现带有效行 mask 和 label smoothing 的多分类 cross entropy，同时返回 loss 对 logits 的解析梯度。

以下为手册重构练习约定。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `cross_entropy(logits, labels, mask=None, smoothing=0) -> (loss, dlogits)`：`logits` 形状 `[N, C]`，`labels` 是形状 `[N]` 的整数，`mask` 是形状 `[N]` 的 bool，`None` 表示全部有效。
- 目标分布是 $(1 - \varepsilon) \cdot \text{onehot}(y) + \varepsilon / C$，loss 是有效行上每行 cross entropy 的平均；`dlogits` 与 `logits` 同形状，无效行的梯度为 0。
- 没有有效行时返回 `loss = 0.0` 和全零梯度。
- 要求 $C \ge 2$、$0 \le \varepsilon < 1$、标签在 $[0, C)$ 内。logits 都是有限值，$N \le 1000$，$C \le 10000$。

### 输入输出示例

```text
cross_entropy([[0, 0]], [1])  -> loss = log(2) ≈ 0.6931, dlogits = [[0.5, -0.5]]
```

两个类别 logits 相同，softmax 是 `[0.5, 0.5]`，目标是 `[0, 1]`，梯度就是两者之差。

## 解题思路与参考答案

cross entropy 和梯度一起从 log-softmax 算，最后都按有效行数平均。先用 logsumexp 算 log-softmax，每行减最大值再取 exp，避免溢出。然后取目标类别的负 log 概率作为每行的 loss，最后按有效行数（有效 token 数）求平均，而不是按总行数。

## 题目

用 NumPy 实现分类 cross entropy loss，并返回对 logits 的梯度。之后扩展两项：只在有效位置上计算的 mask，以及 label smoothing。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 在 Chrome 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

label smoothing 改变的是目标分布：正确类别拿 $1 - \varepsilon$，再把 $\varepsilon$ 均匀分给所有类别。这里要和面试官确认，均匀那份是分给全部 C 个类别（正确类别也分到一份），还是只分给其余 C - 1 个类别。两种写法的 loss 数值不同。

全部位置都被 mask 掉时，有效行数是 0，直接除会得到 NaN。要提前约定这时的返回值，这份练习规定返回 loss 为 0、梯度全零。

自查时用小例子对照手算（两类等概率时 loss 是 $\log 2$），再用数值梯度检查解析梯度，并试一组极大的 logits，确认不出现 inf 或 NaN。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `cross_entropy(logits, labels, mask=None, smoothing=0) -> (loss, dlogits)`：`logits` 形状 `[N, C]`，`labels` 是形状 `[N]` 的整数，`mask` 是形状 `[N]` 的 bool，`None` 表示全部有效。
- 目标分布是 $(1 - \varepsilon) \cdot \text{onehot}(y) + \varepsilon / C$，loss 是有效行上每行 cross entropy 的平均；`dlogits` 与 `logits` 同形状，无效行的梯度为 0。
- 没有有效行时返回 `loss = 0.0` 和全零梯度。
- 要求 $C \ge 2$、$0 \le \varepsilon < 1$、标签在 $[0, C)$ 内，否则抛 `ValueError`。logits 都是有限值，$N \le 1000$，$C \le 10000$。

### 输入输出示例

```text
cross_entropy([[0, 0]], [1])  -> loss = log(2) ≈ 0.6931, dlogits = [[0.5, -0.5]]
```

两个类别 logits 相同，softmax 是 `[0.5, 0.5]`，目标是 `[0, 1]`，梯度就是两者之差。

### 解题思路与正确性

`log_softmax` 先减去每行最大值，再减去 $\log \sum \exp$。减去同一个常数不改变 softmax，但保证最大的指数是 $e^0 = 1$，不会溢出。loss 直接用 log 概率相乘，而不是先算概率再取 log，避免概率下溢成 0 后取 log 得到 `-inf`。

每行目标分布的和是 1，所以每行 cross entropy 对 logits 的梯度是 $\text{softmax} - \text{target}$。再乘上 mask，并除以有效行数，就是平均 loss 的梯度。

用了 label smoothing 后，目标分布本身的熵不为 0，所以 loss 的最小值也不是 0。cross entropy 等于 KL 散度加上目标分布的熵，两者只差一个常数，梯度相同。

### 完整参考实现（Python 3）

```python
import numpy as np


def log_softmax(logits):
    """按行计算 log-softmax。先减去每行最大值，exp 就不会溢出。"""
    shifted = logits - logits.max(axis=1, keepdims=True)
    return shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))


def check_inputs(logits, labels, smoothing):
    if logits.ndim != 2 or logits.shape[1] < 2:
        raise ValueError(
            f"logits must have shape [N, C] with C >= 2, got {logits.shape}"
        )
    num_rows, num_classes = logits.shape
    if labels.shape != (num_rows,) or not np.issubdtype(labels.dtype, np.integer):
        raise ValueError(
            f"labels must be integers of shape ({num_rows},), got {labels.dtype} {labels.shape}"
        )
    if np.any(labels < 0) or np.any(labels >= num_classes):
        raise ValueError(f"labels must be in [0, {num_classes})")
    if not 0 <= smoothing < 1:
        raise ValueError(f"smoothing must be in [0, 1), got {smoothing}")


def cross_entropy(logits, labels, mask=None, smoothing=0):
    """带 mask 和 label smoothing 的 cross entropy，返回 (loss, dlogits)。

    logits: [N, C]，labels: [N] 整数，mask: [N] bool（None 表示全部有效）。
    目标分布是 (1 - smoothing) * one_hot + smoothing / C，loss 只在有效行上平均。
    没有有效行时返回 loss = 0 和全零梯度。
    """
    logits = np.asarray(logits, dtype=float)
    labels = np.asarray(labels)
    check_inputs(logits, labels, smoothing)
    num_rows, num_classes = logits.shape

    valid = (
        np.ones(num_rows, dtype=bool) if mask is None else np.asarray(mask, dtype=bool)
    )
    if valid.shape != (num_rows,):
        raise ValueError(f"mask must have shape ({num_rows},), got {valid.shape}")
    num_valid = int(valid.sum())
    if num_valid == 0:
        return 0.0, np.zeros_like(logits)

    log_probs = log_softmax(logits)  # [N, C]
    target = np.full_like(logits, smoothing / num_classes)  # [N, C]
    target[np.arange(num_rows), labels] += 1 - smoothing

    row_loss = -(target * log_probs).sum(axis=1)  # [N]
    loss = float((row_loss * valid).sum() / num_valid)
    # 每行目标分布的和为 1，所以 d(loss)/d(logits) = softmax - target
    grad = (np.exp(log_probs) - target) * valid[:, None] / num_valid
    return loss, grad
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.isclose(loss, np.log(2))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def numeric_grad(fn, x, eps=1e-4):
    """中心差分，逐个元素估计 fn 对 x 的梯度。"""
    grad = np.zeros_like(x)
    for index in np.ndindex(x.shape):
        plus = x.copy()
        minus = x.copy()
        plus[index] += eps
        minus[index] -= eps
        grad[index] = (fn(plus) - fn(minus)) / (2 * eps)
    return grad


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


# 两类等概率：loss = log 2，梯度是 softmax - one_hot
loss, grad = cross_entropy([[0, 0]], np.array([1]))
assert np.isclose(loss, np.log(2))
assert np.allclose(grad, [[0.5, -0.5]])

# 极端 logits 不溢出；被 mask 掉的行梯度为 0
logits = np.array([[1000.0, -1000.0, 0.0], [1.0, 2.0, 3.0]])
labels = np.array([0, 2])
mask = [True, False]
loss, grad = cross_entropy(logits, labels, mask, 0.1)
assert np.isfinite(loss)
assert np.all(grad[1] == 0)


# 解析梯度与数值梯度一致
def masked_loss(x):
    return cross_entropy(x, labels, mask, 0.1)[0]


assert np.allclose(numeric_grad(masked_loss, logits), grad, atol=1e-6)

# 全部被 mask 时 loss 有定义，等于 0
assert cross_entropy(logits, labels, [False, False])[0] == 0

expect_value_error(cross_entropy, [[0.0]], [0])  # C 必须 >= 2
expect_value_error(cross_entropy, [[0.0, 1.0]], [2])  # 标签越界
expect_value_error(cross_entropy, [[0.0, 1.0]], [0], None, 1)  # smoothing 必须 < 1
```

### 复杂度与追问

时间和空间都是 O(NC)。

- 追问「输入是 token 序列 `[B, T, C]` 怎么办」：先把 logits 展平成 `[B*T, C]`，labels 和 mask 展平成 `[B*T]`。训练语言模型时 mask 一般只保留 response 部分的 token。
- 追问「标签里用 -100 表示忽略」：先根据 `labels == -100` 生成 mask，再把这些位置的标签替换成任意合法下标（比如 0），然后才能按标签取值。直接拿 -100 当下标，类别数不到 100 时会报 IndexError；类别数更多时 NumPy 会把它当成倒数第 100 个类别，静默取到错误的值。

## 相关题

- [[sys-eos-mask]]：后训练里 loss mask 在哪里截断，EOS 本身和 EOS 之后的 pad 该不该计入。
- [[sys-adv-bcast]]：RL 版的 masked loss，序列级优势乘到 response token 上，prompt 和工具返回不计入。
- [[coding-cross-entropy]]：PyTorch 白板版，同样用 log 域和 ignore 下标，但不要求手写梯度和 label smoothing。
- [[coding-logsumexp]]：这里 log-softmax 用的 logsumexp 技巧单独成题，讲减 max 和整行 $-\infty$ 的 edge case。

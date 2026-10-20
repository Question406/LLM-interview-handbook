---
id: apple-topk-sample
section: apple
order: 3
level: A
title: Apple 电面：温度、top-k、nucleus 顺序，端侧为什么常 top-k？
quick: >-
  顺序是先除温度，再 top-k，再 nucleus，最后采样；端侧常用 top-k，因为候选数固定、延迟可预期，也好编成 ANE 的静态图。
tags:
  - 完整编程练习
  - Apple
  - Sampling
  - Top-k
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: The Curious Case of Neural Text Degeneration
    url: https://arxiv.org/abs/1904.09751
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + NumPy，CPU 上验证；没有测 GPU、batch 或性能。

### 题面、接口与约束

- `sample_temp_k_p(logits, T, k, p, rng, mask=None) -> int`：对一维 logits `[V]` 采样一个 token id。顺序固定为：合法性 mask → 除以温度 `T` → top-k → 在重新归一化的分布上做 top-p → 抽样。
- `T >= 0`，`0 <= p <= 1`，`k` 是 `None`（不做 top-k）或正整数；`mask` 与 logits 同形状，`True` 表示允许生成。
- `T == 0` 或 `p == 0` 时走 greedy，返回合法 token 里 logit 最大的那个。
- 概率并列时按 token id 从小到大排；全部 token 被 mask、参数越界、logits 含 NaN 或 $+\infty$ 时抛 `ValueError`。

### 输入输出示例

```text
sample_temp_k_p([0, 0, 0], T=1, k=1, p=1, rng)                          -> 0   # 并列时 top-1 留最小 id
sample_temp_k_p([2, 1, 0], T=0, k=None, p=1, rng, [False, False, True]) -> 2   # 只有 token 2 合法
sample_temp_k_p([1, 2], T=1, k=None, p=1, rng, [False, False])         -> ValueError
```

### 解题思路与正确性

控制符之类禁止生成的 token 在温度之前就 mask 掉，这样它们不参与 top-k 排名，也不占 top-p 的概率质量。全部被禁时，`np.argmax` 会对全 $-\infty$ 的数组静默返回 token 0，所以入口要显式报错。

温度缩放前先减最大值再除以 `T`。极小的正 `T` 下，最大 logit 变成 0，其余变成很大的负数，`exp` 不会上溢。

top-k 用稳定排序在 logit 上选前 `k` 个，其余置 $-\infty$。top-p 在 top-k 之后的概率上按降序累计，保留到第一个让累计质量达到 `p` 的 token 为止（包括它），所以核里至少有一个 token。核内概率重新归一化后再抽样。

### 完整参考实现（Python 3）

```python
import math

import numpy as np


def sample_temp_k_p(logits, T, k, p, rng, mask=None):
    """按 mask → 温度 → top-k → top-p 的顺序采样一个 token id。

    T == 0 或 p == 0 时返回合法 token 中 logit 最大者；并列时取较小的 id。
    """
    scores = np.asarray(logits, dtype=float).copy()
    if scores.ndim != 1 or scores.size == 0:
        raise ValueError(f"logits must be a non-empty 1-D array, got shape {scores.shape}")
    if np.isnan(scores).any() or np.isposinf(scores).any():
        raise ValueError("logits must not contain NaN or +inf")
    if not math.isfinite(T) or T < 0:
        raise ValueError(f"temperature must be finite and >= 0, got {T}")
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError(f"top_p must be in [0, 1], got {p}")
    if k is not None and (type(k) is not int or k < 1):
        raise ValueError(f"top_k must be None or a positive int, got {k!r}")

    if mask is not None:
        if np.shape(mask) != scores.shape:
            raise ValueError(f"mask shape {np.shape(mask)} != logits shape {scores.shape}")
        scores = np.where(mask, scores, -np.inf)
    if not np.isfinite(scores).any():
        raise ValueError("every token is masked out")

    if T == 0 or p == 0:
        return int(np.argmax(scores))  # argmax 并列时返回最小下标

    # 先减 max 再除 T：极小的正 T 下也不会上溢
    scores = (scores - scores.max()) / T

    # 稳定排序：分数并列时较小的 token id 排在前面
    if k is not None:
        order = np.argsort(-scores, kind="stable")
        scores[order[k:]] = -np.inf

    weights = np.exp(scores)
    probs = weights / weights.sum()

    order = np.argsort(-probs, kind="stable")
    cumulative = np.cumsum(probs[order])
    # 第一个累计质量 >= p 的位置也要保留，因此核里至少有一个 token
    nucleus_size = min(probs.size, int(np.searchsorted(cumulative, p, side="left")) + 1)
    kept = order[:nucleus_size]

    kept_probs = probs[kept] / probs[kept].sum()
    return int(rng.choice(kept, p=kept_probs))
```

### 可执行测试

```python
def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


rng = np.random.default_rng(2)

# 三个 logit 并列、k=1：只保留 id 最小的 token 0
assert all(sample_temp_k_p([0, 0, 0], 1, 1, 1, rng) == 0 for _ in range(20))

# 极小的正温度不会溢出，结果接近 greedy
assert sample_temp_k_p([1000, 999], 1e-10, None, 1, rng) == 0

# T=0 走 greedy，并且只在合法 token 里选
assert sample_temp_k_p([2, 1, 0], 0, None, 1, rng, [False, False, True]) == 2

# p=0 也走 greedy
assert sample_temp_k_p([0, 5, 1], 1, None, 0, rng) == 1

# 很小的 p 只保留概率最高的 token
assert all(sample_temp_k_p([0, 3, 1], 1, None, 0.01, rng) == 1 for _ in range(20))

# 全部 token 被 mask 时报错，而不是静默返回 token 0
expect_value_error(sample_temp_k_p, [1, 2], 1, None, 1, rng, [False, False])

# 非法参数
expect_value_error(sample_temp_k_p, [1, 2], -1, None, 1, rng)
expect_value_error(sample_temp_k_p, [1, 2], 1, 0, 1, rng)
expect_value_error(sample_temp_k_p, [1, 2], 1, None, 1.5, rng)
expect_value_error(sample_temp_k_p, [1, float("nan")], 1, None, 1, rng)

# 不截断时采样频率接近 softmax：logits [0, log 3] 对应概率 [0.25, 0.75]
draws = [sample_temp_k_p([0, math.log(3)], 1, None, 1, rng) for _ in range(10000)]
assert abs(sum(draws) / len(draws) - 0.75) < 0.02
```

### 复杂度与追问

设词表大小为 V。这份实现做两次稳定全排序，时间 O(V log V)，额外空间 O(V)。

- 追问「端上能不能更快」：top-k 改用 `np.argpartition` 或堆，O(V + k log k)，之后 top-p 只需在 k 个候选上排序。代价是要另外规定第 k 名并列时保留谁。没改实现之前，不能把这份代码说成线性。
- 追问「15 分钟电面写到什么程度」：写对正向流程、讲清顺序，处理好 $T=0$、核被裁空和全 mask，再用减 max 保证数值稳定，就够了。

## 背景

Apple Siri / Intelligence 相关 MLE 电面常把 sampling 和 attention、k-means 放在同一批 ML coding 里，同一簇公开讨论见 `apple-mha-code`。这题不是某条带 URL 的逐字真题，是按「手写解码 + 端侧约束」整理的。Exponent 的 Apple MLE 指南也提到，on-device 岗会问延迟、量化和推理限制，采样参数正好落在这条线上。

## 顺序：温度先改分布，再截断

记 logits 为 $z\in\mathbb{R}^{|V|}$。Apple 公开的 on-device 模型词表大约 49k。

1. 温度：$z' = z / T$，$T>0$。$T<1$ 让分布更尖，$T>1$ 更平。$T\to 0$ 时不要真除以零，直接退化成 argmax。
2. Top-k：只保留 $z'$ 里最大的 $k$ 个，其余置成 $-\infty$（或足够负的有限值，见 `apple-ondevice-quant`）。
3. Nucleus / top-p：在温度化并过了 top-k 的分布上按概率降序累加，取质量 $\ge p$ 的最短前缀，其余清掉，再归一化。
4. 从剩余分布采样。禁止生成的控制符在第 1 步之前就 mask 掉。

常见错误是先 softmax 再除 $T$，或者先 top-p 再除 $T$。这样截出来的集合不随温度变化，和常见开源实现也对不上。Top-k 与 top-p 同时开时必须规定先后，业界默认温度 → top-k → top-p。两种顺序留下的 token 不同，面试里把约定说死，比争论哪个更正确重要。

$p=1$ 等于关掉 nucleus；$p=0$ 应退化成贪心，$k=1$ 本身就等于贪心。不能把候选裁空后再除以零，也不要对全被 mask、softmax 结果全是 `NaN` 的分布继续抽样。

## 端侧为什么常用 top-k

云端可以每步对十万词表做完整排序再采样，手机上不行。

- **延迟可预期。** Top-k 只要找最大的 $k$ 个，用堆或 `np.partition`，最坏 $O(|V|+k\log k)$，候选数固定。Nucleus 要先算出全词表概率再扫前缀，保留个数随 $p$ 和当前分布变化，p99 延迟会抖。Siri 语音链路的预算见 `apple-siri-latency`：解码一步的采样必须在微秒到亚毫秒级，不能偶尔卡十几毫秒。
- **静态 shape。** ANE 几乎要求固定形状，见 `apple-ane`。Top-k 的候选张量永远是 $[B,k]$；nucleus 的有效长度取决于数据，图要么按最坏的 $|V|$ 分配，要么退回 CPU。
- **小模型的长尾质量差。** On-device 模型大约 3B。温度一升高，长尾里会冒出乱码和语言混杂。Top-k 把尾巴直接砍掉，比只调 $p$ 更稳。产品里的摘要、改写经常用 $k=1$ 或很小的 $k$，要的是可复现，不是多样性。
- **功耗。** Apple 公开的数字是：iPhone 15 Pro 上首 token 延迟大约每个输入提示（prompt）token 0.6 ms，生成约 30 token/s（投机解码之前）。如果采样每步都做全排序，会吃掉这 30 token/s 的一部分，而且这部分计算用不上 Neural Engine。

可以主动补一句：创造性写作可以再叠一个较大的 $p$；工具调用、槽位填充、日期这类输出用贪心或很小的 $k$。不要一套超参用在所有 adapter 上。

## 追问

- **为什么不永远用 nucleus？** 从质量看 nucleus 往往更自然，但端上要为最坏的 $|V|$ 和可变的候选数付出代价。先 top-k 再用较小的 $p$，是延迟和质量之间的折中。
- **和 KV cache 有什么关系？** 采样只看当前 logits，不改 cache。但采错的 token 会让后续 token 在错误的前缀上继续生成，语音里已经读出的词很难撤回，所以产品超参偏保守。
- **投机解码时要注意什么？** Apple 公开文章里 30 token/s 是投机解码之前的数字。草稿模型也要用同一套截断策略，否则验证时两边的分布对不上。
- **mask 用 $-\infty$ 在 ANE 上行不行？** 如果采样仍在 CPU 上对小 $k$ 做 fp32 softmax，$-\infty$ 没问题。如果 logits 已经量化，见 `apple-ondevice-quant`。

## 相关题

- [[coding-topk-nucleus]]：参考实现和测试与本卡相同，题面是通用白板，没有端侧和 ANE 的追问。
- [[p3a-cohere-numpy-top-k-sampling]]：Cohere 用 NumPy 只写 top-k，要求传入 rng、返回原 token id，top-p 放在追问里。
- [[coding-gumbel-max]]：用 argmax 加 Gumbel 噪声代替 softmax 加逆变换采样，可以接在截断之后。
- [[apple-spec-edge]]：同是 Apple 端侧题，讲投机解码值不值得上；草稿要用同一套截断策略就是两题的交点。

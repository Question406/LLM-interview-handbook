---
id: coding-topk-nucleus
section: coding
order: 8
level: S
title: 白板：温度 → top-k → nucleus 的顺序，实现细节
quick: >-
  sampling 先屏蔽非法 token，再除温度 $T$，做 top-k，随后在剩余质量重新 normalization 的分布上做 nucleus 并
  sampling。温度会改变 top-p 的累计质量，所以这一步必须在温度化之后；$T=0$ 或 $p=0$ 直接走 greedy。
tags:
  - 完整编程练习
  - Coding
  - Sampling
  - Nucleus
  - Apple
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: The Curious Case of Neural Text Degeneration
    url: 'https://arxiv.org/abs/1904.09751'
    type: primary
  - title: Generation strategies (Hugging Face)
    url: 'https://huggingface.co/docs/transformers/en/generation_strategies'
    type: secondary
  - title: torch.nn.functional.softmax
    url: 'https://pytorch.org/docs/stable/generated/torch.nn.functional.softmax.html'
    type: primary
---

## 题目描述

实现带温度、top-k、top-p 和 vocabulary mask 的单 token sampling 器。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`sample_temp_k_p(logits,T,k,p,rng,mask=None)` 返回一个整数 token id。logits 为 `[V]`，可包含代表屏蔽的负无穷；mask 为同形布尔数组，True 表示允许，至少有一个合法 token。T>=0，k 为 None 或正整数，p 在 `[0,1]`，rng 为注入的随机数生成器。

处理语义依次为屏蔽非法 token、将 logits 除以 T、保留 top-k、对保留项按指数值做 softmax normalization、保留累计概率首次达到 p 的最短降序前缀，最后重新 normalization 并 sampling。概率相同时 token id 小者优先。T=0 或 p=0 时直接返回合法 token 中 logit 最大者，同分选小 id。

### 示例

```text
logits=[0,0,0], T=1, k=1, p=1，返回 0。
logits=[2,1,0], T=0, k=None, p=1, mask=[False,False,True]，返回 2。
所有情况下均不能返回被 mask 屏蔽的 token。
```

## 解题思路与参考答案

我会先做合法性 mask，再调温度、做 top-k，最后在剩余概率上累计 top-p，保留首次达到阈值的 token 后重新 normalization sampling。比如只有一个合法 token，即使温度为 0，也要返回那个 token；全被屏蔽则报错。并列排序和空核行为也要在接口里先定清楚。


## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + NumPy，CPU 上验证；没有测 GPU、batch 或性能。

### 题面、接口与约束

- `sample_temp_k_p(logits, T, k, p, rng, mask=None) -> int`：对一维 logits `[V]` sampling 一个 token id。顺序固定为：合法性 mask → 除以温度 `T` → top-k → 在重新 normalization 的分布上做 top-p → 从剩余 token 里按概率 sampling。
- `T >= 0`，`0 <= p <= 1`，`k` 是 `None`（不做 top-k）或正整数；`mask` 是与 logits 同形状的布尔数组，`True` 表示允许。
- `T == 0` 或 `p == 0` 时不 sampling，直接返回合法 token 里 logit 最大的那个。
- 概率并列时按 token id 从小到大排；全部 token 被 mask 时抛 `ValueError`，参数越界、logits 含 NaN 或 $+\infty$ 时也抛 `ValueError`。

### 输入输出示例

```text
sample_temp_k_p([0, 0, 0], T=1, k=1, p=1, rng)                          -> 0   # 三个并列，top-1 只留最小 id
sample_temp_k_p([2, 1, 0], T=0, k=None, p=1, rng, [False, False, True]) -> 2   # 只有 token 2 合法
sample_temp_k_p([1, 2], T=1, k=None, p=1, rng, [False, False])         -> ValueError
```

### 解题思路与正确性

mask 必须最先做。被禁的 token 不应该参与温度缩放、top-k 排名和 top-p 累计；如果全部被禁，`np.argmax` 会对全 $-\infty$ 的数组静默返回 0，所以要在入口显式报错。

温度缩放前先减去最大值，再除以 `T`。这样极小的正 `T`（如 `1e-10`）下，最大 logit 变成 0，其他 logit 变成很大的负数，`exp` 不会上溢成 `inf`。

top-k 用稳定排序在 logit 上选前 `k` 个，其余置 $-\infty$。top-p 在 top-k 之后重新 normalization 的概率上做：按概率降序累计，`searchsorted(..., side="left") + 1` 找到第一个让累计质量达到 `p` 的位置，并把它也保留下来，所以核里至少有一个 token。最后对核内概率再 normalization，交给 `rng.choice`。

### 完整参考实现（Python 3）

```python
import math

import numpy as np


def sample_temp_k_p(logits, T, k, p, rng, mask=None):
    """按 mask → 温度 → top-k → top-p 的顺序 sampling 一个 token id。

    T == 0 或 p == 0 时返回合法 token 中 logit 最大者；并列时取较小的 id。
    """
    scores = np.asarray(logits, dtype=float).copy()
    if scores.ndim != 1 or scores.size == 0:
        raise ValueError(
            f"logits must be a non-empty 1-D array, got shape {scores.shape}"
        )
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
            raise ValueError(
                f"mask shape {np.shape(mask)} != logits shape {scores.shape}"
            )
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

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert all(sample_temp_k_p([0, 0, 0], 1, 1, 1, rng) == 0 for _ in range(20))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

数值结果用 `allclose` 一类带容差的 assertion 检查，并同时确认形状；随机输入固定 seed。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

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

# 不截断时 sampling 频率接近 softmax：logits [0, log 3] 对应概率 [0.25, 0.75]
draws = [sample_temp_k_p([0, math.log(3)], 1, None, 1, rng) for _ in range(10000)]
assert abs(sum(draws) / len(draws) - 0.75) < 0.02
```

### 复杂度与追问

设 vocabulary 大小为 V。这份实现做了两次稳定全排序，时间 O(V log V)，额外空间 O(V)。

- 追问「能不能做到线性」：top-k 可以改用 `np.argpartition`，平均 O(V)，但它不保证并列时的顺序，要另外规定第 k 名并列时保留谁。top-p 仍要对保留下来的候选排序，如果先做了 top-k，就只排 k 个，O(V + k log k)。在没改实现之前，不能把这份代码说成线性复杂度。
- 追问「batch 怎么做」：每条样本的核大小不同，不能假设同一个 `nucleus_size`。常见做法是对整行排序后用累计概率生成布尔 mask，把核外位置置成 $-\infty$，再整体 softmax sampling。

## 题怎么来的

Holtzman et al. 提出的 nucleus sampling 已经是 decoding 的默认组件。Apple Siri MLE 电面把 sampling 和 attention 放在一起考；OpenAI、Anthropic 的推理岗会问温度和截断谁先谁后。公开实现（Transformers 的 `generate`）的顺序是温度 → top-k → top-p，白板上按这个顺序写，不要自己发明第四种。稳定 softmax 见 `coding-softmax-stable`；和 greedy、beam search 的取舍见 `coding-beam-search`。

## 顺序：先整形分布，再截尾

记 logits 为 $z$。非法位置先打成 $-\infty$，再做 $z' = z / T$（$T>0$），得到温度化后的分布

$$
\pi_T=\mathrm{softmax}(z').
$$

Top-k 只保留 $\pi_T$ 里最大的 $k$ 个，其余概率置零。Nucleus（top-p）在剩下的概率上按降序累计，取质量和 $\ge p$ 的最短前缀，其余丢掉，再在核内重新 normalization 后 sampling。

$T$ 越小分布越尖，同一个 $p$ 能进核的 token 越少，所以 nucleus 必须定义在温度化之后的分布上。如果先按原始 softmax 截断再除 $T$，截出来的集合不随温度变化，结果和开源推理栈对不上。

正温度不改变 logit 之间的排序，所以 top-k 选出的集合与先除不先除 $T$ 无关；但它改变每个 token 的概率质量，top-p 的累计阈值必须在温度化后的概率上算。Top-k 与 top-p 同时开时，常见做法是先 k 后 p（HF 默认）。反过来保留的集合会不同，选了哪种就写进注释和单测。

$p=1$ 等于不截尾。$T=0$ 或 $p=0$ 走 $\arg\max$，不要真的除以 0，也不要把核裁空。

## Edge Cases 比公式更容易出错

- 在 logits 上做累计：logit 不是概率，累计到 $p$ 没有质量上的含义。
- 截尾后不重新 normalization 就 `choice`：概率和小于 1，NumPy 会直接报错。
- 对全 $-\infty$ 的数组减 max：$-\infty - (-\infty)$ 是 NaN，整行变成 NaN。这份实现在减 max 之前就把全 mask 的情况挡掉了。
- 有重复惩罚时，要规定它是改 logits 还是改概率；通常改 logits，并且发生在 softmax 之前。

Apple on-device 还会问：vocabulary $10^5$ 时 top-k 要不要全排序。用 `argpartition` 的 O(V) 就够，除非你能解释为什么需要每步 `sort`。Gumbel-max 是另一条 sampling 路线，见 `coding-gumbel-max`。

## 追问

**为什么不能先 top-p 再除温度？**
核取决于当前的概率分布。先截断再改 $T$，等于在另一个分布上定的核，和 Transformers 的默认策略不一致。
**$p=0$ 怎么办？**
按定义核是空的，normalization 会失败。实现上把它当作 greedy，结果应和 $T=0$ 落到同一个 token。
**top-k 和 top-p 谁先？**
先约定再写测试。HF 常见先 k 后 p；两种顺序保留的 token 不同，不要口头含糊过去。

## 相关题

- [[apple-topk-sample]]：参考实现和测试与本卡相同，Apple 版多了「on-device 为什么常用 top-k」的追问。
- [[p3a-cohere-numpy-top-k-sampling]]：NumPy 版本，只做 top-k，强调可复现的 rng 和并列时按 id 排序。
- [[coding-gumbel-max]]：截断之后可以用 Gumbel-max sampling，它的温度和 Gumbel-softmax 的松弛温度不是一回事。
- [[coding-token-logprob]]：训练端算 logprob 时要除以和 sampling 时相同的温度，否则新 old policy 的比值会偏。
- [[coding-beam-search]]：同样是从 logits 出 token，beam 走确定性搜索，可以和 sampling 对照取舍。


## Batch 支持范围与完整生成版本

本题的函数只接收一条请求的 `[V]` logits，返回一个 token。支持 `[B,V]`、逐行参数与两种随机实现的版本见[新增 batch 实现](?book=apple-interview&section=decoding&question=apple-batched-token-selection)。

---
id: stepfun-top-p-sampling
section: coding
order: 160
level: A
title: 阶跃星辰：手撕 top-p 采样，边界怎么处理？
quick: >-
  softmax 之后按概率降序累加，留下累计质量刚达到 $p$ 的最小前缀，重新归一化再抽样。边界要处理 $p=0/1$、全 `-inf` 和概率并列。
tags:
  - StepFun
  - Sampling
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阶跃星辰大模型算法实习一面
    url: https://www.nowcoder.com/feed/main/detail/5cb1ebe809fd402d844cce47380a926f
    type: candidate-first-hand
---

## 题目描述

实现 NumPy 函数 `top_p_sample(logits,p,rng,mask=None)`，从一条词表分布做 nucleus（top-p）采样，返回被抽中的 token 下标。面经披露了 top-p 手写题，以下参数与并列规则为手册重构练习约定。

`logits` 是长度 V 的一维有限实数序列，V>0；`rng` 是调用者提供的 `numpy.random.Generator`。可选 `mask` 是长度 V 的布尔数组，**True 表示允许被选择**，至少一个位置可选。`p` 在 `[0,1]`。

未屏蔽位置的概率由 softmax(logits) 定义，屏蔽位置概率为0。p=0 时返回最大 logit 的可选 token，若并列返回下标最小者。p>0 时，按概率降序排列，概率相同保持 token 原始下标顺序；保留累计概率首次达到或超过 p 的最小前缀，达到边界的 token 包含在内。在保留集合内按原概率重新归一化并使用传入 rng 抽样。p=1 保留全部可选 token。

### 示例

```text
输入：logits=log([0.5,0.3,0.2])，p=0.5，mask=None
输出：0（唯一可能结果）

相同logits，p=0.6
输出分布：token 0的概率为5/8，token 1的概率为3/8，token 2不会出现

相同logits，p=0，mask=[False,True,True]
输出：1
```

随机样例验证输出集合或采样分布；不要求不同 NumPy 版本在相同种子下产生同一条随机序列。

## 解题思路与参考答案

top-p 采样就是在概率上截一个最小前缀：softmax 之后按概率从大到小累加，累计质量刚达到 $p$ 的那个 token 也留下，然后在这些 token 上重新归一化再抽。剩下的功夫都在边界上：$p=0$、$p=1$、整行被 mask、概率并列。

这是阶跃星辰（StepFun）大模型算法实习一面的题，来自牛客候选人原帖，可信度 B。面试时间原帖没写，帖子发布于 2026-03-27，原话是手撕 **“top-p sampling、grpo”**。拼多多日常实习二面也出过最简单的 top-k 采样。

最常见的错误是把 nucleus 写成「随机挑一个高概率 token」：先 `softmax`，再随便抽，既没有累计概率质量，也没有截尾后重新归一化。比如概率是 `[0.5, 0.3, 0.2]`、$p=0.6$，正确的结果只会在前两个 token 里按 5:3 抽，第三个永远抽不到。面试官主要看三点：在哪个分布上截断；累计概率刚好达到 $p$ 的那个 token 有没有留下；$p\to 0$ 或整行被 mask 时会不会截成空集。如果同一面还要手撕 GRPO，别把这道采样题和组内优势混成一句「随机采样」。温度和 top-p 的完整先后顺序见 `code-sampling`，本题按阶跃原帖把边界讲清楚就行。

## 流程：先屏蔽非法词，再按概率排序截断

记未归一化的 logit 为 $z$。先把禁用词的 logit 设成 $-\infty$，再在有限位置上做数值稳定的 softmax，然后找最小的前缀：

$$
\pi_i=\mathrm{softmax}(z)_i,\qquad
\mathcal{N}=\min\bigl\{k:\textstyle\sum_{j=1}^{k}\pi_{(j)}\ge p\bigr\}.
$$

$\pi_{(j)}$ 是按降序排好的第 $j$ 个概率，$\mathcal{N}$ 是保留下来的 token 数。在这 $\mathcal{N}$ 个 token 上重新归一化，再用 `multinomial` 抽样。$p=1$ 时保留全部合法词；$p\le 0$（或实现上 $p\to 0$）时退化成 $\arg\max$。任何情况下都要保证 $|\mathcal{N}|\ge 1$。

概率并列时用稳定排序（`mergesort`，不打乱并列项的原始顺序），这样结果可复现，也不会因为浮点抖动丢掉本该留下的边界 token。如果 top-k 和 top-p 同时开，要先说清顺序。常见做法是先截 $k$ 再截 $p$，反过来会得到另一个候选集合，单测就对不上了。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert top_p_sample(logits, 0.0, rng) == 0` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 边界与短实现

词表为空或全部被 mask 时，softmax 会得到全 `NaN`，这时要直接抛异常，别静默抽样。bf16 / fp16 的 softmax 要升到 fp32，或者用减最大值的 logsumexp。累计要按概率排序来做：温度和重复惩罚会改变 logit 的相对大小，概率才是核定义里的质量。截尾后如果不重新归一化就直接 `choice`，概率和小于 1，行为没有定义。

```python
import numpy as np


def top_p_sample(logits, p, rng, mask=None):
    """从 logits 做 top-p（nucleus）采样，返回 token 下标。

    mask 为 True 的位置可选；p <= 0 时贪心取 argmax；全部被屏蔽时抛 ValueError。
    """
    z = np.asarray(logits, dtype=np.float64)
    if mask is not None:
        z = np.where(mask, z, -np.inf)
    if not np.isfinite(z).any():
        raise ValueError("all logits are masked or non-finite")
    z = np.where(np.isfinite(z), z, -np.inf)  # NaN / +inf 也视为非法
    if p <= 0:
        return int(np.argmax(z))

    z = z - np.max(z)
    prob = np.exp(z - np.logaddexp.reduce(z))
    order = np.argsort(-prob, kind="mergesort")  # 稳定排序，并列项保持原顺序
    cumulative = np.cumsum(prob[order])
    keep_count = int(np.searchsorted(cumulative, min(p, 1.0))) + 1
    keep = order[:keep_count]

    nucleus = np.zeros_like(prob)
    nucleus[keep] = prob[keep]
    nucleus /= nucleus.sum()
    return int(rng.choice(nucleus.size, p=nucleus))


# 小测试
rng = np.random.default_rng(0)
logits = np.log([0.5, 0.3, 0.2])

# p <= 0 退化为贪心
assert top_p_sample(logits, 0.0, rng) == 0

# p = 0.5 时第一个 token 的质量刚好达到 p，只保留它
assert all(top_p_sample(logits, 0.5, rng) == 0 for _ in range(20))

# p = 0.6 时保留前两个 token，永远抽不到第三个
assert all(top_p_sample(logits, 0.6, rng) in (0, 1) for _ in range(50))

# 被 mask 的 token 不会被抽到
mask = np.array([False, True, True])
assert all(top_p_sample(logits, 1.0, rng, mask) in (1, 2) for _ in range(50))

# 全部被 mask 时抛异常
try:
    top_p_sample(logits, 0.9, rng, mask=np.zeros(3, dtype=bool))
except ValueError:
    pass
else:
    raise AssertionError("expected ValueError for an all-masked row")
```

`searchsorted` 默认 `side="left"`，找的是第一个累计值 $\ge p$ 的位置，加 1 就是保留数量，所以至少留 1 个 token。$p\ge 1$ 时 `min(p, 1.0)` 让它不截尾。`mergesort` 让并列项的顺序可复现。同一面的 GRPO 手撕见 `stepfun-grpo-group-advantage` 和 `stepfun-grpo-loss-handwrite`。

## 追问

**$p=0$ 和 $p=1$ 各走哪条分支？**
$p\le 0$ 走贪心，$p\ge 1$ 保留全部合法词。两种情况都不能对空集合调 `choice`。

**为什么累计不能按 logits 做？**
因为核的定义是「概率质量至少为 $p$」。经过温度或惩罚之后，logit 的数值已经不代表这份质量，按它累计含义就错了。

**全 `-inf` 怎么办？**
在入口和归一化之后各检查一次，直接抛异常，别抽出 `NaN`。

**和 top-k 谁先？**
先和面试官约定顺序，并写进测试；现场默认先截 $k$ 再截 $p$。

---
id: stepfun-top-p-sampling
section: coding
order: 160
level: A
title: 阶跃星辰：手撕 top-p 采样，边界怎么处理？
quick: >-
  softmax 后按概率降序累加，保留累计质量刚达到 $p$ 的最小前缀，重新归一化再抽样；要处理 $p=0/1$、全 `-inf` 和并列概率。
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

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-03-27
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：手撕 **“top-p sampling、grpo”**
- 相关：拼多多日常实习二面也出过最简单的 top-k 采样。

最常见的错误是把 nucleus 写成“随机挑一个高概率 token”：先 `softmax`，再随便抽，既没有累计概率质量，也没有截尾后重新归一化。面试官主要看三点：在哪个分布上截断；累计概率刚好达到 $p$ 的那个 token 有没有留下；$p\to 0$ 或整行被 mask 时会不会截成空集。如果同一面还要手撕 GRPO，不要把这道采样题和组内优势混成一句“随机采样”。温度和 top-p 的完整先后顺序见 `code-sampling`，本题按阶跃原帖把边界讲清楚即可。

## 流程：先屏蔽非法词，再按概率排序截断

记未归一化的 logit 为 $z$。先把禁用词的 logit 设成 $-\infty$，再在有限位置上做数值稳定的 softmax，然后找最小的前缀：

$$
\pi_i=\mathrm{softmax}(z)_i,\qquad
\mathcal{N}=\min\bigl\{k:\textstyle\sum_{j=1}^{k}\pi_{(j)}\ge p\bigr\}.
$$

$\pi_{(j)}$ 是按降序排好的第 $j$ 个概率，$\mathcal{N}$ 是保留下来的 token 数。在这 $\mathcal{N}$ 个 token 上重新归一化，再用 `multinomial` 抽样。$p=1$ 时保留全部合法词；$p\le 0$（或实现上 $p\to 0$）时退化成 $\arg\max$，任何情况下都保证 $|\mathcal{N}|\ge 1$。

概率并列时用稳定排序（`mergesort`，不打乱并列项的原始顺序），这样结果可复现，也不会因为浮点抖动丢掉本该留下的边界 token。如果 top-k 和 top-p 同时开，要先说清顺序：常见做法是先截 $k$ 再截 $p$，反过来会得到另一个候选集合，单测对不上。

## 边界与短实现

词表为空或全部被 mask 时，softmax 会得到全 `NaN`，这时必须抛异常，不能静默抽样。bf16 / fp16 的 softmax 要升到 fp32，或者用减最大值的 logsumexp。累计必须按概率排序做，而不是按 logit 排序做：温度和重复惩罚会改变 logit 的相对大小，概率才是核定义里的质量。截尾后如果不重新归一化就直接 `choice`，概率和小于 1，行为没有定义。

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

- **$p=0$ 和 $p=1$ 各走哪条分支？** $p\le 0$ 走贪心；$p\ge 1$ 保留全部合法词。两种情况都不能对空集合调用 `choice`。
- **为什么累计不能按 logits 做？** 核的定义是“概率质量至少为 $p$”。经过温度或惩罚之后，logit 的数值不再代表这份质量，按它累计含义就错了。
- **全 `-inf` 怎么办？** 在入口和归一化之后各检查一次，直接抛异常，不要抽出 `NaN`。
- **和 top-k 谁先？** 先和面试官约定顺序并写进测试；现场默认先截 $k$ 再截 $p$。

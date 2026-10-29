---
id: humansand-top-p-live-debug
section: humansand
order: 900
level: A
title: "Humans&：Top-p live coding 与现场 debug"
quick: "我会先让函数返回完整 probability vector，再接 sampling。这样 nucleus 选错与 token ID 映射错可以分开定位，不必靠一次随机输出猜问题。"
companies:
  - humansand
tags:
  - "Frontier Coding 2026-10-28"
  - 完整编程练习
  - "候选人报告改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "第一手面经：DrustZ 找工记（3），Humans& 小节"
    url: "https://www.uscardforum.com/t/topic/535363"
    type: interview
  - title: "作者原始博客"
    url: "https://drustz.com/posts/2026/09/27/jobsearch3/"
    type: interview
---

## 题目描述

来源：Mingrui (Ray) Zhang 的第一手找工记录，Humans& technical 包含手写 top-p 与实时 debug。下面的函数、缺陷类别和测试为手册整理的练习约定。

### 输入、接口与规则

实现 `top_p_probabilities(logits,p,allowed=None)`，输入一维 `[V]` logits，V>0，允许 -inf，禁止 NaN/+inf；p 在 `(0,1]`。allowed 是 None 或同形布尔 mask，True 允许，至少一个允许位置有 finite logit。返回原 vocabulary 顺序的 float64 `[V]` probabilities，总和为 1，屏蔽或不在 nucleus 的位置为 0。

按 logits 降序、同分 token ID 升序取累计概率首次达到 p 的最短前缀，保留跨阈值的 token，并重新 normalization。再实现 `sample_top_p(logits,p,rng,allowed=None)->int`，返回原始 token ID。不得修改输入，全 mask 抛 ValueError。

现场 debug 部分：解释并修复以下两类错误——直接删掉 cumulative>p 的所有项会漏掉跨阈值项；在 sorted 数组中 sampling 后直接返回 rank，会把排序位置当原 ID。要求给每个错误写一个能稳定复现的例子，再验证最终实现。

### 输入输出示例

```text
logits=log([0.4,0.35,0.25]), p=0.5 -> probabilities=[0.4/0.75,0.35/0.75,0]。
logits=log([0.1,0.6,0.3]), p=0.7 -> [0,2/3,1/3]；抽到的 token ID 只能是 1 或 2。
```

## 回答思路

> **输入与任务：** 先区分 logits、sorted rank 和原 token ID。  
> **做法与原因：** Stable sort、保留跨阈值项，然后把概率放回原 ID 顺序。  
> **正确性检查：** 用两个手算反例定位错误，再检查随机频率和全部被 mask 的情况。

## 解题思路与参考答案

我会先让函数返回完整 probability vector，再接 sampling。这样 nucleus 选错与 token ID 映射错可以分开定位，不必靠一次随机输出猜问题。

例如累计概率从 0.4 跳到 0.75 才跨过 0.5，第二个 token 必须留下。排序后还要保留原 ID；token 1 排在第 0 位，不代表应该返回 0。

### 完整参考实现

```python
import numpy as np


def top_p_probabilities(logits, p, allowed=None):
    scores = np.asarray(logits, dtype=np.float64).copy()
    if scores.ndim != 1 or scores.size == 0 or not 0 < p <= 1:
        raise ValueError("expected [V] logits and 0 < p <= 1")
    if np.isnan(scores).any() or np.isposinf(scores).any():
        raise ValueError("invalid logits")
    if allowed is not None:
        allowed = np.asarray(allowed, dtype=bool)
        if allowed.shape != scores.shape:
            raise ValueError("mask shape mismatch")
        scores[~allowed] = -np.inf
    if not np.isfinite(scores).any():
        raise ValueError("no legal finite token")
    scores -= scores.max()
    probs = np.exp(scores)
    probs /= probs.sum()
    order = np.argsort(-probs, kind="stable")
    cumulative = np.cumsum(probs[order])
    count = min(probs.size, int(np.searchsorted(cumulative, p, side="left")) + 1)
    keep = order[:count]
    result = np.zeros_like(probs)
    result[keep] = probs[keep] / probs[keep].sum()
    return result


def sample_top_p(logits, p, rng, allowed=None):
    probs = top_p_probabilities(logits, p, allowed)
    return int(rng.choice(probs.size, p=probs))
```

## 简单测试怎么写

将实现与下面测试按顺序保存为 `solution.py`，使用安装 NumPy/PyTorch 的 Python 运行 `python solution.py`。先核对题面的手算输出，再执行下列 assertions。

```python
probs = top_p_probabilities(np.log([0.4, 0.35, 0.25]), 0.5)
np.testing.assert_allclose(probs, [0.4 / 0.75, 0.35 / 0.75, 0])
# Original IDs 1 and 2 survive; sorted positions 0 and 1 are not token IDs.
np.testing.assert_allclose(
    top_p_probabilities(np.log([0.1, 0.6, 0.3]), 0.7), [0, 2 / 3, 1 / 3]
)
assert top_p_probabilities([0, 0, 0], 0.1).tolist() == [1.0, 0.0, 0.0]
assert (
    sample_top_p([1000, 0, -1000], 0.9, np.random.default_rng(1), [False, False, True])
    == 2
)
rng = np.random.default_rng(77)
counts = (
    np.bincount(
        [sample_top_p(np.log([0.1, 0.6, 0.3]), 0.7, rng) for _ in range(6000)],
        minlength=3,
    )
    / 6000
)
np.testing.assert_allclose(counts, [0, 2 / 3, 1 / 3], atol=0.025)
for logits, mask in [([0, 1], [False, False]), ([-np.inf], None)]:
    try:
        top_p_probabilities(logits, 0.9, mask)
    except ValueError:
        pass
    else:
        raise AssertionError("empty candidate set must fail")
print("Humans& top-p debug: passed")
```

## 复杂度与追问

完整排序时间 `O(V log V)`，空间 `O(V)`。当前练习是单步 `[V]`；完整 batch 生成已在 Apple Decoding 专题。动态合法集合、temperature 与 top-k 可以在确认顺序后扩展。

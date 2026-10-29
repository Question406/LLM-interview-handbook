---
id: p3a-cursor-speculative-decoding-acceptance
section: coding
order: 808
level: A
title: Cursor：speculative decoding 的接受率与残差 sampling
quick: >-
  让 draft 提出候选，target 一次给出这些位置的分布，再按 min(1, p/q) 逐个接受。首次拒绝时从 max(p − q, 0)
  normalization 后的残差 resampling 并丢弃后缀，全部接受时再补采一个 token。这样每个输出位置仍服从 target
  分布，测试还要分别检查分布正确性和模型调用次数。
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - cursor
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 1Point3Acres · Cursor：投机解码的接受率与残差采样
    url: >-
      https://www.1point3acres.com/interview/problems/f0d3fbd8-0cde-5a44-ae56-6b9e105bed69
    type: secondary
---

## 题目描述

实现 speculative decoding 的本地模拟器，在减少目标模型调用的同时保持目标模型的生成分布。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`speculative(target_batch,draft_next,limit,block,rng,eos=-1)` 返回 `(tokens,target_calls)`。`draft_next`(prefix) 返回下一 token 的概率向量 q；`target_batch`(prefix,candidates) 一次返回 K+1 个目标概率向量，其中第 i 个以 prefix 加 candidates[:i] 为条件。所有向量为同一不超过 50 的 vocabulary 上的 normalization 分布。

每轮最多提出 block 个草稿 token，验证得到与目标模型逐 token sampling 相同的分布：候选 token x 以 `min(1,p(x)/q(x))` 的概率接受；首次拒绝后丢弃剩余草稿，从 `max(p-q,0)` normalization 后的分布 sampling 替代 token；全部接受时允许从目标模型的额外分布再取一个 token。输出不超过 limit 个 token，遇 eos 停止且不包含 eos；limit=0 时不调用目标模型。limit<=100，block 为正整数，`target_calls` 是 `target_batch` 实际调用次数。

### 示例

```text
草稿和目标模型在任何 prefix 下都以概率 1 输出 token 0。
limit=10, block=3, eos=-1。
返回 tokens=[0,0,0,0,0,0,0,0,0,0], target_calls=3。
```

## 解题思路与参考答案

## 题目

我会先实现普通 autoregressive decoding 作为基线，再让 draft 提议、target 批量验证，用接受规则和残差 sampling 保证分布一致。题目要求两种 decoding 的输出 sampling 分布相同，模型训练不在范围内。

> 来源：一亩三分地 Cursor 题目详情页（2026-10-18 读取）。题面是网站从面经整理的；网站收录不等于公司官方确认，也不要把它推到 Cursor 其他岗位的面试上。下面的接口、约束和测试是手册补的练习约定。

## 接受与拒绝后分别怎么处理

speculative decoding 的做法是：小的 draft 模型先连续猜几个 token，大的 target 模型一次前向就把这几个位置的分布都算出来，再逐个决定接不接受。

接受规则是这道题的核心。设 draft 在某个位置的分布是 q，target 的分布是 p，draft 提出的 token 是 x：

- 以 $\min(1, p(x) / q(x))$ 的概率接受 x；
- 如果拒绝，就从残差分布 $\max(p - q, 0)$ normalization 之后重新 sampling 一个 token，并丢掉这个位置之后的所有候选。

丢掉后缀是必须的：后面候选的 target 分布是以「前面的候选都被接受」为条件算的，一旦这里换了 token，那些分布就不再成立。

如果所有候选都被接受，target 在最后一个位置多算出来的那个分布可以直接用来再 sampling 一个 token，这一轮就多产出了一个。

工程上还要注意 KV cache 的回滚：缓存要截到实际接受的长度。评估加速效果时，先用小 vocabulary 的分布实验验证正确性，再去测量真实延迟，只比较模型调用次数是不够的。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `speculative(target_batch, draft_next, limit, block, rng, eos=-1)`：返回 `(tokens, target_calls)`，即生成的 token 列表和 target 模型的调用次数。
- `draft_next(prefix)`：返回 draft 模型在 `prefix` 之后的概率向量 q。
- `target_batch(prefix, candidates)`：一次返回 K + 1 个分布，第 i 个分布 $p_i$ 条件于 `prefix + candidates[:i]`。所有分布必须同 vocabulary、已 normalization，否则抛 `ValueError`。
- 每轮 draft 最多提出 `block` 个候选（可以包括 EOS），按顺序验证；第一次拒绝时 resampling 并丢弃后续候选；全部接受时从最后一个分布多采一个 token。
- EOS 不放进输出，生成到 EOS 或满 `limit` 个 token 就停。`limit = 0` 时不调用任何模型。vocabulary 不超过 50，`limit` 不超过 100。

### 输入输出示例

```text
target p = [0.8, 0.2]，draft q = [0.2, 0.8]
重复 6000 次 speculative(..., limit=1, block=3)，统计第一个 token：
token 0 的频率 ≈ 0.8      # 服从 target，而不是 draft 的 0.2
```

draft 和 target 都确定地输出 token 0 时，所有候选都被接受。`limit=10, block=3` 需要 3 轮：前两轮各产出 3 + 1 个，第三轮产出 2 个，target 只调用 3 次。

### 解题思路与正确性

为什么输出分布等于 p：看某个位置最终输出 token x 的概率。

- 走接受路径：先由 draft 提出 x（概率 $q(x)$），再被接受（概率 $\min(1, p(x)/q(x))$），合起来是 $\min(q(x), p(x))$。
- 走拒绝路径：总拒绝概率是 $\sum_y \max(q(y) - p(y), 0)$，它恰好等于残差的总质量 $\sum_y \max(p(y) - q(y), 0)$；再从残差里采到 x 的概率是 $\max(p(x) - q(x), 0)$ 除以这个总质量。两者相乘，就是 $\max(p(x) - q(x), 0)$。

两条路径相加：$\min(p(x), q(x)) + \max(p(x) - q(x), 0) = p(x)$。所以每个被输出的位置都服从 target 分布。

代码分四步：draft 提议、target 批量打分、逐个验证、全部接受时补 sampling。残差为空只会在 $p = q$ 时出现，但那时接受概率恒为 1，不会走到拒绝分支，所以代码里把它当作不可能的情况报错。

确定性的 speculative edits 是另一种契约，不使用这里的随机接受规则，不要混在一起。

### 完整参考实现（Python 3）

```python
import numpy as np


def as_distribution(values):
    """校验并返回一维概率向量：非负、有限、和为 1。"""
    probs = np.asarray(values, dtype=float)
    if probs.ndim != 1 or len(probs) == 0:
        raise ValueError("distribution must be a non-empty 1-D vector")
    if not np.isfinite(probs).all() or np.any(probs < 0):
        raise ValueError("distribution must be finite and non-negative")
    if not np.isclose(probs.sum(), 1):
        raise ValueError("distribution must sum to 1")
    return probs / probs.sum()


def sample(rng, probs):
    return int(rng.choice(len(probs), p=probs))


def residual_sample(rng, p, q):
    """拒绝后从 max(p - q, 0) normalization 后的分布里重新 sampling。"""
    residual = np.maximum(p - q, 0)
    total = residual.sum()
    if total <= 0:
        # p == q 时接受概率恒为 1，不可能走到这里
        raise ArithmeticError("rejection with an empty residual")
    return sample(rng, residual / total)


def speculative(target_batch, draft_next, limit, block, rng, eos=-1):
    """投机 sampling，返回 (生成的 token 列表, target 调用次数)。

    draft_next(prefix) -> q：draft 模型在 prefix 之后的下一 token 分布。
    target_batch(prefix, candidates) -> [p_0, ..., p_K]：p_i 条件于 prefix + candidates[:i]，
    一次调用验证 K 个候选，并多给一个分布用于全部接受后的补 sampling。
    EOS 不进入输出；limit == 0 时不调用任何模型。
    """
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if block < 1:
        raise ValueError("block must be >= 1")

    output = []
    target_calls = 0
    while len(output) < limit:
        # 1. draft 依次提出最多 block 个候选，遇到 EOS 就停
        proposed = []
        draft_probs = []
        for _ in range(min(block, limit - len(output))):
            q = as_distribution(draft_next(output + proposed))
            token = sample(rng, q)
            draft_probs.append(q)
            proposed.append(token)
            if token == eos:
                break

        # 2. target 一次性给出每个位置的分布
        target_probs = [
            as_distribution(p) for p in target_batch(list(output), proposed)
        ]
        target_calls += 1
        if len(target_probs) != len(proposed) + 1:
            raise ValueError(
                "target_batch must return len(candidates) + 1 distributions"
            )
        if any(p.shape != draft_probs[0].shape for p in target_probs):
            raise ValueError("target and draft vocabularies differ")

        # 3. 逐个验证：以 min(1, p/q) 接受；第一次拒绝时从残差分布 resampling 并丢弃后面的候选
        all_accepted = True
        for token, q, p in zip(proposed, draft_probs, target_probs):
            if rng.random() < min(1.0, p[token] / q[token]):
                chosen = token
            else:
                chosen = residual_sample(rng, p, q)
                all_accepted = False
            if chosen == eos:
                return output, target_calls
            output.append(chosen)
            if len(output) >= limit:
                return output, target_calls
            if not all_accepted:
                break

        # 4. 全部接受时，target 的最后一个分布还能免费多采一个 token
        if all_accepted:
            extra = sample(rng, target_probs[-1])
            if extra == eos:
                return output, target_calls
            output.append(extra)
    return output, target_calls
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert abs(firsts.count(0) / len(firsts) - 0.8) < 0.025` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
rng = np.random.default_rng(5)

# draft 偏向 token 1，target 偏向 token 0：首个 token 的分布应服从 target（约 0.8）
target_dist = np.array([0.8, 0.2])
draft_dist = np.array([0.2, 0.8])


def biased_target(prefix, candidates):
    return [target_dist] * (len(candidates) + 1)


def biased_draft(prefix):
    return draft_dist


firsts = [
    speculative(biased_target, biased_draft, 1, 3, rng)[0][0] for _ in range(6000)
]
assert abs(firsts.count(0) / len(firsts) - 0.8) < 0.025

# limit == 0 时不调用 target
assert speculative(biased_target, biased_draft, 0, 3, rng) == ([], 0)

# draft 与 target 完全一致时全部接受：每轮 3 个候选 + 1 个补 sampling，10 个 token 需要 3 轮
certain = np.array([1.0, 0.0])


def certain_target(prefix, candidates):
    return [certain] * (len(candidates) + 1)


output, calls = speculative(certain_target, lambda prefix: certain, 10, 3, rng)
assert output == [0] * 10
assert calls == 3

# EOS 不进入输出
eos_dist = np.array([0.0, 1.0])
output, calls = speculative(
    lambda prefix, candidates: [eos_dist] * (len(candidates) + 1),
    lambda prefix: eos_dist,
    10,
    3,
    rng,
    eos=1,
)
assert output == []
assert calls == 1
```

### 复杂度与追问

设 vocabulary 大小为 V。每轮最多调用 draft `block` 次、target 1 次；不算模型本身，Python 这边的开销是 O(limit · V)，来自每个位置的分布校验和 sampling。

- 实际能快多少？取决于接受率、block 大小、两个模型的速度比，以及 KV cache 回滚的开销。接受率高时，一次 target 前向能产出多个 token；接受率低时，draft 的计算就白费了。
- 这份练习测了什么？只测输出分布是否正确、target 调用了几次，不测真实的推理时延。

## 相关题

- [[coding-spec-accept]]：同一条接受规则，白板题只写单轮的接受和残差，并检查 $p=q$ 时残差全零的 edge case；两题可以当一题练。
- [[google-spec-decode]]：口述无损性的道理，以及接受率怎样决定加速比。
- [[p3a-xai-speculative-edits]]：草稿换成原代码、sampling 换成 greedy 之后，接受规则退化成前缀匹配。

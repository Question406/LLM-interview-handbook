---
id: p3a-microsoft-beam-search-decoder
section: microsoft
order: 606
level: S
title: "Microsoft AI / Copilot：Beam Search：从 greedy 到 top-K 扩展"
quick: "每步将所有未结束 beam 的扩展与已结束序列一起比较，按累计 log 概率全局保留 width 条。EOS 后不再扩展，有限宽度不保证全局最优；用小词表、足够宽的搜索与穷举对照验证。"
companies:
  - microsoft
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Microsoft AI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Microsoft AI / Copilot · beam-search-decoder"
    url: https://www.1point3acres.com/interview/problems/company/microsoft/beam-search-decoder
    type: secondary
---

## 题目描述

实现一个确定性 beam search 解码器。模型以任意当前 token 序列为输入，返回下一 token 的 log 概率；维护限定数量的候选，按累计分数选择并返回最终候选序列。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `beam_search(next_logprobs, start, eos, width, max_new)`：从 `start` 开始最多生成 `max_new` 个 token，返回剩下的所有 beam，格式是 `[(tokens, score), ...]`，按分数降序。
- `next_logprobs(tokens)` 返回词表上 V 个已归一化的 log 概率。假定不含 NaN 且各项不大于 0；值为 $-\infty$ 的扩展直接丢弃。
- 每一步只扩展未结束的 beam，已生成 EOS 的 beam 原样保留。所有候选按累计 log 概率降序、token 序列升序排序，截断到 `width` 个。EOS 保留在返回的序列里，没有长度惩罚。
- `width >= 1`，`max_new >= 0`。$V \le 100$，`max_new` 不超过 30。

### 示例

词表是 {0, 1}，1 是 EOS，模型每步都给出 P(0) = 0.4、P(1) = 0.6：

```text
beam_search(model, [], eos=1, width=1, max_new=10)  -> [([1], log 0.6)]
beam_search(model, [], eos=1, width=2, max_new=2)   -> [([1], log 0.6), ([0, 1], log 0.24)]
beam_search(model, [8], eos=1, width=1, max_new=0)  -> [([8], 0.0)]
```

## 解题思路与参考答案

每一步把所有 beam 的扩展放在同一个池里，用累计 log 概率全局保留最好的 `width` 条；遇到 EOS 的序列不再扩展，但仍参与比较。比如 width 为 1 时就是 greedy，宽度足够覆盖所有路径时才等价于穷举。

## 题目

模型接口已经给好，输入一个 token 序列，返回下一个 token 的 log 概率。要求在它外面实现解码逻辑和 beam 的管理。

> 来源：一亩三分地 Microsoft AI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

每个 beam 记三样东西：token 序列、累计 log 概率、是否已经结束。每一步对未结束的 beam 枚举所有下一个 token，把累计 log 概率加上这一步的 log 概率，然后在所有候选里全局选最好的 `width` 个。已经生成 EOS 的 beam 单独保留，不再扩展。

累计分数用 log 概率相加，直接连乘会让长序列下溢成 0。全局截断只留下固定数量候选；若每条 beam 都单独留 `width` 个，池会越来越大，也不再是同一搜索算法。

长度惩罚、EOS 和提前停止会改变最优的定义，先和面试官约定，再实现与测试。

验证时用一个小词表、可以手算的模型，把 beam 开到足够宽，和穷举结果对比。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `beam_search(next_logprobs, start, eos, width, max_new)`：从 `start` 开始最多生成 `max_new` 个 token，返回剩下的所有 beam，格式是 `[(tokens, score), ...]`，按分数降序。
- `next_logprobs(tokens)` 返回词表上 V 个已归一化的 log 概率。值为 NaN 或大于 0 时抛 `ValueError`；值为 $-\infty$ 的扩展直接丢弃。
- 每一步只扩展未结束的 beam，已生成 EOS 的 beam 原样保留。所有候选按累计 log 概率降序、token 序列升序排序，截断到 `width` 个。EOS 保留在返回的序列里，没有长度惩罚。
- `width >= 1`，`max_new >= 0`，否则抛 `ValueError`。$V \le 100$，`max_new` 不超过 30。

### 输入输出示例

词表是 {0, 1}，1 是 EOS，模型每步都给出 P(0) = 0.4、P(1) = 0.6：

```text
beam_search(model, [], eos=1, width=1, max_new=10)  -> [([1], log 0.6)]
beam_search(model, [], eos=1, width=2, max_new=2)   -> [([1], log 0.6), ([0, 1], log 0.24)]
beam_search(model, [8], eos=1, width=1, max_new=0)  -> [([8], 0.0)]
```

### 解题思路与正确性

每一步把当前所有活跃 beam 的一步扩展放进同一个候选池，再全局取前 `width` 个。已结束的 beam 也放进池里，分数不变，所以它会和新候选公平竞争，也不会在 EOS 之后继续被加分。所有 beam 都结束、或者候选池为空时提前停止。

分数用 log 概率相加，而不是概率相乘，这样长序列不会下溢。注意 beam search 在有限宽度下不保证找到全局最优序列；只有 `width` 不小于所有路径数时，它才等价于穷举，测试里最后一条就是用这个性质做对照。

### 完整参考实现（Python 3）

```python
import math


def beam_search(next_logprobs, start, eos, width, max_new):
    """逐步 beam search，返回 [(tokens, score), ...]，按分数降序。

    next_logprobs(tokens) 返回词表上每个 token 的 log 概率。
    已经生成 EOS 的 beam 不再扩展，原样参与后续排序；没有长度惩罚。
    分数相同时按 token 序列的字典序排，保证结果确定。
    """
    if width < 1:
        raise ValueError(f"width must be >= 1, got {width}")
    if max_new < 0:
        raise ValueError(f"max_new must be >= 0, got {max_new}")

    # 每个 beam 是 (tokens, 累计 log 概率, 是否已结束)
    beams = [(tuple(start), 0.0, False)]
    for _ in range(max_new):
        candidates = []
        for tokens, score, finished in beams:
            if finished:
                candidates.append((tokens, score, True))
                continue
            for token, logprob in enumerate(next_logprobs(list(tokens))):
                if math.isnan(logprob) or logprob > 1e-10:
                    raise ValueError(f"invalid log probability: {logprob}")
                if logprob == -math.inf:
                    continue  # 概率为 0 的扩展直接丢弃
                candidates.append((tokens + (token,), score + logprob, token == eos))

        # 所有候选放在一起全局截断，而不是每个 beam 各留 width 个
        candidates.sort(key=lambda beam: (-beam[1], beam[0]))
        beams = candidates[:width]
        if not beams or all(finished for _, _, finished in beams):
            break

    return [(list(tokens), score) for tokens, score, _ in beams]
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert result[0][0] == [1]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def constant_model(tokens):
    # 词表 {0, 1}，1 是 EOS；每一步 P(0) = 0.4，P(1) = 0.6
    return [math.log(0.4), math.log(0.6)]

# width = 1 时就是贪心：第一步选 EOS 后停止
result = beam_search(constant_model, [], 1, 1, 10)
assert result[0][0] == [1]
assert math.isclose(result[0][1], math.log(0.6))

# width = 2：已结束的 [1] 保留，和新扩展的 [0, 1] 一起排序
result = beam_search(constant_model, [], 1, 2, 2)
assert [tokens for tokens, _ in result] == [[1], [0, 1]]

# max_new = 0 时原样返回 start
assert beam_search(constant_model, [8], 1, 1, 0) == [([8], 0.0)]

# beam 足够宽时，2 步内的所有路径都应该出现
result = beam_search(constant_model, [], 1, 8, 2)
assert {tuple(tokens) for tokens, _ in result} == {(1,), (0, 1), (0, 0)}
```

### 复杂度与追问

设词表大小为 V，最多生成 L = `max_new` 步，宽度为 W。每一步最多产生 $W \cdot V$ 个候选，排序是 $O(WV \log(WV))$；复制 token 元组还要乘上序列长度。总时间约 $O(L \cdot WV \log(WV))$，候选池占 $O(WV \cdot L)$ 空间。排序可以换成 `heapq.nlargest`，降到 $O(WV \log W)$。

如果追问怎么加长度惩罚：把排序用的分数换成 $\text{score} / \text{len}^{\alpha}$。这会改变「最优」的定义，短序列不再天然占优，要和面试官确认用哪种归一化。

如果追问真实模型怎么做：活跃 beam 应该拼成一个 batch 一次前向，截断后按每个新 beam 的 parent 下标重排 KV cache。

## 相关题

- [[p3a-perplexity-beam-search-decoder]]：同一份练习实现，Perplexity 那边的题面是补全已有代码。
- [[coding-beam-search]]：白板版本，测试几乎相同，多了长度惩罚以及和 greedy、sampling 的对比。

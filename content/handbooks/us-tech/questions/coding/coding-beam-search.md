---
id: coding-beam-search
section: coding
order: 12
level: A
title: 白板：beam search vs greedy vs sampling，长度惩罚
quick: >-
  Greedy 每步取 $\arg\max$；beam 保留 $k$ 条前缀按累计 log-prob 扩展，$k=1$ 就是 greedy；sampling 从分布里抽。短句累计 log-prob 天生更大，要加长度惩罚。
tags:
  - 完整编程练习
  - Coding
  - Beam Search
  - Decoding
  - Anthropic
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Google's Neural Machine Translation System
    url: https://arxiv.org/abs/1609.08144
    type: primary
  - title: Generation strategies (Hugging Face)
    url: https://huggingface.co/docs/transformers/en/generation_strategies
    type: secondary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 标准库即可运行。

### 题面、接口与约束

- `beam_search(next_logprobs, start, eos, width, max_new) -> list[(tokens, score)]`：`next_logprobs(tokens)` 返回固定词表上每个 token 的 log 概率（$\le 0$，`-inf` 表示禁用）。每轮只扩展还没结束的 beam；生成 EOS 的 beam 不再扩展，但继续和其他 beam 竞争宽度。每轮按累计 log-prob 降序、token 序列字典序升序截断到 `width` 条，结果确定。`max_new = 0` 时直接返回 prompt。
- `rank_with_length_penalty(beams, prompt_length=0, alpha=0.6)`：对最终候选按 GNMT 长度惩罚重新排序。长度只算新生成的 token，包含 EOS。这只是对结果重排，不等于在搜索过程中使用长度惩罚，也不保证找到全局最优。
- `width >= 1`，`max_new >= 0`，`alpha >= 0`，否则抛 `ValueError`；log 概率为 NaN 或大于 0 时也抛 `ValueError`。

### 输入输出示例

```text
next_logprobs 恒为 log([0.4, 0.6])，eos = 1，width = 2，max_new = 2
第 1 轮：[1]（log 0.6，已结束）、[0]（log 0.4）
第 2 轮：[1] 不再扩展；[0] 扩成 [0, 1]（log 0.24）和 [0, 0]（log 0.16）
结果 -> [[1], [0, 1]]
```

### 解题思路与正确性

每个候选带着自己的 token 序列、累计分数和是否已结束。已结束的 beam 原样进入下一轮的候选池，不再调用模型，所以不会在 EOS 后面继续补 token，也不会重复加 EOS。未结束的 beam 对每个合法 token 生成一个子候选，分数在 log 域相加。

截断时用 `(-score, tokens)` 排序：分数相同时按序列字典序，保证同样的输入总得到同样的结果。所有保留的 beam 都结束时提前停止。

### 完整参考实现（Python 3）

```python
import math


def beam_search(next_logprobs, start, eos, width, max_new):
    """返回最多 width 条 (tokens, 累计 log-prob)，按分数降序、序列字典序升序。"""
    if width < 1:
        raise ValueError(f"width must be at least 1, got {width}")
    if max_new < 0:
        raise ValueError(f"max_new must be non-negative, got {max_new}")

    beams = [(tuple(start), 0.0, False)]  # (tokens, score, finished)
    for _ in range(max_new):
        candidates = []
        for tokens, score, finished in beams:
            if finished:
                candidates.append((tokens, score, True))  # EOS 之后不再扩展
                continue
            for token, logprob in enumerate(next_logprobs(list(tokens))):
                if math.isnan(logprob) or logprob > 1e-10:
                    raise ValueError(f"invalid log probability {logprob} for token {token}")
                if logprob != -math.inf:
                    candidates.append((tokens + (token,), score + logprob, token == eos))
        beams = sorted(candidates, key=lambda beam: (-beam[1], beam[0]))[:width]
        if not beams or all(finished for _, _, finished in beams):
            break
    return [(list(tokens), score) for tokens, score, _ in beams]


def rank_with_length_penalty(beams, prompt_length=0, alpha=0.6):
    """按 GNMT 长度惩罚 score / ((5 + 新 token 数) / 6) ** alpha 重新排序。"""
    if alpha < 0:
        raise ValueError(f"alpha must be non-negative, got {alpha}")

    def penalized(beam):
        tokens, score = beam
        new_length = len(tokens) - prompt_length
        return score / ((5 + new_length) / 6) ** alpha

    return sorted(beams, key=lambda beam: (-penalized(beam), beam[0]))
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError from {fn.__name__}{args}")


def fixed(seq):
    return [math.log(0.4), math.log(0.6)]


def uniform(seq):
    return [math.log(0.5)] * 2


# EOS 后不再扩展；已结束的 [1] 仍然占一个 beam 位置
results = beam_search(fixed, [], 1, 2, 2)
assert [tokens for tokens, _ in results] == [[1], [0, 1]]

# max_new = 0 直接返回 prompt
assert beam_search(fixed, [9], 1, 2, 0) == [([9], 0.0)]

# 宽度足够时保留所有路径，但 [1] 之后不会出现 [1, 1]
results = beam_search(uniform, [], 1, 8, 2)
assert {tuple(tokens) for tokens, _ in results} == {(0, 0), (0, 1), (1,)}
assert [1, 1] not in [tokens for tokens, _ in results]

# width = 1 就是 greedy
assert beam_search(fixed, [], 0, 1, 3) == [([1, 1, 1], 3 * math.log(0.6))]

# 被 -inf 禁用的 token 不会出现
results = beam_search(lambda seq: [-math.inf, 0.0], [], 5, 2, 2)
assert results == [([1, 1], 0.0)]

# 非法参数和非法 log 概率
expect_value_error(beam_search, fixed, [], 1, 0, 2)
expect_value_error(beam_search, fixed, [], 1, 2, -1)
expect_value_error(beam_search, lambda seq: [0.5, -1.0], [], 1, 2, 1)
expect_value_error(beam_search, lambda seq: [math.nan, -1.0], [], 1, 2, 1)

# 长度惩罚：累计分数相同时，长句排在前面
assert rank_with_length_penalty([([0], -1.0), ([0, 0], -1.0)])[0][0] == [0, 0]

# alpha = 0 时不惩罚，只按分数排
assert rank_with_length_penalty([([0, 0], -2.0), ([0], -1.0)], alpha=0)[0][0] == [0]
expect_value_error(rank_with_length_penalty, [([0], -1.0)], 0, -0.1)
```

### 复杂度与追问

设 $T$ 是 `max_new`，$K$ 是 `width`，$V$ 是词表大小。每轮最多 $KV$ 个候选，排序是 $O(KV\log(KV))$，总时间 $O(T\cdot KV\log(KV))$，不含模型调用本身。保存序列额外需要 $O(KT)$ 空间。

- 追问「能更快吗」：每轮不必全排序，用大小为 $K$ 的堆或 `torch.topk` 取前 $K$ 个即可，降到 $O(KV\log K)$。
- 追问「beam 一定找到最优吗」：不会。每轮剪掉的路径后面可能更好，beam 只是近似搜索。
- 追问「最后选哪一条」：这份实现把已结束和未结束的 beam 一起返回。实际使用时应先在已生成 EOS 的序列里选；只有全部顶到 `max_new` 都没有 EOS，才退回到未结束的 beam。

## 题怎么来的

解码三件套是 greedy、beam 和 sampling。Anthropic / Apple 会让你比较它们，而不是默写 `generate` 的参数。翻译、代码补全常用 beam；聊天常用温度加 nucleus，见 `coding-topk-nucleus`。长度惩罚来自 GNMT（Wu et al.）：不加惩罚，短句会占满结果。

## greedy / beam / sampling

Greedy：每步取当前条件概率最大的 token，也就是 $k=1$ 的 beam。速度快，但容易陷入循环和重复。

Sampling：从温度调整后的分布 $\pi_T$ 或 nucleus 里抽。结果多样，但没有任何搜索保证。温度、top-k、top-p 改变的是每一步的分布，不是搜索宽度。

Beam：保留 $k$ 条活跃前缀。每一步把每条前缀扩展到整个词表，累计分数是

$$
s(y_{1:t})=s(y_{1:t-1})+\log\pi(y_t\mid y_{1:t-1}),
$$

然后在 $k\cdot V$ 个候选里取前 $k$ 个。分数必须在 log 域相加，概率连乘会下溢。生成 EOS 的前缀进入已完成集合，不再扩展；没生成 EOS 的留在活跃集合。最后先在已完成的句子里比；只有全部达到 `max_len` 都没有 EOS，才退回到活跃 beam。

生产实现里每个子候选还要记 `parent`，用来复制 token 前缀和重排 KV cache。如果 cache 不按 parent gather，子节点读到的就是别的 beam 的历史。batch 内各样本的 beam 互相独立，pad 位置不要扩展。

## 长度惩罚：短句的 log-prob 和更大

$\sum\log\pi$ 每多一个 token 就更负一点，所以短句往往分数更高。GNMT 用下面的分数做归一化：

$$
\mathrm{score}(y)=\frac{1}{\bigl((5+|y|)/6\bigr)^\alpha}\sum_t\log\pi(y_t\mid y_{1:t-1}),
$$

$|y|$ 是生成长度，$\alpha$ 常取 $0.6$ 到 $1$，$\alpha=0$ 等于不惩罚。EOS 之后停止扩展，也能避免“再补几个 token 刷分”。重复 n-gram 屏蔽和坏 token mask 要在打分之前加上。

如果 beam 的每一步先做 nucleus 截断，分布就变了，不再是经典 beam search。面试先写标准 beam。产品上聊天很少用 beam，翻译和结构化输出才值得。Apple 端侧场景下 $k>1$ 意味着逐 token 生成（decode）时读 KV 的带宽乘以 $k$，GQA 能把这部分省回来一些，见 `meta-llama-gqa`。

## 追问

- **为什么不用概率相乘？** 长序列下概率会下溢成 0。log 域相加数值稳定，也和交叉熵损失（CE）里的 log-softmax 一致。
- **最终为什么不看活跃集合？** 没生成 EOS 的前缀和已完成的句子不可比。只有一个完成句都没有时才退回活跃集合。
- **$k$ 越大一定越好吗？** 不一定。$k$ 大时结果更偏短、更千篇一律，还需要长度惩罚和多样性约束；KV 带宽也随 $k$ 增长。

## 相关题

- [[p3a-microsoft-beam-search-decoder]]：Microsoft 题面，测试和本卡几乎一样，但契约里没有长度惩罚。
- [[p3a-perplexity-beam-search-decoder]]：Perplexity 题面是在已有代码上补全，重点是停止条件，同样不含长度惩罚。
- [[coding-topk-nucleus]]：采样那一支怎么写：温度、top-k、nucleus 的顺序和边界。

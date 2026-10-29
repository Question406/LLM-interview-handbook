---
id: p3a-perplexity-byte-tokenizer-and-token-count-estimator
section: design
order: 611
level: S
title: Perplexity：Byte Tokenizer：等价优化与计数估计
quick: >-
  先读准慢参考实现的字节编码、合并优先级和并列规则，再用链表加堆优化并与参考做差分测试；token 数估计靠随机窗口 sampling，要说明 window
  boundaries 带来的偏差。
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · Perplexity · byte-tokenizer-and-token-count-estimator
    url: >-
      https://www.1point3acres.com/interview/problems/company/perplexity/byte-tokenizer-and-token-count-estimator
    type: secondary
---

## 题目描述

实现一个字节级 BPE tokenizer，并在字符编码预算有限时估算长文本的 token 数。编码和 decoding 必须保留多字节 Unicode 文本。

以下为手册重构练习约定。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `encode(text, merges) -> list[bytes]`：字节级 BPE。先把文本按 UTF-8 编码，每个字节是一个初始 token。`merges` 是按优先级从高到低排列的 `(左, 右)` bytes 对，不能重复，也不能含空 bytes。每轮在所有相邻对里找优先级最高的（同优先级取最左），只合并这一对，然后重新找，直到没有可合并的对。
- `decode(tokens) -> str`：拼接所有 bytes，按 UTF-8 严格 decoding。
- `estimate(text, merges, budget, rng) -> (估计值, 实际编码的字符数)`：最多编码 `budget` 个字符。文本不超过预算时精确计算；否则随机取若干个长度为 $\min(32, budget)$ 的字符窗口，用平均「token 数 / 字符数」乘以总字符数。这个估计不是无偏的。
- 文本不超过 $10^4$ 个 UTF-8 字节。
- budget 为正整数，按 Python 字符数计而不是 UTF-8 字节数；rng 为注入的 Python random.Random。窗口起点在所有可取字符窗口内均匀抽样；总编码字符数不得超过 budget。空文本精确返回 (0.0,0)。
- 长文本固定取 floor(budget/min(32,budget)) 个窗口，窗口可重叠或重复，按抽样顺序调用 rng.randrange；实际编码字符数是窗口数乘窗口长度。

### 输入输出示例

```text
merges=[(b"a",b"b"),(b"ab",b"ab")]
encode("abab",merges) -> [b"abab"]
encode("aaa",[(b"a",b"a")]) -> [b"aa",b"a"]
decode(encode("你好🙂",merges)) -> "你好🙂"
estimate("abab",merges,budget=4,rng=任意给定随机源) -> (1.0,4)
```

## 解题思路与参考答案

## 题目

给一份很慢的字节级 tokenizer 参考实现，先读懂它，再写一个输出完全相同但更快的版本。然后在只能处理有限文本量（预算）的条件下，估计一段长文本的 token 数。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

## 思路

我会先固定参考实现的字节编码、合并优先级和并列规则，再用链表加堆优化，并持续做差分测试。比如同一对在多个位置都能合并，必须和参考实现一样取最左边；换了顺序，即使 decoding 仍能还原原文，token 序列也可能不同。

优化时，每改一步都拿参考实现做差分测试：对大量随机输入和 edge-case inputs，比较两个版本的输出是否逐字节相同。

常见的加速做法是用双向链表存 token、用优先队列存候选的相邻对。每次弹出优先级最高的一对合并，再把新产生的相邻对加入队列。难点在于合并之后，堆里还留着一些已经不存在的旧候选对，弹出时要检查它是否仍然有效。

估计 token 数时，随机抽几个文本窗口编码，算出平均每个字符多少 token，再乘以总字符数。要说明这个估计的偏差：window boundaries 会切断本来能跨 window boundaries 合并的 token，估计值往往偏高。不能为了绕开预算，在估计函数里偷偷编码全文。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `encode(text, merges) -> list[bytes]`：字节级 BPE。先把文本按 UTF-8 编码，每个字节是一个初始 token。`merges` 是按优先级从高到低排列的 `(左, 右)` bytes 对，不能重复，也不能含空 bytes。每轮在所有相邻对里找优先级最高的（同优先级取最左），只合并这一对，然后重新找，直到没有可合并的对。
- `decode(tokens) -> str`：拼接所有 bytes，按 UTF-8 严格 decoding。
- `estimate(text, merges, budget, rng) -> (估计值, 实际编码的字符数)`：最多编码 `budget` 个字符。文本不超过预算时精确计算；否则随机取若干个长度为 $\min(32, budget)$ 的字符窗口，用平均「token 数 / 字符数」乘以总字符数。这个估计不是无偏的。
- 文本不超过 $10^4$ 个 UTF-8 字节。

### 输入输出示例

```text
merges = [(b"a", b"b"), (b"ab", b"ab")]
encode("abab", merges)                 -> [b"abab"]      # 先合并成 ab ab，再合并成 abab
encode("aaa", [(b"a", b"a")])          -> [b"aa", b"a"]  # 同优先级取最左
decode(encode("你好🙂", merges))         -> "你好🙂"
```

### 解题思路与正确性

`encode` 直接实现慢参考的语义：每轮重新扫描所有相邻对，取 `(rank, 位置)` 最小的合并。因为每次合并 token 数减一，循环最多执行「字节数 - 1」次。

合并只拼接 bytes，不改变字节内容和顺序，所以 `decode` 一定能还原原文，即使中间某个 token 只包含一个多字节字符的一部分。

`estimate` 复用同一个 `encode`，不另写一份 tokenizer 逻辑。代价是 window boundaries 会阻断跨窗口的合并，结果有偏差；函数同时返回实际编码的字符数，调用方可以确认预算没有超出。

### 完整参考实现（Python 3）

```python
import random


def encode(text, merges):
    """字节级 BPE。merges 按优先级从高到低排列，每轮只合并一对。

    每轮在所有相邻 token 对里找 rank 最小的（相同 rank 取最左），合并后重新找，
    直到没有可合并的对。返回 bytes token 列表。
    """
    ranks = {pair: rank for rank, pair in enumerate(merges)}
    if len(ranks) != len(merges):
        raise ValueError("merges must not contain duplicates")
    if any(not left or not right for left, right in merges):
        raise ValueError("merge parts must be non-empty bytes")

    tokens = [bytes([byte]) for byte in text.encode("utf-8")]
    while True:
        candidates = [
            (ranks[(tokens[i], tokens[i + 1])], i)
            for i in range(len(tokens) - 1)
            if (tokens[i], tokens[i + 1]) in ranks
        ]
        if not candidates:
            return tokens
        _, i = min(candidates)  # 先比 rank，再比位置
        tokens[i : i + 2] = [tokens[i] + tokens[i + 1]]


def decode(tokens):
    """拼回字节后按 UTF-8 严格 decoding。"""
    return b"".join(tokens).decode("utf-8")


def estimate(text, merges, budget, rng):
    """最多编码 budget 个字符，估计整段文本的 token 数。返回 (估计值, 实际编码的字符数)。

    文本不超过预算时直接精确计算；否则随机取若干个固定长度的字符窗口，
    用平均「token 数 / 字符数」乘以总字符数。窗口边界会切断跨窗口的合并，
    所以这个估计有偏差（通常偏高）。
    """
    if budget < 1:
        raise ValueError(f"budget must be at least 1: {budget}")
    if not text:
        return 0.0, 0
    if len(text) <= budget:
        return float(len(encode(text, merges))), len(text)

    window = min(32, budget)
    sampled_chars = 0
    sampled_tokens = 0
    while sampled_chars + window <= budget:
        start = rng.randrange(len(text) - window + 1)
        sampled_tokens += len(encode(text[start : start + window], merges))
        sampled_chars += window
    return sampled_tokens / sampled_chars * len(text), sampled_chars
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert encode("abab", merges) == [b"abab"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
merges = [(b"a", b"b"), (b"ab", b"ab")]

# 先合并 a+b，再合并 ab+ab
assert encode("abab", merges) == [b"abab"]

# 编码再 decoding 要还原原文，包括多字节字符和 emoji
for text in ("", "hello", "你好🙂", "abab"):
    assert decode(encode(text, merges)) == text

# 相同 rank 取最左：aaa 只能合并前两个
assert encode("aaa", [(b"a", b"a")]) == [b"aa", b"a"]

# 文本不超过预算时精确计数
assert estimate("abab", merges, 4, random.Random(1)) == (1.0, 4)

# 超过预算时只编码不超过 budget 个字符
estimated, sampled = estimate("abab" * 100, merges, 100, random.Random(3))
assert estimated > 0
assert sampled <= 100

# 非法 merges
try:
    encode("a", [(b"a", b"b"), (b"a", b"b")])
except ValueError:
    pass
else:
    raise AssertionError("duplicate merges should be rejected")
```

### 复杂度与追问

设 UTF-8 字节数为 n。最多合并 n - 1 次，每次扫描 O(n) 个相邻对，每次比较或拼接 bytes 的代价和 token 长度有关，所以慢参考最坏是 $O(n^2)$ 次扫描操作再乘以 bytes 比较的成本。空间是 O(n + 合并规则数)。

**怎么做得更快？**
用双向链表存 token，用最小堆存 `(rank, 位置, 左右节点)` 候选。合并后把新的左右邻对加入堆；弹出时检查两个节点是否仍然存在且仍然相邻，失效的直接丢弃。这样每次合并是 O(log n)，总体 $O(n \log n)$。改完要和慢参考做逐输入的差分测试。
**预算按字符还是按字节算？**
这里按字符。如果面试要求按字节预算，切窗口时要保证不把一个多字节字符切成两半，否则单独编码这个窗口时会多出不完整的字节，需要另外约定安全的切分方式。

## 相关题

- [[anthropic-bpe-tokenizer]]：几乎同一题，合并优先级、最左并列、往返和预算计数的测试都一样，另外讲了 BPE 训练和 merge 表从哪来。
- [[coding-bpe-merge]]：训练端的一步 merge，可以和这里的 encode 对照。
- [[openai-tiktoken]]：生产里的字节级 BPE 在合并前还有正则预分词和特殊 token，这份练习没有这两层。

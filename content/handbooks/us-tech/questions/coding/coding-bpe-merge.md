---
id: coding-bpe-merge
section: coding
order: 7
level: A
title: 白板：BPE 训练一步 merge，词表膨胀；词尾标记写成 endofword 禁止 XML
quick: >-
  统计相邻 pair 频次，合并最高频的一对，词表加 1；训练每轮重数频次，encode 只按顺序回放 merge 表。词尾写成 `endofword`，不用 XML 标签。
tags:
  - 完整编程练习
  - Coding
  - BPE
  - Tokenizer
  - Anthropic
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Neural Machine Translation of Rare Words with Subword Units
    url: https://arxiv.org/abs/1508.07909
    type: primary
  - title: tiktoken
    url: https://github.com/openai/tiktoken
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题或官方测试。Python 3 标准库。

### 题面、接口与约束

- `bpe_one_merge(corpus, merges) -> (new_corpus, new_merges)`：做一步 BPE 训练。
- `corpus` 是若干个 token 列表（`list[list[str]]`），词尾已经是 `endofword`；同一个词出现几次，就有几个列表。`merges` 是已经发生的有序 merge 表。
- 计数：统计每个列表内部的相邻 pair 频次，不跨列表。频次相同时，选 token 对按字典序**较大**的那个。
- 合并：选出一个 pair 后，每个列表从左到右做非重叠替换。
- 返回新的 corpus，和在末尾追加了这个 pair 的新 merges；不修改输入。如果没有任何相邻 pair（每个列表都只有一个 token），原样返回输入的两个对象。

### 输入输出示例

```text
bpe_one_merge([["a", "a", "a"]], [])  -> ([["aa", "a"]], [("a", "a")])
# (a, a) 计数为 2，但替换是非重叠的：合并前两个后，第三个 a 没有右邻居

bpe_one_merge([["a", "b"], ["b", "c"]], [])  -> ([["ab"], ["bc"]], [("b", "c")])
# 两个 pair 都出现 1 次，按字典序较大者 ("b", "c") 优先
```

### 解题思路与正确性

计数时重叠的 pair 都要算进去：`a a a` 里有两个 `(a, a)`。但替换必须是非重叠的，从左往右扫，命中就合并并跳过两个位置，否则一个 `a` 会被用两次。

`max` 的 key 是 `(频次, pair)`，频次相同就比较 pair 本身，tie-break 是确定的，同样的输入每次都得到同样的 merge 表。

函数每次都构造新列表，`merges` 也用 `list(merges) + [...]` 生成新列表，所以调用方的输入不会被改动。

### 完整参考实现（Python 3）

```python
from collections import Counter


def bpe_one_merge(corpus, merges):
    """做一步 BPE 训练：合并最高频的相邻 pair，返回 (new_corpus, new_merges)。

    corpus: list[list[str]]，词尾已是 "endofword"；merges: 已发生的有序 merge 表。
    频次相同时选字典序较大的 pair；不修改输入。
    """
    pair_counts = Counter()
    for tokens in corpus:
        pair_counts.update(zip(tokens, tokens[1:]))
    if not pair_counts:
        return corpus, merges

    left, right = max(pair_counts, key=lambda pair: (pair_counts[pair], pair))
    merged = left + right
    new_corpus = []
    for tokens in corpus:
        index = 0
        output = []
        while index < len(tokens):
            if index + 1 < len(tokens) and tokens[index] == left and tokens[index + 1] == right:
                output.append(merged)
                index += 2  # 非重叠：跳过已合并的两个 token
            else:
                output.append(tokens[index])
                index += 1
        new_corpus.append(output)
    return new_corpus, list(merges) + [(left, right)]
```

### 可执行测试

```python
# 重叠 pair：计数为 2，但只合并前两个；不修改输入
corpus = [["a", "a", "a"]]
merges = []
output, new_merges = bpe_one_merge(corpus, merges)
assert output == [["aa", "a"]]
assert new_merges == [("a", "a")]
assert corpus == [["a", "a", "a"]]
assert merges == []

# 没有任何相邻 pair：原样返回
output, new_merges = bpe_one_merge([["a"], ["b"]], [])
assert output == [["a"], ["b"]]
assert new_merges == []

# 频次相同时选字典序较大的 pair
output, new_merges = bpe_one_merge([["a", "b"], ["b", "c"]], [])
assert new_merges == [("b", "c")]
assert output == [["a", "b"], ["bc"]]

# 频次优先于字典序；pair 不跨列表统计
output, new_merges = bpe_one_merge([["x", "y"], ["x", "y"], ["y", "z"]], [])
assert new_merges == [("x", "y")]
assert output == [["xy"], ["xy"], ["y", "z"]]
output, new_merges = bpe_one_merge([["a", "b"], ["c", "d"]], [])
assert ("b", "c") not in new_merges

# 已有的 merge 表在末尾追加；四个 a 合成两个 aa
output, new_merges = bpe_one_merge([["a", "a", "a", "a", "endofword"]], [("q", "r")])
assert output == [["aa", "aa", "endofword"]]
assert new_merges == [("q", "r"), ("a", "a")]
```

### 复杂度与追问

设语料的 token 总数为 n，不同的相邻 pair 数为 P。一轮计数和替换都是 O(n)，pair 计数表占 O(P)。

- 追问「训练很多轮太慢」：每轮都重扫全语料，总代价是 O(n × merge 次数)。生产实现用堆存 pair 频次，再用倒排索引记录每个 pair 出现在哪些位置，合并后只更新被碰到的邻居 pair。
- 追问「同一个词出现很多次」：把语料压成 `词 -> 次数`，计数时乘上次数，不用把重复的词展开成多个列表。

## 题怎么来的

Sennrich et al. 2016 提出的 BPE 是 GPT / Claude 词表的前身。Anthropic 公开题库里有手写 tokenizer 的题；OpenAI 的 coding 环节也会问一步 merge 到底发生了什么。要讲清楚三件事：训练时合并谁、词表怎么增长、encode 为什么不能每步重新数频次。完整的 encode/decode 不变量见 `anthropic-bpe-tokenizer`。

白板上不要把词尾标记写成 XML 标签，手册的构建器会把它当成 HTML 吞掉；写成 `endofword` 或「词尾标记」。

## 一步 merge：数 pair、合最高频、词表 +1

语料先切成符号序列。字符级 BPE 从单个字符出发，每个词末尾贴一个 `endofword`，这样 `cat` 和 `cater` 的前缀不会混在一起统计。字节级 BPE 从 0–255 这 256 个字节出发，任何输入都能表示，所以没有 unk。每一步做三件事：

1. 统计所有相邻 pair 的频次（同一个词出现 $n$ 次，它的 pair 就乘以 $n$）；
2. 选频次最高的 pair，平手时要有确定的 tie-break，比如字典序；
3. 把这个 pair 合成一个新符号，词表大小加 1，并记下这次 merge 的顺序。

同一个 pair 在不同轮的频次会变，因为上一轮的合并改变了它的邻居。所以每轮都要重数，不能拿初始的 pair 表一路合到底。达到目标词表大小或 merge 次数时停止。最终词表 = 基础符号 ∪ 每次 merge 产生的新符号。

## Encode 不是再训练一遍

上线后没有语料频次，只有一张冻结的 merge 表。Encode 的做法是：把词拆成基础符号，按训练时的 merge 顺序能合就合，直到没有任何一条 merge 能命中。常见的误区是在当前序列上每步重新找频次最高的 pair，那是在训练，不是 encode。

在训练字符集上，`decode(encode(s))` 必须等于 `s`。空格规则要前后对称：GPT-2 把前导空格当成 token 的一部分，`"a b"` 和 `"ab"` 不能编成同一串 id。词表 id 一旦对外发布，重新训练时就不能打乱顺序，除非同时保存新旧 id 的映射。

## 追问

- **词表为什么会膨胀？** 每 merge 一次就多一个符号。目标 50k 的词表 ≈ 基础符号数 + merge 次数，并不是把整词全塞进去。
- **WordPiece / Unigram 有什么不同？** WordPiece 按合并后的似然增益选 pair；Unigram 是子词级的语言模型，从大词表往下剪。BPE 是确定性地按频次 merge。Claude 和 GPT 都属于 BPE 家族。
- **为什么要词尾标记？** 没有它，词中间的 `st` 和词尾的 `st` 会共享统计；逐 token 解码时也分不清词的边界。写成 `endofword`，不要用 XML。

## 相关题

- [[anthropic-bpe-tokenizer]]：训练之后的 encode / decode：按 merge 表顺序回放，保证往返不变。
- [[p3a-perplexity-byte-tokenizer-and-token-count-estimator]]：字节级 BPE encode 的优化版，用链表加堆代替每轮重新扫描。
- [[p3a-anthropic-coding-q6-tokenizer]]：最长匹配切词，不需要 merge 表，和 BPE 的切法不同。

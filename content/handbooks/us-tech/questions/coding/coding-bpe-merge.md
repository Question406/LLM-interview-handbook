---
id: coding-bpe-merge
section: coding
order: 7
level: A
title: 白板：BPE 训练一步 merge，词表膨胀；词尾标记写成 endofword 禁止 XML
quick: >-
  统计相邻 pair 频次，合并最高频那一对，词表加 1。训练要重数频次；encode 只回放有序 merge 表。词尾写成
  `endofword`，不要写成任何 XML 标签。
tags:
  - Coding
  - BPE
  - Tokenizer
  - Anthropic
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Neural Machine Translation of Rare Words with Subword Units
    url: https://arxiv.org/abs/1508.07909
    type: primary
  - title: tiktoken
    url: https://github.com/openai/tiktoken
    type: primary
---

## 题怎么来的

Sennrich et al. 2016 的 BPE 是 GPT / Claude 词表的祖先。Anthropic 公开题库有手写 tokenizer；OpenAI 也会在 coding 里问 merge 一步发生了什么。要说清：训练时合并谁、词表怎么长、encode 为什么不能每步重新数频次。完整 encode/decode 不变量见 `anthropic-bpe-tokenizer`。白板禁止写 XML 词尾标签，构建器会当成 HTML；写成 `endofword` 或「词尾标记」。

## 一步 merge：数 pair、合最高频、词表 +1

语料先切成符号序列。字符级从字符出发，词尾贴 `endofword`，避免 `cat` 和 `cater` 的前缀糊在一起。字节级从 0-255 出发，没有 unk。每一步：

1. 统计所有相邻 pair 的频次（同一词出现 $n$ 次就乘 $n$）；
2. 取频次最高的 pair，平手要有确定的 tie-break（字典序）；
3. 把该 pair 合成新符号，词表大小加 1，记下这次 merge 的顺序。

同一个 pair 在不同轮的频次会变，因为上一轮合并改了邻居。必须重数，不能拿初始 pair 表一路合到底。停在目标词表或 merge 次数。词表 = 基础符号 ∪ 每次 merge 产生的新符号。

```python
from collections import Counter

def bpe_one_merge(corpus, merges):
    # corpus: list[list[str]], 词尾已是 "endofword"
    # merges: 已发生的有序 merge 表
    pairs = Counter()
    for seq in corpus:
        pairs.update(zip(seq, seq[1:]))
    if not pairs:
        return corpus, merges
    a, b = max(pairs, key=lambda p: (pairs[p], p))
    token = a + b
    nxt = []
    for seq in corpus:
        i, out = 0, []
        while i < len(seq):
            if i + 1 < len(seq) and seq[i] == a and seq[i + 1] == b:
                out.append(token)
                i += 2
            else:
                out.append(seq[i])
                i += 1
        nxt.append(out)
    merges.append((a, b))
    return nxt, merges
```

朴素一步 $O(\text{tokens})$。生产会用堆 + 倒排只更新被碰到的邻居；白板先写对暴力版。

## Encode 不是再训练一遍

上线没有语料频次，只有冻结的 merge 表。Encode：把词拆成基础符号，按训练时的 merge 顺序能合就合，直到一轮都不命中。常见错法：每步在当前序列上重新找频次最高的 pair，那是训练，不是 encode。

`decode(encode(s))` 在训练字符集上要可逆。空格规则必须对称：GPT-2 用前导空格当独立信息，不要把 `"a b"` 和 `"ab"` 编成同一串 id。词表 id 一旦发出去就不能在新训练里洗牌还不存 mapping。

## 追问

- **词表为什么膨胀？** 每 merge 一次多一个符号。目标 50k 词表 ≈ 基础符号数 + merge 次数。不是把整词全塞进去。
- **WordPiece / Unigram？** WordPiece 用似然增益；Unigram 是子词语言模型。BPE 是确定性 merge。Claude / GPT 都是 BPE 家族。
- **为什么要词尾标记？** 没有它，词中的 `st` 和词尾的 `st` 会共享统计，decode 也分不清词边界。写成 `endofword`，不要用 XML。

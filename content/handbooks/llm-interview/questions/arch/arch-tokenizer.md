---
id: arch-tokenizer
section: arch
order: 15
level: A
title: BPE、WordPiece、SentencePiece、Byte-level BPE 大致区别？
quick: >-
  BPE 反复合并语料里最高频的相邻符号，WordPiece 按似然增益选合并，两者都是学 vocabulary 的算法。SentencePiece
  是直接拿原始文本训练 tokenizer 的工具框架，里面可以跑 BPE 或 Unigram；byte-level BPE 从字节起步，所以几乎没有
  vocabulary 外字符（OOV）。
tags:
  - Tokenizer
  - Basics
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Neural Machine Translation of Rare Words with Subword Units (BPE)
    url: 'https://arxiv.org/abs/1508.07909'
    type: primary
  - title: SentencePiece
    url: 'https://arxiv.org/abs/1808.06226'
    type: primary
---

这四个名字不在一个层次上。BPE、WordPiece、Unigram 是学 vocabulary 的算法；SentencePiece 是一个可以直接在 raw text 上训练的工具箱，里面能跑 BPE 或 Unigram，并且把空格当普通符号；byte-level BPE 还是 BPE，只是起点换成了字节。所以别把 SentencePiece 说成一种独立的 merge 目标，也别说 byte-level BPE 和 BPE 完全不是一类。

比如一段中文本来没有空格，用 SentencePiece 就不需要先分词，直接吃原始文本训练，空格本身会变成 `▁` 一类的符号，中日韩文本都能这么处理。

## 各自怎么学 vocabulary

BPE 从字符（或字节）出发，反复合并语料里出现最频繁的相邻 pair，直到 vocabulary 达到目标大小，decoding 时按学到的 merge 表贪心切分。WordPiece（BERT 系）挑候选 merge 时看的是语言模型的似然增益，裸频率高不一定被选，所以它的切分更偏向让整句概率变大。Unigram LM 反过来，先给一个过大的 vocabulary，再按损失剪枝。

Byte-level BPE（GPT-2 系）从 $256$ 个 byte 起步，任何 Unicode 都能落到 byte 上，几乎没有 OOV。代价是某些语言、特殊符号、带声调的字符会被拆得更碎，同样一句话，$T$ 更长。

## 为什么还要管 tokenizer

因为 $T$ 直接乘进 attention 的 $O(T^2 d)$ 和 KV cache。中文 vocabulary 切得过碎，同样 8k 的上下文装下的「话」就更少；切得过粗，稀有实体、代码、数字会粘在一起，编辑距离式的纠错和 MoE 路由都会变难。训练和推理必须用同一套 tokenizer：多一个 BOS，或者空格规范化不一样，RoPE 的位置 $m$ 就会整体错位，$\langle R_m q,R_n k\rangle$ 对应的就不是同一个相对距离了。

至于和架构公式的关系，SwiGLU、RMSNorm 都不关心 vocabulary，它们吃的是 embedding 之后的 $x$。vocabulary 大小只影响 embedding / lm_head 那个 $V\times d$ 矩阵的显存。

## 追问

**中文用字表还是用 BPE？**
现在的大模型多用 byte-level 或 SentencePiece BPE 的多语 vocabulary。纯字表序列短、OOV 少，但英文和代码会变差。选哪种，用 $T$ 和下游效果一起验收。

**为什么数字会被拆开？**
byte 级或字符级切分里很常见。想让算数稳定，要加专门的数字规则，或者靠后训练。

**换了 tokenizer，能直接继续预训练吗？**
一般不行。要重做 embedding 对齐，或者重新训，光改配置文件没用。

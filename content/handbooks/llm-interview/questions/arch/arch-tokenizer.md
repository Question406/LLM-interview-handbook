---
id: arch-tokenizer
section: arch
order: 15
level: A
title: BPE、WordPiece、SentencePiece、Byte-level BPE 大致区别？
quick: >-
  BPE 迭代合并高频 symbol pairs；WordPiece 选择更偏 likelihood 增益的 subword；SentencePiece
  是可直接在 raw text 上训练的 tokenizer framework；byte-level BPE 从 bytes 出发，几乎无 OOV。
tags:
  - Tokenizer
  - Basics
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Neural Machine Translation of Rare Words with Subword Units (BPE)
    url: https://arxiv.org/abs/1508.07909
    type: primary
  - title: SentencePiece
    url: https://arxiv.org/abs/1808.06226
    type: primary
---

这块容易把 SentencePiece 说成一种独立的 merge 目标，或把 byte-level BPE 说成「和 BPE 完全不是一类」。面试先分清：BPE / WordPiece / Unigram 是学词表的算法；SentencePiece 是可在 raw text 上训练的工具箱，里面能跑 BPE 或 Unigram，并把空格当普通符号。

## 四种东西各管什么

BPE：从字符（或字节）出发，反复合并语料里出现最频繁的相邻 pair，直到词表到目标大小。解码按学到的 merge 表贪心。WordPiece（BERT 系）：候选 merge 看的是语言模型似然增益，而不是裸频率，所以切分更偏「让整句概率变大」。Unigram LM：先给一个过大词表，再按损失剪枝。SentencePiece：直接吃未预分词文本，空格变成 `▁` 一类符号，中日韩不必先分词。

Byte-level BPE（GPT-2 系）从 $256$ 个 byte 起步，任意 Unicode 都能落到 byte，几乎无 OOV。代价是某些语言、特殊符号、带调字符会拆得更碎，同样一句话 $T$ 更长。

## 为什么还要管 tokenizer

$T$ 直接乘进注意力 $O(T^2 d)$ 和 KV cache。中文词表过碎，同样 8k 上下文装下的「话」更少；过粗则稀有实体、代码、数字粘在一起，编辑距离式纠错和 MoE 路由都会变难。训推必须用同一套 tokenizer：多一个 BOS、空格规范化不同，RoPE 位置 $m$ 会整体错位，$\langle R_m q,R_n k\rangle$ 对的就不是同一相对距离。

和架构公式的关系：SwiGLU / RMSNorm 不关心词表；它们吃的是 embedding 后的 $x$。词表大小只影响 embedding / lm_head 的 $V\times d$ 矩阵显存。

## 追问

- **中文用字还是用 BPE？** 纯字表短、OOV 少，但英文和代码变差；现行大模型多用 byte-level 或 SentencePiece BPE 的多语词表，用 $T$ 和下游一起验收。
- **为什么数字会被拆开？** byte / 字符级切分常见；要稳定算数需专门数字规则或后训练。
- **换 tokenizer 能否直接继续预训练？** 一般要重做 embedding 对齐或重新训，不能只改配置文件。

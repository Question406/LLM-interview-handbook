---
id: anthropic-bpe-tokenizer
section: anthropic
order: 2
level: A
title: Anthropic：手写 BPE Tokenizer，encode / decode 要对齐什么不变量？
quick: >-
  训练：反复合并频次最高的相邻 pair，得到有序 merge 表。Encode：先拆成字符或预分词，再按 merge
  优先级扫到不能再合。Decode：id 映回 token 字符串再拼接。不变量是
  `decode(encode(s))` 对训练字符集可逆；字节级 BPE 还要对任意 utf-8 可逆。
tags:
  - Anthropic
  - Tokenizer
  - BPE
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Anthropic Coding Interview Questions (LinkJob)
    url: https://www.linkjob.ai/interview-questions/anthropic-coding-interview/
    type: secondary
  - title: Neural Machine Translation of Rare Words with Subword Units (BPE)
    url: https://arxiv.org/abs/1508.07909
    type: primary
  - title: tiktoken
    url: https://github.com/openai/tiktoken
    type: primary
---

## 真题记录

- 公司：Anthropic
- 岗位：SWE 编码题库中的 Tokenizer 题（公开复盘把其列为题库第六题）
- 来源：LinkJob 对近两年面经的汇总；实现细节以 Sennrich BPE 和字节级 BPE 为准

Anthropic 要的是 merge 表怎么用、空格和字节怎么处理、encode 是否稳定，不是调库。

## 训练：pair 计数 + 有序列表

语料先切成符号序列。字符级 BPE 从字符出发；GPT-2 式字节级从 0–255 出发，避免 unk。反复：

1. 统计相邻 pair 频次；
2. 合并最高频 pair 成新符号；
3. 记下这次 merge。

停止条件：词表大小或 merge 次数。词表 = 基础符号 ∪ merge 产生的符号。优先级就是 merge 发生的顺序，不是字母序。

面试别漏：**同一个 pair 在不同轮的频次会变**，因为上一轮合并改了邻居。必须重数，不能用初始 pair 表一路合到底。

## Encode：按 merge 顺序，不是每次贪心最高频

正确做法是把 merge 列表当成优先队列：只应用训练时出现过的 pair，且按训练顺序。伪代码：把词拆成符号数组，扫描 merge 表，能合就合，直到一轮都没有命中。

常见错法：每步在当前序列上重新找频次最高的 pair。那是训练，不是 encode。上线没有语料频次，只有冻结的 merge 表。

特殊符号：词尾标记（BPE 论文里常写成 end-of-word）或空格当独立符号。GPT-2 用 `Ġ` 表示前导空格。空格规则必须和 decode 对称，否则 `encode("a b")` 和 `encode("ab")` 会糊在一起。

## Decode 与不变量

id → token 字符串，拼接。字节级要把 latin-1 字节映回 utf-8，非法 utf-8 要有替换策略，面试说「替换字符 / 抛错」即可。

不变量：

- 训练集字符上 `decode(encode(s)) == s`；
- 同一 merge 表，encode 确定性；
- 词表 id 稳定，不能每次训练重新洗 id 还不存 mapping。

复杂度：朴素 encode 每个 token $O(T\cdot M)$，$M$ 是 merge 数。生产用 trie / 预分词 + 查表（tiktoken 那类）。白板先写对朴素版，再提加速。

## 追问

- **WordPiece / Unigram 差在哪？** WordPiece 用似然增益；Unigram 是子词概率模型。BPE 是确定性 merge。Claude / GPT 词表都是 BPE 家族，不是 WordPiece。
- **为什么字节级？** 任意 utf-8 可表示，没有 unk，多语言和乱码不会炸。
- **和 embedding 矩阵的关系？** `vocab_size` 必须等于 embedding 行数。扩词表要扩 embedding 和 lm_head，并处理新 id 的初始化。见 `arch-tokenizer`。

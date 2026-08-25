---
id: openai-tiktoken
section: openai
order: 21
level: A
title: OpenAI：tiktoken / BPE 和 SentencePiece 差在哪，特殊 token 和词表怎么扩
quick: >-
  两边都可以是 BPE，差在预分词。tiktoken 先用正则切块再按有序 merge 表合；SentencePiece 常把空格当普通字符
  （码点 U+2581），也可走 Unigram。特殊 token 不进 merge，encode 时单独查表。扩词表是加行到 $[V, D]$，不是改已有
  merge 的语义。
tags:
  - OpenAI
  - tiktoken
  - BPE
  - Tokenizer
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: openai/tiktoken
    url: https://github.com/openai/tiktoken
    type: primary
  - title: Neural Machine Translation of Rare Words with Subword Units
    url: https://arxiv.org/abs/1508.07909
    type: primary
  - title: SentencePiece — A simple and language independent subword tokenizer
    url: https://arxiv.org/abs/1808.06226
    type: primary
  - title: Language Models are Unsupervised Multitask Learners
    url: https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
    type: primary
---

## 题怎么来的

OpenAI 的公开分词器是 tiktoken：Rust 核、Python 包装，编码名 `r50k_base` / `p50k_base` / `cl100k_base` / `o200k_base`。Anthropic 编码轮会手写 BPE，见 `anthropic-bpe-tokenizer` 和 `coding-bpe-merge`。OpenAI 研究岗更常问：**和 SentencePiece 到底差哪一步、特殊 token 为什么不会被 BPE 拆掉、上新工具标记时 embedding 怎么长**。词尾标记写成 `endofword`，不要写成 XML 闭合标签，构建器会当成 HTML。

## 算法可以相同，预分词不同

Sennrich BPE：从字符（或已标词尾的词内字符）出发，反复合并最高频相邻 pair，得到 **有序 merge 表**。Encode 是回放这张表，不是每句话重新数频次。GPT-2 / tiktoken 的字节级 BPE 把原始字节先可逆映射到 unicode 码点，再 BPE，任意 utf-8 都能 round-trip，没有 unk。

关键差别在 BPE **之前**：

- **tiktoken / GPT-2。** 正则预分词先切出「单词块 / 数字块 / 标点块」，再在块 **内部** merge。空格常附着在后一块上。跨块的 pair 根本不会合，所以 `hello` 和前面带空格的 `hello` 可以是两个 id。这是有意的：空格变成特征，而不是被吃进字母。
- **SentencePiece。** 默认把整句当 unicode 序列，空格变成普通符号（U+2581），不依赖语言特定正则。算法可以是 BPE 或 Unigram LM。Unigram 是另一套：维护一个很大的候选词表，用 EM 丢概率低的片，decode 是 Viterbi，不是按 merge 优先级扫。把 SentencePiece 说成「就是 tiktoken」会在这一步翻车。

`cl100k_base`（GPT-3.5 / GPT-4）和 `o200k_base`（GPT-4o）是不同 merge 表和不同预分词，压缩率、多语言、空白处理都不一样。不要拿 GPT-2 的 50k 词表去估 4o 的上下文 token 数。计费和上下文窗口都是 **tiktoken 的 token**，不是空白分词。

不变量仍是 `decode(encode(s))` 在允许的特殊 token 策略下可逆。字节级还要对任意字节可逆。

## 特殊 token、扩表、embedding

特殊 token（`endoftext`、聊天边界 `im_start` / `im_end`、工具边界）**不是 merge 出来的**。它们是词表里额外的原子 id，encode 路径上先按最长匹配抠出来，剩下的再走 BPE。tiktoken 用 `allowed_special` / `disallowed_special`：用户文本里若出现这些字面量，默认应拒绝或当普通字节切，否则 prompt 注入可以提前结束一段。训练聊天格式时它们必须是原子，否则模型会在中间插入半个边界。

扩词表两件不同的事：

1. **只加特殊符。** merge 表不动，$V\leftarrow V+k$。embedding / lm_head 从 $[V, D]$ 变成 $[V+k, D]$。新行初始化用旧表均值或很小的随机，旧行保持预训练值。词表绑定（tying）时两份权重一起改。
2. **继续 BPE 训练。** 在旧 merge 后续加新 pair，旧 id 必须稳定，否则所有 checkpoint 作废。一般不值得为几个工具名去做；加特殊符更干净。

错法：把新工具名当普通字符串，指望 BPE 切完模型自己「认」。切出来的是若干子词，边界监督没了。另一错法：扩表后忘记 lm_head，logits 维和 id 对不上，CE 直接读垃圾，那种 NaN 见 `openai-loss-spike`。

白板补一句复杂度：encode 对每个预分词块按 merge 优先级扫，实现上 tiktoken 用预处理好的核，复杂度按块长而不是按语料再训练。

## 追问

- **为什么 GPT-2 要正则预分词？** 避免跨空格疯狂合并，让词边界稳定，也让空格成为可学习特征。SentencePiece 用显式空格符达到类似目的。
- **Unigram 和 BPE 谁可逆？** 字节级 BPE 对字节可逆。Unigram 依赖词表覆盖；覆盖不全就要 fallback。
- **旧模型 embedding 怎么迁到新词表？** 旧 token 字符串对齐拷贝；对不上的行新初始化，再在新数据上短训。不要打乱旧 id。
- **`o200k_base` 只是 $V$ 更大吗？** 不只是。预分词和 merge 都换了，同样英文通常更短，多语言更明显。

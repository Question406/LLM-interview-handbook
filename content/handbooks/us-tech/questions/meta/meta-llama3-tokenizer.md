---
id: meta-llama3-tokenizer
section: meta
order: 3
level: A
title: Meta：Llama 3 tokenizer（tiktoken 风格）相对 Llama 2 SentencePiece 面试怎么讲
quick: >-
  Llama 2 是 32k 的 SentencePiece BPE；Llama 3 换成 tiktoken 风格的字节级 BPE，词表约 128k（公开报告是
  100k tiktoken 底表再加约 28k 非英语 token）。英语压缩大约 3.17 提到 3.94 字符/token。词表和 embedding
  绑死，不能混用两代 tokenizer。
tags:
  - Meta
  - Llama
  - Tokenizer
  - BPE
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Introducing Meta Llama 3
    url: https://ai.meta.com/blog/meta-llama-3/
    type: primary
  - title: Llama 3.2 — Connect 2024 vision, edge, and mobile
    url: https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/
    type: primary
  - title: tiktoken
    url: https://github.com/openai/tiktoken
    type: primary
---

Llama / GenAI 岗很少问「BPE 的全称」。更常见的是：两代 Llama 词表差在哪、压缩率怎么进训练和推理账、为什么不能拿 Llama 2 的 tokenizer 去数 Llama 3 的 context。公开材料就够答，不必假装有内部词表文档。算法骨架可以和 `anthropic-bpe-tokenizer` 对齐，本题收在 Meta 的选型上。

## 两代分别是什么

Llama 2（沿用 Llama 1）：SentencePiece 上的 BPE，词表 $32000$，带 byte fallback。空格是独立符号（常见写法是下划线块），整句送进去，没有 GPT-2 那种正则预分词。OOV 靠字节回退，不会 unk 炸掉，但多语言和代码会切得很碎。

Llama 3：Herd 论文写明，词表约 $128\mathrm{K}$，底表来自 tiktoken 的约 $100\mathrm{K}$ token，再加约 $28\mathrm{K}$ 非英语 token。实现是字节级 BPE：先按正则切成片段（字母、数字、标点），再按冻结的 merge 优先级合并。这和 GPT-4 系同一条族谱；别当成 SentencePiece 换了个文件名。Llama 3 Instruct 还有一套管道符包裹的 special token（`begin_of_text`、`eot_id`、header），chat 模板必须和训练时一致。

现场别说成「Llama 3 改用 Unigram」或「SentencePiece 不能做 BPE」。SentencePiece 是训练/编码框架，Llama 2 选的是里面的 BPE；Llama 3 换的是库、预分词和词表规模。

## 压缩率为什么是训练题

Llama 3 博客给过一个对外数字：同样文本最多大约少 $15\%$ token。Herd 论文更具体：一段英语样本上，字符/token 从 $3.17$ 到 $3.94$。含义是固定 $T$ 的上下文和固定 FLOPs 的预训练，模型「读到的字」变多。代码、CJK、西里尔这类在 32k 词表里很碎的分布，收益比英语大。

反过来，词表变大，embedding 和 lm_head 是 $[V, D]$。Llama 3 8B 比 Llama 2 7B 大约多 1B 参数，公开叙述里很大一块就是 $V$：$128256$ 对 $32000$。博客同时说：更好的压缩加上 8B 也用了 GQA（见 `meta-llama-gqa`），推理侧大致还能和 7B 打平。所以「词表越大越亏」是错的，要同时报 $V\cdot D$ 和平均 $T$。

端侧更狠。Llama 3.2 把小模型塞到手机和边缘设备，KV cache 和 prefill 都跟 $T$ 走。同一段用户话少 $15\%$ token，是延迟和显存，不只是 tokenizer 竞赛分数。

## 编码不变量，以及不能混用

tiktoken 风格 encode 的错法和 Anthropic 白板同一类：上线没有语料频次，只有 merge 表。按训练顺序合，遇到已经在词表里的片段可以整段留下（HuggingFace 对 Llama 3 的说明：若整词在词表里，不必再按 merge 拆）。SentencePiece 路线是另一套优先级（score / BPE 表），切出来的 id 序列对不上。

不变量：

- 同一 tokenizer，`decode(encode(s))` 在字节级上可逆（非法 utf-8 要有替换策略）；
- `vocab_size` 必须等于 embedding 行数；
- 特殊 token 的 id 冻结，chat 模板多一个或少一个 bos，位置编码会整段错位。

两代不能互换：用 Llama 2 的句长去估 Llama 3 的 8k/128k 窗口，会系统性偏长。继续预训练如果换词表，要扩矩阵并处理新 id 的初始化，改配置文件不够。

白板如果被要求对比 encode，我会先画预分词：tiktoken 族先用正则把数字、空格、字母切开，再对每个片段做 BPE；SentencePiece Llama 2 更接近「整句一条链」。不要在现场发明 Llama 3 的正则原文，说「和 GPT-4 同类、以仓库里的 tokenizer 文件为准」就够。

## 追问

- **为什么加 28k 非英语 token？** 论文说压缩和下游都有收益，且英语切分基本不受影响。面试答「多语言 fertility」，不要编造每个语言加了多少。
- **数字怎么切？** tiktoken 族常常把数字切得很细（一位一块很常见）。算术和表格任务会变长；这是词表税，模型「不会数数」只是其中一种读法。
- **和 128k 上下文是一件事吗？** 词表压缩改变的是同样字符占用的 $T$；长上下文是注意力能看多远，见 `meta-llama-rope`。两者相乘：更肥的 token 在同样 128k 窗口里能塞更多字。
- **能把 Llama 2 权重接到 Llama 3 tokenizer 上吗？** 不能直接接。id 空间变了，embedding 行对不上。要扩词表并重新训或做 embedding 对齐，这是另一个项目。

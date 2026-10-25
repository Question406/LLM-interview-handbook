---
id: meta-llama3-tokenizer
section: meta
order: 3
level: A
title: Meta：Llama 3 tokenizer（tiktoken 风格）相对 Llama 2 SentencePiece 面试怎么讲
quick: "Llama 2 用 32k SentencePiece BPE，Llama 3 换成约 128k 的 tiktoken 风格字节级 BPE，英语压缩从 3.17 提升到 3.94 字符/token。同样文本占的 token 更少，但 embedding 更大；两代 id 空间不同，不能混用 tokenizer 和权重。"
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

Llama 3 相比 Llama 2，主要换了 tokenizer 库、预分词方式和词表规模，仍然属于 BPE。更大的词表让同样文本用更少 token 表示，能降低上下文和 KV 成本，但也扩大 embedding 与 lm_head。两代 id 的含义不同，不能拿 Llama 2 的编码结果直接送给 Llama 3。

## 两代编码和压缩率有什么变化

Llama 2（沿用 Llama 1）：SentencePiece 上的 BPE，词表 $32000$，带 byte fallback。空格是独立符号（常见写法是下划线块），整句送进去，没有 GPT-2 那种正则预分词。OOV 靠字节回退，不会 unk 炸掉，但多语言和代码会切得很碎。

Llama 3：Herd 论文写明，词表约 $128\mathrm{K}$，底表来自 tiktoken 的约 $100\mathrm{K}$ token，再加约 $28\mathrm{K}$ 非英语 token。实现是字节级 BPE：先按正则切成片段（字母、数字、标点），再按冻结的 merge 优先级合并。这和 GPT-4 系属于同一类编码方式，预分词和词表都与 Llama 2 不同。Llama 3 Instruct 还有一套管道符包裹的 special token（`begin_of_text`、`eot_id`、header），chat 模板必须和训练时一致。

这里要区分框架和算法：SentencePiece 支持 BPE，Llama 2 就选了 BPE；Llama 3 也没有因此变成 Unigram。

压缩率会直接影响训练和推理预算。Llama 3 博客给过一个对外数字：同样文本最多大约少 $15\%$ token。Herd 论文更具体：一段英语样本上，字符/token 从 $3.17$ 到 $3.94$。含义是固定 $T$ 的上下文和固定 FLOPs 的预训练，模型「读到的字」变多。代码、CJK、西里尔这类在 32k 词表里很碎的分布，收益比英语大。

反过来，词表变大，embedding 和 lm_head 是 $[V, D]$。Llama 3 8B 比 Llama 2 7B 大约多 1B 参数，公开叙述里很大一块就是 $V$：$128256$ 对 $32000$。博客同时说：更好的压缩加上 8B 也用了 GQA（见 `meta-llama-gqa`），推理侧大致还能和 7B 打平。因此要一起估算 $V\cdot D$ 和平均 $T$，才能判断大词表的总成本。

端侧对这项取舍更敏感。Llama 3.2 把小模型塞到手机和边缘设备，KV cache 和 输入预填充（prefill，即处理输入并建立缓存） 都跟 $T$ 走。同一段用户话少 $15\%$ token，是延迟和显存，不只是 tokenizer 竞赛分数。

## 上线时怎么检查兼容性

tiktoken 风格的 encode 上线时依据固定 merge 表，不再依据语料频次。按训练顺序合，遇到已经在词表里的片段可以整段留下（HuggingFace 对 Llama 3 的说明：若整词在词表里，不必再按 merge 拆）。SentencePiece 路线是另一套优先级（score / BPE 表），切出来的 id 序列对不上。

不变量：

- 同一 tokenizer，`decode(encode(s))` 在字节级上可逆（非法 utf-8 要有替换策略）；
- `vocab_size` 必须等于 embedding 行数；
- 特殊 token 的 id 冻结，chat 模板多一个或少一个 bos，位置编码会整段错位。

两代不能互换：用 Llama 2 的句长去估 Llama 3 的 8k/128k 窗口，会系统性偏长。继续预训练如果换词表，要扩矩阵并处理新 id 的初始化，改配置文件不够。

对比 encode 时，可以先画预分词：tiktoken 族先按正则把数字、空格和字母分段，再逐段做 BPE；SentencePiece Llama 2 更接近整句编码。具体正则以仓库 tokenizer 文件为准。

相关：`anthropic-bpe-tokenizer`。

## 追问

**为什么加 28k 非英语 token？**
论文说压缩和下游都有收益，且英语切分基本不受影响。面试答「多语言 fertility」，不要编造每个语言加了多少。
**数字怎么切？**
tiktoken 族常常把数字切得很细（一位一块很常见）。算术和表格任务会变长；这是词表税，模型「不会数数」只是其中一种读法。
**和 128k 上下文是一件事吗？**
词表压缩改变的是同样字符占用的 $T$；长上下文是注意力能看多远，见 `meta-llama-rope`。两者相乘：更肥的 token 在同样 128k 窗口里能塞更多字。
**能把 Llama 2 权重接到 Llama 3 tokenizer 上吗？**
不能直接接。id 空间变了，embedding 行对不上。要扩词表并重新训或做 embedding 对齐，这是另一个项目。

## 相关题

- [[openai-tiktoken]]：tiktoken 和 SentencePiece 的算法差别、特殊 token 和扩词表，讲得比本卡更细。
- [[sys-tokenizer-same]]：两套 id 空间不能混用；那张卡讲 RL 训练里混用之后具体坏在哪。
- [[anthropic-bpe-tokenizer]]：字节级 BPE 的手写实现和往返不变量。

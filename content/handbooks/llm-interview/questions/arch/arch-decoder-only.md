---
id: arch-decoder-only
section: arch
order: 18
level: A
title: 为什么大多数生成式 LLM 使用 Decoder-only？
quick: >-
  Decoder-only 用一个因果 next-token 目标覆盖预训练、续写、对话和 in-context
  learning，连续文本不用包装成 pair，数据和系统都好 scale。这是工程、数据和产品形态的复合选择；源要双向编码、输出较短的翻译摘要类任务，encoder-decoder 仍有优势。
tags:
  - Transformer
  - Architecture
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Improving Language Understanding by Generative Pre-Training
    url: https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf
    type: primary
  - title: Language Models are Unsupervised Multitask Learners
    url: https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
    type: primary
  - title: Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer
    url: https://arxiv.org/abs/1910.10683
    type: secondary
---

主要原因是统一：Decoder-only 把所有 token 放进同一条序列，用 causal mask 学 $p(x_t\mid x_{\lt t})$，预训练、续写、对话、in-context learning 都是这一个目标，大规模互联网文本也不用人工构造 source / target pair。这是工程和数据上的选择，decoder 在表达力上并不处处更强。翻译、摘要这类「条件输入要双向编码、输出再生成」的任务，encoder-decoder 仍有结构优势。

所以面试里别把 GPT 路线说成唯一正确的架构。要讲清两件事：统一目标怎么换来了 scale，以及什么时候还该用编码器。

## 统一的因果目标让数据和任务都变简单

预训练语料是连续文本，Decoder-only 直接最大化 next-token likelihood，不用把文档切成「源语言 / 目标语言」或「文章 / 摘要」。指令微调只是在同一条因果链上换了分布：用户和助手的轮次拼进同一条序列，照样预测下一个 token。In-context learning 也是同一个机制，示范写在左边，被 causal mask 当成条件。一套参数、一套损失（loss）、一套 autoregressive 推理循环，从预训练一直用到部署。

Encoder-decoder 要先双向看完整个源，再 cross-attend 着生成。预训练得先定义源和目标怎么切，T5 的 text-to-text 也还是要包装一层，流水线更重。用大规模无监督文本训练时，包装步骤越少越容易扩大规模；而且把语料包装成 pair，本身就引入了归纳偏置。GPT 系把这一点做成了默认生态：工具、KV cache、speculative decoding、对齐算法都按单栈 autoregressive 来写。

代价是 causal mask 让前缀内部没法双向交互。比如「先读完整篇文章再写摘要」，encoder 一次双向编码更省；decoder-only 只能靠更多层、更长上下文去补。GPT 路线靠 next-token 目标学多种任务，把指令和示范放在前缀里，这很适合通用对话，但不代表对所有条件生成任务都最合适。

## Encoder-decoder 的主场

翻译、摘要、span 重建，以及输入很长、需要被反复交叉访问的条件生成，用 encoder-decoder 仍然自然：源侧双向、目标侧因果，两侧参数还可以不对称，大编码器配小 decoding 器来降生成延迟，源侧表示也能缓存。T5、BART、Flan-T5 说明统一文本接口也可以走这条路。

生成式 LLM 偏向 decoder-only，是因为产品形态变成了开放式的 chat / reasoning / agent。这些场景没有稳定的「源句子」，条件是对话历史、工具返回、检索片段，本来就可以当左前缀拼进因果序列。为每种条件单独配一个编码器，收益往往抵不过统一栈的基础设施成本。而且通用助手的输出常比输入长（解释、代码、chain of thought），成本主要在 decoding 器，再加一个大编码器的边际收益就小了。多模态里的「视觉编码器 + 文本 decoder」，视觉编码器只是感知前端，主模型并没有回到机器翻译式的 seq2seq。

## Scale 与生态

社区默认 decoder-only 之后，推理引擎、并行（DP/TP/PP）、post-training（SFT/PPO/DPO）都按 causal LM 来写。KV cache、paged attention、speculative decoding、RLHF 的接口都是单栈的，换成 seq2seq 要重做 mask、位置和缓存布局，团队往往因此留在 decoder-only。这是统一目标加统一系统带来的复合优势，数学上并没有证明 decoder-only 处处最优。反例可以举条件很长、输出很短的分类式任务，或者需要强双向理解的检索编码器，这些本来就不必拿生成式 LLM 硬扛。

选型可以这么说：开放续写和对话用 decoder-only；源和目标稳定分离、源必须双向读，考虑 encoder-decoder；要的是理解向量、不用生成，就用 encoder-only。别把三种 Transformer 用法混成一句「现在都用 GPT」。路线的分歧在预训练包装成本和产品形态上，跟谁「更 Transformer」无关。

## 追问

**Decoder-only 的前缀为什么不能双向？**
Causal mask 禁止位置 $t$ 看到后面的位置，整段 prompt 内部因此没有 BERT 式的双向交互，只能靠层深和 attention 间接传信息。

**Prefix-LM / UL2 算什么？**
折中方案。在 decoder 栈上对前缀放开双向 attention，或者混用去噪目标，没有再引入独立的编码器；目标的包装可能比 causal LM 更重。

**Chat 为什么仍用 causal？**
轮次拼成一条序列就行，不用定义「用户侧编码器」，工具结果也当作新的前缀，这和开放式的产品形态一致。

**小模型做翻译是不是该用 encoder-decoder？**
常常是。源短、对齐质量要求高、数据是平行句对时，seq2seq 仍很合适，这和千亿级通用 chat 的数据形态不同，别拿 GPT 生态去否定翻译栈。

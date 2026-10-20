---
id: arch-decoder-only
section: arch
order: 18
level: A
title: 为什么大多数生成式 LLM 使用 Decoder-only？
quick: >-
  Decoder-only 用统一的因果 next-token 目标覆盖预训练、续写、对话和 in-context
  learning，数据格式简单、scale 方便。Encoder-decoder 在条件输入要双向编码、输出再生成的任务上仍有优势。
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

Decoder-only 把所有 token 放在同一条序列里，用 causal mask 学 $p(x_t\mid x_{\lt t})$。大规模互联网文本不必人工构造 source / target pair，预训练、续写、对话、in-context learning 共用一个目标。这是工程和数据的选择：decoder 并不在表达力上处处更强。Encoder-decoder 在翻译、摘要这类「条件输入要双向编码、输出再生成」的任务上仍有结构优势。面试别把 GPT 路线说成唯一正确架构；要讲清统一目标怎么换来 scale，以及何时还该用编码器。

## 统一因果目标，数据与任务都变简单

预训练语料是连续文本。Decoder-only 直接最大化 next-token likelihood，不需要把文档切成「源语言 / 目标语言」或「文章 / 摘要」。指令微调只是在同一条因果链上换分布：用户与助手轮次拼进同一序列，仍然预测下一个 token。In-context learning 也是同一机制：示范写在左边，被 causal mask 当成条件。一套参数、一套 损失（loss）、一套自回归推理循环，覆盖预训练到部署。

Encoder-decoder 要双向看见整个源，再 cross-attend 生成。预训练必须定义源和目标怎么切（T5 的 text-to-text 仍要包装），流水线更重。使用大规模互联网无监督文本训练时，减少数据包装步骤更便于扩大训练规模。GPT 系把这一点做成默认生态：工具、KV cache、投机解码、对齐算法都按单栈自回归来写。

Causal mask 的代价是前缀内部不能双向交互。「先读完整篇文章再写摘要」这类任务，encoder 一次性双向编码更省；decoder-only 只能靠已生成前缀和注意力，用更多层、更长上下文来补。无监督语料被包装成 pair 时，包装本身就引入归纳偏置。GPT 路线依赖 next-token 目标来学习多种任务，把指令和示范放在前缀上下文中。这种方式适合通用对话，但不代表对所有条件生成任务都最合适。

## Encoder-decoder 的主场

翻译、摘要、span 重建、输入很长且应被反复交叉访问的条件生成，encoder-decoder 仍自然：源侧双向、目标侧因果，参数可以两侧不对称（大编码器、小解码器）以降低生成延迟。T5、BART、Flan-T5 证明统一文本接口也可以走这条路。

生成式 LLM 主流偏 decoder-only，因为产品形态变成了开放式 chat / reasoning / agent：没有稳定的「源句子」，条件是对话历史、工具返回、检索片段，本来就可以当左前缀拼进因果序列。为每一种条件单独配置编码器，收益常常盖不过统一栈的基础设施。多模态里「视觉编码器 + 文本 decoder」是感知前端，不是又回到机器翻译式的 seq2seq 主模型。

「源必须被反复、双向地读，输出相对短」时，encoder-decoder 仍更省：翻译解码器可以更小，源侧表示可缓存。通用助手的输出往往比输入更长（解释、代码、思维链），解码器主导成本，再增加一个大编码器的边际收益变小。这是产品形态驱动架构，不是 decoder 在一切 perplexity 竞赛里必胜。

## Scale 与生态

社区一旦默认 decoder-only，推理引擎、并行（DP/TP/PP）、post-training（SFT/PPO/DPO）都按 causal LM 写。换架构要重做 mask、位置、KV cache 布局。统一目标加统一系统带来复合优势，并不是数学证明 decoder-only 处处最优。反例可以举条件很长、输出很短的分类式任务，或强双向理解的检索编码器：那些本来就不必用生成式 LLM 硬扛。

选型：开放续写和对话用 decoder-only；稳定的源目标分离且源必须双向，考虑 encoder-decoder；要理解向量而不是生成，用 encoder-only。不要把三种 Transformer 用法混成一句「现在都用 GPT」。生态锁定也很实在：KV cache、paged attention、投机解码、基于人类反馈的强化学习（RLHF） 的 causal LM 接口都按单栈写；换 seq2seq 要重做 mask 与缓存布局，团队往往因此留在 decoder-only。承认这是系统和数据的复合选择，比声称 decoder 表达力更强更经得起追问。路线分歧在预训练包装成本和产品形态，不在谁「更 Transformer」。

## 追问

- **Decoder-only 前缀为什么不能双向？** Causal mask 禁止 $t$ 看见更后面的位置。整段 输入提示（prompt） 内部因此没有 BERT 式双向交互，只能靠层深和注意力间接传信息。Prefix-LM 可以对前缀放开，那是折中。
- **Prefix-LM / UL2 算什么？** 在 decoder 栈上对前缀放开双向或混用去噪目标，是折中，不是又引入独立编码器。目标仍可比 causal LM 更重包装。
- **Chat 为什么仍用 causal？** 轮次拼成一条序列即可，不必定义「用户侧编码器」。工具结果也当作新前缀。这与开放式产品形态一致。
- **小模型翻译是不是该用 encoder-decoder？** 常常是。源短、需要对齐质量、数据是平行句对时，seq2seq 仍很合适；那与千亿通用 chat 的数据形态不同。不要用 GPT 生态去否定翻译栈。

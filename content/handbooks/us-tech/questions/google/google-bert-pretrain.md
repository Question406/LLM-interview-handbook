---
id: google-bert-pretrain
section: google
order: 11
level: A
title: Google：BERT 两个预训练任务各解决什么，NSP 后来为什么被质疑
quick: "MLM 用被遮盖的词训练双向表示，NSP 原本想教相邻两段的关系。NSP 的跨文档负例容易靠主题判断，RoBERTa 在更强配方下去掉它仍更好，ALBERT 则用同一对段落交换顺序的 SOP 来学连贯性。"
tags:
  - Google
  - BERT
  - MLM
  - NSP
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: BERT — Pre-training of Deep Bidirectional Transformers for Language Understanding
    url: https://arxiv.org/abs/1810.04805
    type: primary
  - title: RoBERTa — A Robustly Optimized BERT Pretraining Approach
    url: https://arxiv.org/abs/1907.11692
    type: primary
  - title: ALBERT — A Lite BERT for Self-supervised Learning of Language Representations
    url: https://arxiv.org/abs/1909.11942
    type: primary
---

MLM 让 BERT 学双向上下文，NSP 原本想补上句间关系的监督。后来对 NSP 的质疑主要是：跨文档抽负例太容易让任务退化成主题分类，在更强的训练配方下也未必需要它。

GPT 式因果 LM 只看左边，BERT 允许双向注意力，直接做标准 next-token 会从右侧看到答案。MLM 因此随机选约 15% WordPiece，让位置 $i$ 从损坏输入预测原词。选中的 token 中，80% 换成 `[MASK]`，10% 换随机词，10% 原样保留，构成 80/10/10。微调时没有 `[MASK]`，保留原词与噪声能减轻预训练和微调的不一致。

每个位置因此融合左右语境，QA、NER、分类可以再接任务层。不过 token 级目标没有显式教两段是否在原文相邻。NSP 用同文档连续两段作正例，第二段来自其他文档作负例，比例 50/50，在 `[CLS]` 上二分类，BERT 论文报告它对 QA / NLI 有帮助。

例如 A 是“他打开了门”，B 是“房间很黑”，这是正例；B 换成另一篇体育新闻就是负例，主题词已足以判断。ALBERT 的 SOP 保留同一对连续段落，把顺序对调作负例，主题没变，必须判断语篇先后。论文中 NSP 模型做 SOP 接近随机，SOP 模型却还能部分做对 NSP，支持了 NSP 未充分学到连贯性的解释。

RoBERTa（2019）则保留双向 MLM，用更长训练、更大 batch、动态 mask，并去掉 NSP、改喂长连续文档，GLUE / SQuAD / RACE 都没有下降。它说明 NSP 的收益与数据、训练量和输入格式交织；去掉 loss 但仍用短句对，和改用长文档也会不同，Devlin 的消融可能混合了这两个变量。由此更稳妥的结论是，更强配方下 NSP 并非必需，不能简单说它被证明完全错误。

搜索 query 与文档通常不需要“下一句”关系，双向表示和下游微调更重要。检索双塔一般用 query-doc 对比学习，主题匹配本身也是目标。Google 后来大量用 T5 / decoder-only，句间任务也可直接生成；继续训练编码器时，可以默认 MLM 或 span，若确需句序 / 连贯监督再考虑 SOP 或下一句生成。

## 追问

**动态 mask 和原始 BERT 有何不同？**
原始实现一次生成 mask 后复用，RoBERTa 每次重新采样，同样训练步数看到更多损坏模式。

**为什么不把遮盖比例提得更高？**
太高会破坏上下文，太低监督又稀。T5 仍用约 15% token，不过改成 span。

**没有 NSP，还能用 `[CLS]` 吗？**
可以。编码器仍可用 `[CLS]` 或平均池化，decoder-only 常用最后 token 或 pooling。NSP 不是 next-token，RoBERTa 去掉 NSP 也不等于双向表示无效。

**SOP 和 NSP 可以同时加吗？**
一般没有必要。SOP 已覆盖连贯性，再加 NSP 更多是在增加容易的主题判别任务。

相关：`google-t5-span`

---
id: google-bert-pretrain
section: google
order: 11
level: A
title: Google：BERT 两个预训练任务各解决什么，NSP 后来为什么被质疑
quick: "MLM 逼编码器同时看左右上下文，填被盖住的 token，学的是双向表示。NSP 是二分类：两段是不是原文里相邻，本意是学句间关系。RoBERTa 去掉 NSP 更好；ALBERT 认为 NSP 太容易靠主题做对，改成句序 SOP。"
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

Google BERT 岗 / 搜索理解岗的基础题。不是默 2018 年的设定，是问两个 损失（loss） 各自监督什么、后来哪一篇把它证伪。生成式对照见 `google-t5-span`。

## MLM：给双向编码器一个合法的训练信号

GPT 式因果 LM 只能看左边。BERT 要双向，就不能用标准 next-token：模型会从右边「抄答案」。MLM 随机盖约 15% WordPiece，让位置 $i$ 只通过 `[MASK]` 这类损坏输入去预测原词，整句仍双向注意力。

80/10/10：被选中的 token 里，80% 换成 `[MASK]`，10% 随机词，10% 原样保留。原因：微调时没有 `[MASK]`，若预训练全是 mask，会出现预训练-微调不一致。留一点原词和噪声，逼表示在没有 mask 时也有用。

MLM 解决的是 token 级双向语境。QA、NER、分类之所以能直接接一层，是因为每个位置已经融合了左右。它不显式教「两句话是不是同一篇文档里的下一句」。句子对任务（NLI、问答的 query-passage）要另开一条监督，这就是 NSP 的动机。

## NSP：本意是句间关系，后来被说成太容易

正样本：同一文档里连续两段。负样本：第二段从别的文档抽。50/50。`[CLS]` 上做二分类。论文说这对 QA 和 NLI 有帮助。

质疑来自两头：

RoBERTa（2019）。 同样架构，更长训练、更大 batch、动态 mask，去掉 NSP，用连续全文而不是句子对。GLUE / SQuAD / RACE 不降反升。结论：原始 BERT 的 NSP 收益，和「训练不够、数据不够、静态 mask」缠在一起；在更强配方下 NSP 不是必要项。他们还指出：去掉 NSP 但仍喂短句对，和喂长连续文档，效果不同：Devlin 的消融可能把「输入格式」和「NSP loss」混在一起了。

ALBERT。 认为 NSP 的负样本来自不同文档，模型靠主题就能做对：两段是不是同一个话题。这和 MLM 已经学到的文档内聚高度重叠。真正难的是语篇连贯。SOP 正样本仍是连续两段，负样本是同一对但顺序对调。主题一样，必须看先后。ALBERT 写：NSP 模型在 SOP 上接近随机，说明它没学连贯；SOP 模型还能部分做对 NSP。

所以面试不要骂「NSP 是错的」。更准的句子：NSP 的负采样让任务退化成主题判别，和 MLM 重复；句间关系若还要，应该用 SOP 或下一句生成，而不是跨文档二分类。

## 现场怎么讲取舍

搜索相关性：query 和文档是不是「下一句」并不重要，重要的是双向编码和后续微调。Google 后来大量用 T5 / decoder-only，句间任务直接生成。若还在训编码器，默认 MLM（或 span），不加 NSP，除非下游明确是句序 / 连贯。

常见误区是：把 NSP 说成 next-token；把 `[CLS]` 说成必须有 NSP 才能用；说 RoBERTa 证明双向没意义。RoBERTa 去掉的是 NSP，不是 MLM。

现场例子：A「他打开了门。」B「房间很黑。」是 NSP 正样本；B 换成另一篇体育新闻是负样本。模型靠主题词就能做对。SOP 负样本只是把 A/B 对调，主题不变，必须看顺序。这就是 ALBERT 说 NSP 太容易的原因。

## 追问

- **动态 mask 是什么？** BERT 原实现把 mask 一次做好复用。RoBERTa 每次看到序列重新采样 mask，同样步数看到更多腐蚀模式。微调时没有 mask 记号，所以预训练才保留 10% 原词和 10% 随机词，减轻记号不一致。
- **15% 能不能更高？** 太高上下文被毁，双向优势没了；太低监督太稀。T5 仍用约 15% token，但改成 span，见 `google-t5-span`。
- **NSP 对检索双塔还有用吗？** 一般不用 NSP。用对比学习对齐 query-doc。主题匹配正是双塔要学的。原文说 NSP 是为了 QA / NLI；后来去掉 NSP 改连续文档，这些任务并不掉。
- **为什么现在很少提 `[CLS]`？** Decoder-only 用最后一个 token 或 pooling。编码器分类仍可用 `[CLS]` 或平均池化；这和 NSP 无关。
- **SOP 和 NSP 能同时加吗？** 没必要。SOP 已经覆盖连贯；再加 NSP 等于再给一条容易的主题题。收口：MLM 学双向词义；NSP 本想学习句间关系，却退化成主题分类，所以后来去掉或改 SOP。

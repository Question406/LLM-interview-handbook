---
id: google-t5-span
section: google
order: 3
level: A
title: Google：T5 span corruption 预训练目标为什么比 BERT MLM 更适合生成
quick: "T5 用一个 sentinel 替换一段连续缺失文本，让编码器读残缺输入、解码器按顺序生成被挖掉的片段。这个预训练接口和摘要、翻译的 text-to-text 微调更接近；BERT MLM 则在双向编码器的被遮位置做词表分类，没有练同一条自回归生成路径。"
tags:
  - Google
  - T5
  - Span Corruption
  - Pretraining
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer
    url: https://arxiv.org/abs/1910.10683
    type: primary
  - title: BERT — Pre-training of Deep Bidirectional Transformers for Language Understanding
    url: https://arxiv.org/abs/1810.04805
    type: primary
---

T5 的 span corruption 更适合迁移到生成任务，因为预训练时已经在练「读输入、按顺序写文本」这条编码器到解码器的路径。比如挖掉一句话中的短语，解码器要连续把短语补出来，和摘要、翻译所需的生成方式更接近。下面比较同样约 15% 噪声时的两种目标，BERT 的预训练任务见 `google-bert-pretrain`。

BERT MLM：随机遮住约 15% 的 token，编码器双向看整句，在被盖位置做词表分类。每个被盖位置几乎独立，没有「从左到右写出一句话」这条计算图。下游若要摘要、翻译，你得另接解码器，或把 BERT 当编码器冻住。预训练和生成微调接口对不上。

T5 默认目标（论文 Figure 2）：同样丢掉约 15% token，但连续被丢的片段合成 一个 sentinel。编码器看到的是缩短后的带洞句子；解码器的目标 只含被挖掉的 span，用同一套 sentinel 当分隔，最后再加一个结束 sentinel。均值 span 长度他们扫过，基线取 3。

拿一句话看会更清楚。原句 `Thank you for inviting me to your party last week.` 若挖掉 `for inviting` 和 `last`：

- 编码器输入：`Thank you extra_id_0 me to your party extra_id_1 week.`
- 解码器目标：`extra_id_0 for inviting extra_id_1 last extra_id_2`

解码器每一步都是因果语言模型，交叉注意力看着编码器。这就是生成。

这里有几处与生成任务直接对应：

1. 输出是一段序列，不是一袋独立分类。 摘要、翻译、问答的微调格式都是「前缀任务名，解码出文本」。预训练已经在练这段解码器。MLM 练的是双向填空，生成时还要重新学因果和长度。
2. Span 逼你重建短语，不只是单点词表。 生成错误经常是整段漏信息。连续 span 比单 token mask 更接近「写出 missing 内容」。
3. 减少解码器需要预测的内容。 目标长度大约是被腐蚀的那 15%，不是整句重构。论文写明：只预测丢掉的 token、把连续洞收成一个 sentinel，是为了省预训练算力。BERT 式「编码器输出整句、每个位置都算」在 encoder-decoder 里反而更贵，而且解码器没有真正生成。

T5 消融里，prefix LM、整句重构 MLM、打乱复原，大多不如 span corruption；翻译 BLEU 上 span 也更好。不要据此声称「理解任务 MLM 一定差」：GLUE 上差距没有那么大。要强调生成接口和目标长度。

- 把 T5 说成「BERT 加上自回归」。差在：洞的粒度、解码器目标是不是全句、下游是否统一成 text-to-text。
- 说 span 降低了 FLOPs 公式里的 $O(T^2)$。没有。注意力仍按序列长度走；省的是目标序列短、解码步少，以及编码器侧洞被压缩。
- 用尖括号把 sentinel 写成 HTML 标签。白板写 `extra_id_0` 或「哨兵 0」。

算一笔账。长度 512、腐蚀 15%、平均 span 3：大约二十来个洞。解码器目标长度约 $0.15\cdot 512$ 再加 sentinel，不是 512。BERT 要对整段每个位置出 logits（被盖位置才有监督）。生成微调时，T5 继续让编码器看全文、解码器从左到右写；BERT 还要另接一层解码或改成 seq2seq，预训练算力没有花在这条路径上。

若问「现在全是 decoder-only 了，T5 还有意义吗」：生成预训练的直觉还在，UL2 / prefix-LM 是后话。Google 面 T5，要讲清腐蚀方式和生成接口怎么对齐，别和 PaLM 比谁更大。规模化那条线见 `google-palm-pathways`。

## 追问

**为什么不让解码器重构整句？**
也能训，但计算浪费在已看见的 token 上。T5 基线只生成洞里的 span，encoder 已经读过上下文。

**span 长度取 1 不就是 MLM 吗？**
长度 1 仍是 sentinel + 解码器生成，接口还是生成；只是监督从短语退回单 token，生成迁移变弱。

**和 BERT 的 80/10/10 替换？**
T5 是丢掉 span 换 sentinel，不是随机替换原词。随机替换那路在 T5 消融里更弱。

**微调翻译时输入还挖洞吗？**
不挖。预训练学的是「看残缺上下文，写出缺失文本」；微调改成完整源句子 $\to$ 目标句子，编码器-解码器权重接着用。

**和 UL2 / 混合去噪？**
同一家族：多种腐蚀混合，仍是「损坏输入 → 生成缺失」。面试抓住 span 相对 MLM 的接口差即可，不必把 UL2 配方背全。

**sentinel 要进词表吗？**
要。`extra_id_0` 这类是额外特殊 token，不是自然语言子词。白板不要画成 HTML 尖括号标签。

---
id: openai-data-mix
section: openai
order: 19
level: A
title: OpenAI：pretrain 数据配比，web / code / math、epoch 和过滤怎么答
quick: "公开能引用的 OpenAI 数字停在 GPT-3：crawl 降权后仍占六成 token，WebText2 / 书 / 百科上采样。code 和 math 是后来默认要单列的域，不是 GPT-3 表里的行。配比是采样权重，不是磁盘占比。重复有用但有上限；过滤要防把方言和考题一起洗掉。"
tags:
  - OpenAI
  - Pretraining
  - Data mix
  - Filtering
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Language Models are Few-Shot Learners
    url: https://arxiv.org/abs/2005.14165
    type: primary
  - title: Scaling Data-Constrained Language Models
    url: https://arxiv.org/abs/2305.16264
    type: primary
  - title: DoReMi — Optimizing Data Mixtures Speeds Up Language Model Pretraining
    url: https://arxiv.org/abs/2305.10429
    type: primary
  - title: GPT-4 Technical Report
    url: https://arxiv.org/abs/2303.08774
    type: primary
---

## 题怎么来的

GPT-3 论文把训练混合写进了表：Common Crawl、WebText2、Books、Wikipedia 的 token 采样权重和磁盘容量不是一回事。GPT-4 报告几乎不谈 mix。面试如果问「你们内部 web / code / math 各占多少」，答：我不知道 GPT-4 的百分比，我知道权重、epoch、过滤、去污各自管什么。编一个 15% code 当内部数字，比答错 Kaplan 坐标还糟。

## 配比是采样，不是仓库体积

GPT-3 的公开账：Common Crawl 原始 token 远多于其它源，训练时只给约 60% 的采样质量；WebText2 约 22%，两类书合计约 16%，百科约 3%。高质量源会看到不止一个 epoch（论文写大约 2–3 遍），crawl 大约一轮。这就是「配比」：每一步从哪个桶抽，不是磁盘上谁最胖。

现在还会被追问 code / math，因为 GPT-3 那张表几乎是自然语言 web。后来 Codex 把代码当一域来继续训；公开模型把代码和数学单独加权。我会这么拆，而不报假百分比：

- **Web。** 体量来源。必须过滤：分类器（GPT-3 用 WebText 当正例打 crawl）、MinHash 近重、语言识别、boilerplate。不过滤，Chinchilla 的 $D$ 是脏的，$L(D)$ 拟合会骗人。
- **Code。** 语法严、长依赖，对后来的工具调用和推理有溢出效应。太多会把聊天变成函数体腔；太少则 HumanEval / 仓库编辑掉点。代码要用文档边界或结束符切开。随机把两个仓库拼成一条长序列且不做文档 mask，是另一种脏 $D$，长窗 packing 见 `openai-long-ctx-train`。
- **Math。** 真实占比通常小，靠上采样和合成题撑评测。合成题极易污染 GSM8K 一类，过滤器和 eval 去污要一起设计，见 `openai-eval-harness`。

DoReMi 先训一个小 proxy 学域权重，再放到大模型上。用来说明「权重可以学，不是拍脑袋 60/20/20」。不要声称 OpenAI 用了 DoReMi。

## epoch、重复、过滤的边界

Chinchilla 的 $D$ 默认当成独立 token。数据不够时可能重复使用已有样本。Muennighoff et al. 的公开结论大致是：重复到约 4 个 epoch，和新鲜数据差不多；再往上边际很快掉，十几 epoch 明显亏。所以「缺数据就多扫几遍」只在短区间成立。重复之前仍要去重：同一网页 20 次不算 20 倍信息，还容易把 eval 题干刷进记忆。

过滤不是越狠越好。按模型 perplexity 砍尾巴，常把代码、小语种、口语砍掉，留下「像百科的英语」。分类器在正例里如果全是 WebText，风格会朝那偏。毒性过滤和 PII 是产品约束，和 perplexity 过滤分开报。

epoch 和配比会耦合：百科权重 3% 但扫 3 个 epoch，有效暴露远高于 3%。白板要写清是采样概率还是每个源的遍数。Resume 时打乱种子，避免每次都在同一 shard 边界撞上坏 batch，那种 spike 见 `openai-loss-spike`。

和质量相对的另一头是 compute-optimal：在固定 $C$ 下先把 $D$ 当独立高质量 token 来算，再谈重复，见 `openai-scaling-laws`。脏数据上谈 20 token/参数没有意义。

一个常见误区是：把「高质量多看几遍」和「垃圾 crawl 也多看几遍」说成同一件事。前者是 GPT-3 表里的上采样；后者是在烧 FLOPs 背重复噪声。

白板我还会画一条简单的采样循环：每个 step 先抽域（web / code / math），再从该域的 shard 里抽文档，再 pack 到上下文长度。权重改的是第一步；epoch 改的是 shard 要不要重开。把这两步说成一个旋钮，后面的消融会解释不清。

## 追问

- **GPT-4 配比呢？** 未公开。讲 GPT-3 表 + 后来 code / math 要单列的原因。百分比只说自己做过的消融。
- **去重在过滤前还是后？** 近重一般在质量分类之后做，否则重复垃圾会骗过「出现次数」。Eval 去污单独扫 n-gram / canary。
- **合成 math 能当 $D$ 加进 scaling 吗？** 能加进训练，不能假装它和自然 web token 同质。评测泄漏时，$L(D)$ 和下游分数会分叉。
- **空桶怎么办？** 某个域滤完只剩一点，不要靠无限 epoch 补。要么降权，要么换源，否则重复定律先被打穿。

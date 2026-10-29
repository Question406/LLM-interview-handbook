---
id: openai-data-mix
section: openai
order: 19
level: A
title: OpenAI：pretrain 数据配比，web / code / math、epoch 和过滤怎么答
quick: >-
  数据配比先说每步从各个域 sampling 的权重，再交代各域重复多少遍、怎样过滤和去污。GPT-3 有公开配比，GPT-4
  没公开；web、code、math 的权重应靠 ablation 或代理模型比较，不能把仓库容量直接当训练占比。
tags:
  - OpenAI
  - Pretraining
  - Data mix
  - Filtering
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Language Models are Few-Shot Learners
    url: 'https://arxiv.org/abs/2005.14165'
    type: primary
  - title: Scaling Data-Constrained Language Models
    url: 'https://arxiv.org/abs/2305.16264'
    type: primary
  - title: DoReMi — Optimizing Data Mixtures Speeds Up Language Model Pretraining
    url: 'https://arxiv.org/abs/2305.10429'
    type: primary
  - title: GPT-4 Technical Report
    url: 'https://arxiv.org/abs/2303.08774'
    type: primary
---

我会把配比解释成训练每步从哪个数据桶抽样，再把各桶的 epoch 和过滤单独列出。比如百科磁盘上很小，也能 upsampling 多看几遍；直接报磁盘百分比，说明不了模型到底见过多少百科。

GPT-3 的公开 sampling 账是 Common Crawl 约 60%、WebText2 约 22%、两类书合计约 16%、Wikipedia 约 3%。crawl 原始 token 远多于其他源，高质量源约看 2–3 遍，crawl 约一轮。GPT-4 技术报告没有公开这样的 mix，因此不能虚构内部的 code 15% 等数字。

实际设计会单列 web、code、math。web 提供体量，但先做语言识别、boilerplate 清理、质量分类和 MinHash 近重；GPT-3 用 WebText 作 crawl 分类器正例。否则 Chinchilla 的 $D$ 混着低质重复，$L(D)$ 拟合也不可靠。code 有严格语法和长依赖，可影响工具调用与推理；过多可能让聊天像函数体，太少则 HumanEval、仓库编辑下降。document boundaries 或结束符要保留，随机拼两个仓库又不做文档 mask 会污染长窗 packing。

math 的自然占比通常少，可 upsampling 或补合成题，但 GSM8K 一类的污染风险要和过滤一起控制。Codex 把代码当单独域继续训练，后来的公开模型也单列代码和数学；这不代表 GPT-3 原表里就有这两行。DoReMi 通过小 proxy 学域权重，再用于大模型，说明权重可实验学习，不能据此声称 OpenAI 使用了 DoReMi。

需要限制重复次数。Chinchilla 的 $D$ 默认独立 token；Muennighoff et al. 发现约 4 个 epoch 内的重复接近新鲜数据，之后收益下降，十几 epoch 明显吃亏。重复前仍应去重，同一网页出现 20 次没有 20 倍信息，还可能反复强化 eval 题干记忆。

过滤也会改变域分布。perplexity 砍尾可能误删代码、小语种、口语，只剩百科式英语；全用 WebText 正例的分类器也会偏向该风格。毒性、PII 作为产品约束单列，避免与 perplexity 过滤混在一起。

白板上可以画成每步先抽域，再抽域内 shard 文档，再 pack 到上下文。权重控制第一步，epoch 控制 shard 是否重开；百科 3% 且看 3 遍时，暴露量要和遍数一起报清楚。resume 时打乱种子，减少总在同一 shard boundaries 碰到坏 batch 的 spike。在固定 $C$ 下，先按独立高质量 $D$ 算 compute-optimal，再讨论重复；脏数据上套 20 token/参数也不能说明训练是否合算。高质量 upsampling 与重复垃圾 crawl 的收益不同，需要分开 ablation。

## 追问

**GPT-4 配比怎么答？**
说未公开，引用 GPT-3，再解释 code、math 为什么要单列。自己做过的比例要有 ablation 依据。

**先过滤还是去重？**
近重一般在质量分类之后做，避免重复垃圾的出现次数干扰判断；eval 去污单独扫描 n-gram、canary。

**合成 math 能计入 $D$ 吗？**
能用于训练，但与自然 web token 不同质。泄漏评测时，$L(D)$ 与下游分数可能分叉。

**某个域过滤后几乎空了怎么办？**
降权或换源，无限加 epoch 会很快碰到重复收益的上限。

相关：`openai-long-ctx-train`、`openai-eval-harness`、`openai-loss-spike`、`openai-scaling-laws`

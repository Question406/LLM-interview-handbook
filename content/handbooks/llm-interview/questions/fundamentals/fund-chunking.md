---
id: fund-chunking
section: fundamentals
order: 15
level: A
title: RAG 的 Chunk Size / Overlap 怎么选？
quick: >-
  Chunk 太小丢 context、召回碎片化；太大 embedding/keyword 被稀释，而且塞入 LLM 成本高。Overlap
  防语义跨边界，但增加重复索引和 context redundancy。
tags:
  - RAG
  - Chunking
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: LlamaIndex node parsers
    url: https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/
    type: primary
  - title: Lost in the Middle
    url: https://arxiv.org/abs/2307.03172
    type: secondary
---

我会按文档结构、问题粒度和 reranker 能力调，而不是背一个固定 token 数。Chunk 太小：句子没有指代对象，召回一堆碎片，生成时拼不回完整规定。太大：embedding 被多主题稀释，关键词被淹没，而且少数几个 chunk 就占满窗口。Overlap 是为了不让跨段的定义在边界上被切开，不是越大越稳。别先报「512 / 50」，先说失败模式，再谈结构切分和 parent-child。代码、条款、对话需要不同切法。更好方案是小块召回、父级或邻窗生成，用召回和忠实度一起验收。

## 太小、太大、overlap 各自破坏哪一步

检索和生成是两条链：

- 太小：召回可能命中，但证据不自洽（「该条款适用」却看不到主语）。Rerank 也缺乏上下文。生成只能靠模型补全，忠实度下降。
- 太大：向量变成多主题平均，语义检索偏向「这篇文档像查询」而不是「这段话回答查询」。送进 LLM 后，真正相关的几句可能落在中间而被忽略。
- Overlap：让跨边界的实体 + 定义同时出现在某个 chunk 里，降低漏召回。代价是索引膨胀、同一段落被多个 chunk 带进 context，浪费窗口、还可能让模型看到重复句子。

没有与语料无关的最优宽度。代码函数、法律条款、论文段落、日志行的「语义单元」本来就不同；用同一字符窗去切，只是把问题推迟到调 overlap。代码按函数 / 类切，能保住签名和文档字符串在同一块；法律按条、款切，能保住「适用条件 + 法律效果」；对话按轮切，避免把两个人的话黏成一个向量。固定 token 窗是这些结构都不可用时的退路。Overlap 只服务一件事：语义单元被窗边界切断。若你已经按结构切，overlap 可以很小甚至为 0；若被迫用滑动窗，overlap 应覆盖典型句子长度，而不是块长的一半。

## 按结构切，再决定窗口，而不是相反

更好的顺序是：先按 heading、函数、条款、空行切出候选语义块，再对超长块做二次切分并加少量 overlap。结构切分失败时（纯扫描件、无标题 wiki）再退回固定窗。二次切分的目标是：单块能被 embedding 区分，同时单块或「块 + 邻居」足够回答一类典型问题。

Overlap 只需要覆盖「句子在边界被切断」的长度，而不是块长的一半。过大 overlap 会让相邻 chunk 几乎互为副本，ANN 返回近重复，rerank 失去区分度。应用层按 ID 或页码去重，避免 top-k 全是同一段的滑动窗。

问题粒度也要匹配。用户问「第 3.2 条赔偿上限」，块应接近条款；问「这份合同总体风险」，需要更大的 parent 或摘要索引。一种 chunk 大小服务不了两种问题分布。混合查询的系统往往维护两级索引：细粒度用于精确定位，粗粒度或摘要用于主题问题。只调一个 `chunk_size` 去迁就所有问题，会在某一类上系统性失败。还要考虑 embedding 模型的有效长度：块远长于它擅长的窗口，等于把多主题平均写进向量。切块参数是检索模型的超参，应在同一批问题上做网格，而不是从博客抄一个数。

## Parent-child / window 检索：小块召回，大块生成

实践里常用「小 chunk 负责召回、大 span 负责生成」：

- 句级或小节 embedding 提高召回分辨率；
- 命中后向上取 parent 节、前后句窗口，把指代补全再送给 LLM；
- 需要时再上 reranker，在扩大后的候选里排，而不是先塞满窗口。

这样不必把 chunk 做大来「预防切错」，也不必做很小然后指望 overlap 奇迹般还原章节。评测应同时看检索召回（小块）和问答忠实度（拼回后的上下文），以及平均送入 token 数。只优化召回会把 overlap 和块长推高；只优化延迟会切得过碎。索引更新成本也随 overlap 线性变差，热更新语料上这不是免费参数。Parent-child 的实现要点是：子块带 parent id，召回后去重到父级再送 LLM，避免五个子块把同一节重复贴五次。窗口检索（sentence window）是同一思想的局部版：命中句向两侧扩。无论哪种，chunking 都应落到「召回分辨率 vs 生成上下文」这一对矛盾，而不是一个魔法数字。

## 追问

- **有没有默认 token 数？** 没有跨语料的定律。从文档结构出发，用验证问题上的召回、忠实度、context 长度一起选，不要背固定值。代码、条款、对话的单元本来不同。先结构切，再谈窗长。
- **Overlap 能否替代语义切分？** 不能。它只修补边界切断，修不了「一块里塞了三个主题」。结构可用时 overlap 可以很小。
- **为什么还要 parent-child？** 召回要的是可区分的小单元，生成要的是完整局部上下文。一个粒度很难同时满足。命中后按 parent 去重，避免同一节贴多次。
- **块太大时 LLM 会怎样？** 相关句被稀释，且长上下文中部利用率差。这是检索+位置的叠加问题，不是单纯「窗口还不够」。先切对，再谈要不要更长模型。

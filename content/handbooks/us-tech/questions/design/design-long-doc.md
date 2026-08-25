---
id: design-long-doc
section: design
order: 15
level: A
title: 设计：长文档问答（检索 vs 长上下文 vs 分层摘要）
quick: >-
  先问文档是否单份、是否日更、是否要句级引用、p95 预算。单份能塞进窗口且要全局推理：长上下文。库大、权限、新鲜：检索。
  要廉价总览：分层摘要。多数生产是检索再在短窗口上生成，不是「一百万 token 一砸」。
tags:
  - Anthropic
  - Microsoft
  - Amazon
  - RAG
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Lost in the Middle — How Language Models Use Long Contexts
    url: https://arxiv.org/abs/2307.03172
    type: primary
  - title: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
    url: https://arxiv.org/abs/2005.11401
    type: primary
  - title: Anthropic — Long context
    url: https://www.anthropic.com/news/100k-context-windows
    type: secondary
---

Anthropic 长窗口、Microsoft 长上下文、Amazon 企业知识库都会问长文档 QA。Lost in the Middle 说明中间证据会被丢掉；RAG 论文给检索加生成骨架。白板要三选一的决策树，不是背窗口数字。不是某次现场逐字题。生产 RAG 纪律见 `design-prod-rag`；公司长上下文见 `anthropic-long-context`、`msft-long-context`。权限和引用仍是硬约束。

## 决策树：三种形状

我会先问：一份合同还是十万份政策、更新频率、ACL、要不要句级引用、p95、是否要跨章推理。

1. **长上下文。** 用户就这一份（或几份）PDF，需要全文对照、条款互斥、全局指代。把文档塞进窗口，引用页码。代价：prefill 随 token 涨，中间证据容易丢，见 Lost in the Middle。适合交互式「读这一本」。不适合整库。
2. **检索。** 语料大、多租户、日更、ACL。切片 + 元数据过滤 + 混合检索，答案必须带 `chunk_id`。细节见 `design-prod-rag`。适合「哪条政策适用」。跨很多文档的综合题召回会漏，要多跳或先路由再检索。
3. **分层摘要。** 先 map 每章摘要，再 reduce 成目录 + 问题相关的细读。适合「这本五百页讲什么」和预算紧的离线。摘要会丢数字和例外条款，不能当唯一证据；最终回答仍要回原文块。

混合最常见：检索 top 块，若块内还要全局关系，对 **命中的那几章** 再开长上下文，而不是对整库开窗口。路由错了比窗口不够更常见。

## 长上下文不是免费正确

窗口大，注意力仍偏两端。证据放中间会丢。对策：把检索到的块放两端或重复关键句；问句靠近证据；对引用做支撑检查，对不上就删句。Prefill 成本按 token，一百页扫一遍会打爆 p95 和钱（不谈单价，谈 token 和延迟）。NVIDIA 侧是 KV 带宽和页数，见 `sys-paged-attn`、`design-chat-serving`。

多份文档塞进同一窗口还有权限问题：检索层必须先 ACL。不能靠模型「别看无权限段」。存在性泄漏仍算事故。

表格、脚注、跨页句子：切片按结构，固定 token 会切断「仅适用于…」。长上下文也要把版面解析对，否则窗口里是乱码。

## 分层摘要的坑

Map-reduce 便宜、可并行，但：

- 数字、日期、例外在 map 被平均掉。
- 问题在 reduce 才出现，map 不知道该留哪句。应用 **问题相关的 map**：每章按当前问题抽，而不是通用摘要进库。
- 摘要版本要和源文档版本一起过期。源改了摘要没改，等于过期 RAG。

评测：单跳事实、多跳、数字、否定句（「不适用于」）、中间位置证据、权限负例。不要只用「读完好像对」。人评看引用是否真在源句，见 `design-offline-eval`。

失败模式：什么都塞长窗口导致 p95 爆炸；只检索导致跨章矛盾答不出；只摘要导致数字错；引用页码和 chunk 对不上。

白板决策顺序：先 ACL 和新鲜度，再窗口。无权限块根本不进上下文。单份合同、要对照互斥条款，走长上下文 + 页码引用。十万份日更政策，走检索。用户先问「这本讲什么」再问细节，走问题相关的分层摘要，细节仍回原文块。混合时检索导航、长上下文只读命中的那几章，不要对整库开窗口。

## 追问

- **窗口已经一百万了还要 RAG 吗？** 要。权限、新鲜、成本、中间丢失、整库塞不进一次交互。窗口解决的是「读这一本」。
- **用户上传一本再问十次？** 第一次解析 + 索引或缓存 KV 前缀；后续当会话前缀，见 `sys-prefix-cache`。
- **法律合同必须全文？** 倾向长上下文 + 条款级引用，检索只当导航。最终断言回原文。
- **多跳怎么补？** 先问题分解再检索，或迭代检索。一次 top-k 不够就承认，不要靠把 k 开到 100 装进去。

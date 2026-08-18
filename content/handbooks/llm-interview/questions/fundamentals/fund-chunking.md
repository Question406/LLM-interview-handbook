---
id: fund-chunking
section: fundamentals
order: 15
level: A
title: RAG 的 Chunk Size / Overlap 怎么选？
quick: >-
  Chunk 太小丢 context、召回碎片化；太大 embedding/keyword 被稀释且塞入 LLM 成本高。Overlap
  防语义跨边界，但增加重复索引与 context redundancy。
tags:
  - RAG
  - Chunking
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Chunk 太小丢 context、召回碎片化；太大 embedding/keyword 被稀释且塞入 LLM 成本高。Overlap 防语义跨边界，但增加重复索引与 context redundancy。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>应按文档结构、问题粒度与 reranker能力调，而不是固定 512 tokens。代码、法律条款、论文段落、日志需要不同 segmentation。</p><p>更好方案包括 heading/semantic chunk、parent-child retrieval、sentence window：先召回小 chunk，再扩展相邻/父级 context。</p></div>

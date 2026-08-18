---
id: fund-rag
section: fundamentals
order: 13
level: A
title: BM25、Dense Retrieval、Cross-Encoder Reranker 如何组合？
quick: >-
  BM25 擅长 exact lexical match；dense retrieval 擅长语义 paraphrase；工业常做 hybrid
  recall，再用更昂贵 cross-encoder 同时编码 query+document 做精排。
tags:
  - RAG
  - Retrieval
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>BM25 擅长 exact lexical match；dense retrieval 擅长语义 paraphrase；工业常做 hybrid recall，再用更昂贵 cross-encoder 同时编码 query+document 做精排。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>第一阶段需要从百万文档快速取 top-K，bi-encoder embedding 可预计算 document vectors；cross-encoder 每个 query-doc pair 联合 attention，准确但 O(K) 次昂贵 forward，所以只对几十/几百候选 rerank。</p><p>Hybrid 可避免专有名词/ID 被 dense miss，也补充 semantic recall。最终 RAG quality 要拆 retrieval recall 与 answer faithfulness。</p></div>

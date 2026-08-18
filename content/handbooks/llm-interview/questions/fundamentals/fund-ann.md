---
id: fund-ann
section: fundamentals
order: 14
level: A
title: HNSW / IVF / PQ 各自是什么？
quick: >-
  HNSW 是多层小世界图近邻搜索；IVF 先聚类到倒排 coarse cells 再搜少量 cells；PQ 把向量子空间量化成
  code，主要省内存并加速距离估计。
tags:
  - RAG
  - ANN
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>HNSW 是多层小世界图近邻搜索；IVF 先聚类到倒排 coarse cells 再搜少量 cells；PQ 把向量子空间量化成 code，主要省内存并加速距离估计。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>HNSW 查询从稀疏高层逐步下降到密集底层，recall 高但图内存大。IVF 的 nprobe 控制 speed/recall；PQ 将向量切 m 个 sub-vectors，各自用 codebook quantize，压缩 storage。</p><p>实践常组合 IVF-PQ 或 HNSW + quantized vectors。参数选择应以 recall@K、latency、memory 和 update rate 为准。</p></div>

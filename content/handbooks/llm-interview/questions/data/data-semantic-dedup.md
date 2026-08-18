---
id: data-semantic-dedup
section: data
order: 10
level: A
title: Semantic Dedup 怎么做而不过度删除？
quick: >-
  Embedding similarity 只代表语义接近，不代表训练信号重复。应先 coarse retrieve，再结合结构/答案/metadata
  判断“是否同一 training signal”，并对高价值多解法数据保留 diversity。
tags:
  - Data
  - Dedup
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Embedding similarity 只代表语义接近，不代表训练信号重复。应先 coarse retrieve，再结合结构/答案/metadata 判断“是否同一 training signal”，并对高价值多解法数据保留 diversity。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>典型流程：embedding ANN 找高相似 candidate → cross-encoder/LLM 或规则复核 → cluster → 选择代表样本。</p><p>对 reasoning 数据尤其要防过度删除：两个问题语义相似但需要不同 proof strategy/algorithm，仍有训练价值；两个 prompt 文本不同但 solution template 完全相同，反而可能是真重复。可以把 prompt embedding、answer/program AST、reasoning signature 一起纳入。</p></div>

---
id: sys-prefix-cache
section: systems
order: 15
level: A
title: Prefix Cache 的命中条件和风险？
quick: >-
  只有 tokenized prefix、模型权重/adapter、position/attention semantics 等一致时才能安全复用
  KV；字符串看起来相同但 tokenizer/template/LoRA 不同可能不能命中。
tags:
  - Serving
  - Cache
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>只有 tokenized prefix、模型权重/adapter、position/attention semantics 等一致时才能安全复用 KV；字符串看起来相同但 tokenizer/template/LoRA 不同可能不能命中。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Cache key 至少应包含 token IDs、model/version、adapter、relevant attention config。对带 dynamic system prompt、tool schema 的 Agent，prefix 很容易变化。</p><p>风险包括 cache poisoning/tenant isolation、显存 eviction、热点 prefix 占满 cache。可用 LRU/LFU/size-aware eviction，并按 tenant/security boundary 隔离。</p></div>

---
id: sys-pagedattention
section: systems
order: 8
level: A
title: PagedAttention 为什么像虚拟内存？
quick: >-
  把 KV Cache 切成固定-size blocks/pages，逻辑 sequence 的 KV 不必物理连续；block table 负责
  logical→physical 映射，减少碎片并支持动态增长/共享。
tags:
  - vLLM
  - KV Cache
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ vLLM
    url: 'https://arxiv.org/abs/2309.06180'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>把 KV Cache 切成固定-size blocks/pages，逻辑 sequence 的 KV 不必物理连续；block table 负责 logical→physical 映射，减少碎片并支持动态增长/共享。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>传统为每个 request 预留最大连续 KV buffer 会造成内部浪费和外部碎片。PagedAttention 只在需要时分配 blocks，sequence 结束就回收。</p><p>相同 prefix 的 requests 可以 copy-on-write / share 相同 blocks；beam search 的共同前缀也可复用。PagedAttention 改的是 memory management，不改变 attention 数学。</p></div>
          
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2309.06180" target="_blank" rel="noopener noreferrer">↗ vLLM</a></div>

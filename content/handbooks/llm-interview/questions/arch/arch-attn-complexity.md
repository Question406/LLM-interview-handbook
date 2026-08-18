---
id: arch-attn-complexity
section: arch
order: 2
level: A
title: Self-Attention 的时间和显存复杂度是什么？
quick: >-
  QKᵀ 与 attention×V 是 O(T²d)，显式 attention matrix 是 O(T²) memory；Q/K/V/O
  projections 还有 O(Td²)。短序列可能 projection 主导，长序列 T² 项主导。
tags:
  - Transformer
  - Complexity
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>QKᵀ 与 attention×V 是 O(T²d)，显式 attention matrix 是 O(T²) memory；Q/K/V/O projections 还有 O(Td²)。短序列可能 projection 主导，长序列 T² 项主导。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>对 X∈R^{T×d}，线性投影约 O(Td²)；attention score QKᵀ 为 O(T²d)，再乘 V 也是 O(T²d)。</p><p>所以不要只背“O(n²)”。当 T≪d 时，大矩阵 projection 可能占更大 FLOPs；当 T 很大时 attention 二次项主导。FlashAttention 不改变 exact attention 的渐近 FLOPs，而是避免 materialize 大量 T×T intermediate 到 HBM。</p></div>

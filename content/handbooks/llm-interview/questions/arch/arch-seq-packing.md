---
id: arch-seq-packing
section: arch
order: 17
level: A
title: Sequence Packing 如何减少 Padding 浪费？
quick: >-
  把多个短样本拼到同一个固定长度 sequence 里，提高有效 token 比例；关键是 attention mask、position/segment
  boundary 和 loss mask 不能让不同样本互相泄漏。
tags:
  - Training
  - Packing
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>把多个短样本拼到同一个固定长度 sequence 里，提高有效 token 比例；关键是 attention mask、position/segment boundary 和 loss mask 不能让不同样本互相泄漏。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>例如 max length 4096，四条 800-token 样本独立 padding 会浪费约 80%；packing 后可以放进同一 sequence。</p><p>需要 block-diagonal causal mask 或 varlen attention metadata，让 sample A 的 token 不能看到 sample B；position ids 可每段 reset 或连续，取决于模型实现。</p><p>Packing 提高训练吞吐，但会让 batch 中“样本数”与“token 数”关系变化，loss reduction/gradient weighting 要以 token 还是 sequence 为单位需明确。</p></div>

---
id: sys-checkpoint
section: systems
order: 5
level: A
title: Activation Checkpointing 的 Compute–Memory Tradeoff 是什么？
quick: >-
  前向只保存少量 checkpoint activations，反向需要时重算被丢弃的中间激活；显存显著下降，代价是额外 forward compute
  和更复杂 schedule。
tags:
  - Training
  - Memory
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>前向只保存少量 checkpoint activations，反向需要时重算被丢弃的中间激活；显存显著下降，代价是额外 forward compute 和更复杂 schedule。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>不 checkpoint 时每层保存大量 activation；checkpoint 可每几层保存边界，backward 时从边界重放。极端 full recompute 显存最省但计算最多。</p><p>实际要看模型是 compute-bound 还是 memory-bound、是否能 overlap 通信；重算增加 FLOPs 但如果原本受显存容量限制，它可以换来更大 batch/sequence，整体 throughput 反而可能更好。</p></div>

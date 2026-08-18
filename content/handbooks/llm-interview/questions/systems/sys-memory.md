---
id: sys-memory
section: systems
order: 3
level: S
title: Adam 训练一个 7B 模型为什么远不止 14GB？
quick: >-
  BF16 参数 2 bytes/param 只是权重本身。训练还可能保存 gradients、FP32 master weights、Adam
  m/v、activations、temporary buffers。经典 mixed-precision Adam 的参数状态常达到约 12–18
  bytes/param，取决于实现。
tags:
  - Memory
  - Optimizer
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>BF16 参数 2 bytes/param 只是权重本身。训练还可能保存 gradients、FP32 master weights、Adam m/v、activations、temporary buffers。经典 mixed-precision Adam 的参数状态常达到约 12–18 bytes/param，取决于实现。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>白板上不要死背“16 bytes/param”，而是列组成：BF16 params≈2B、grad≈2B或4B、FP32 master≈4B、Adam first moment≈4B、second moment≈4B。是否存在 master copy、grad dtype、fused optimizer 会改变总数。</p><p>7B×16 bytes≈112GB 只是一个常见量级；还没算 activation。Activation memory 与 batch、sequence、hidden、layers 强相关，activation checkpointing 可以用重算换显存。</p><p>ZeRO/FSDP 分片主要针对参数/梯度/optimizer states；TP/PP/CP 和 checkpointing 再解决模型层/activation/context。</p></div>

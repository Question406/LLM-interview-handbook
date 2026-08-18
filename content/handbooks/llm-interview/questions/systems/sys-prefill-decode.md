---
id: sys-prefill-decode
section: systems
order: 7
level: S
title: Prefill 为什么更 Compute-Bound，Decode 为什么更 Memory-Bound？
quick: >-
  Prefill 一次处理很多 tokens，形成大 GEMM、算术强度高；Decode 每 step 每 sequence 只新增 1
  token，却要读取大量模型权重和历史 KV，矩阵瘦、算术强度低，因此常受显存带宽限制。
tags:
  - Serving
  - Inference
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Prefill 一次处理很多 tokens，形成大 GEMM、算术强度高；Decode 每 step 每 sequence 只新增 1 token，却要读取大量模型权重和历史 KV，矩阵瘦、算术强度低，因此常受显存带宽限制。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Prefill 的 projection/FFN 类似 [T,d]×[d,d]，T 大时 GPU 能充分做矩阵乘；decode 更像 [B,d]×[d,d]，且每步重复读取 weights 和 KV。</p><p>Context 越长，decode 读取历史 K/V 越多，attention 部分 bandwidth 增长；batch 增大可提高 GEMM efficiency，但也增加 KV footprint。</p><p>这解释了 continuous batching、KV compression、prefill/decode disaggregation、chunked prefill 等 serving 技术的动机。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Batch 增大会让 decode 不再 memory-bound 吗？</summary><div class="follow-answer"><p>算术强度会提高，可能逐渐更 compute-friendly，但长 KV 和模型权重带宽仍重要；最终取决于模型/硬件/batch。</p></div></details><details class="followup"><summary>TTFT 和 TPOT 分别受什么影响？</summary><div class="follow-answer"><p>TTFT 主要受 queue+prefill；TPOT 主要受 decode scheduling、batch、KV/weight bandwidth。</p></div></details></div>

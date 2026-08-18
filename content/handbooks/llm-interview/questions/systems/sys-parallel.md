---
id: sys-parallel
section: systems
order: 1
level: S
title: DP / TP / PP / CP / EP 分别切什么？
quick: >-
  DP 切 batch；TP 切单层 tensor/matrix；PP 切 layers；CP/sequence parallel 切
  sequence/context；EP 切 experts。大模型通常多维组合，因为它们解决不同内存/通信瓶颈。
tags:
  - Distributed Training
  - Parallelism
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>DP 切 batch；TP 切单层 tensor/matrix；PP 切 layers；CP/sequence parallel 切 sequence/context；EP 切 experts。大模型通常多维组合，因为它们解决不同内存/通信瓶颈。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>并行</th><th>切分维度</th><th>主要通信/问题</th></tr></thead><tbody><tr><td>DP</td><td>batch</td><td>gradient all-reduce / reduce-scatter</td></tr><tr><td>TP</td><td>单层矩阵/heads</td><td>每层频繁 collective，依赖高速互联</td></tr><tr><td>PP</td><td>layers</td><td>pipeline bubble、microbatch scheduling</td></tr><tr><td>CP / sequence</td><td>sequence/context</td><td>attention/activation 跨设备通信</td></tr><tr><td>EP</td><td>experts</td><td>token dispatch/combine all-to-all</td></tr></tbody></table></div><p>TP 适合单层本身放不下或希望多卡共同做 GEMM；PP 适合按层切模型；ZeRO/FSDP 属于参数状态分片，与这些维度可以组合。MoE 还需要 EP 把 experts 分散。</p><p>并行策略应匹配拓扑：TP/EP 通信频繁，更适合 NVLink/NVSwitch 域内；DP/PP 可以跨相对慢的网络。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>TP 为什么对高速互联敏感？</summary><div class="follow-answer"><p>每层都可能 all-reduce/all-gather，通信在 critical path；延迟和带宽直接影响每 token latency。</p></div></details><details class="followup"><summary>PP 如何降低 bubble？</summary><div class="follow-answer"><p>增加 microbatches、1F1B 等 schedule、virtual stages；但 microbatch 太多会增加调度/activation开销。</p></div></details><details class="followup"><summary>CP 与 sequence parallel 完全同义吗？</summary><div class="follow-answer"><p>不同框架术语不完全一致。一般 CP 更强调长 context attention 跨设备；sequence parallel 常指把某些 activation/norm 按 sequence 维切分。</p></div></details></div>

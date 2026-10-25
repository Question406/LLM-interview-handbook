---
id: sys-parallel
section: systems
order: 1
level: S
title: DP / TP / PP / CP / EP 分别切什么？
quick: "DP 把 batch 分给不同副本，TP 切单层 tensor 或矩阵，PP 切层，CP 或 sequence parallel 沿 sequence/context 维切，EP 则分配不同专家。可以先用表格看各自切什么，再结合显存瓶颈和通信拓扑组合这些维度。"
tags:
  - Distributed Training
  - Parallelism
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>DP 把 batch 分给不同副本，TP 切单层 tensor 或矩阵，PP 切层，CP 或 sequence parallel 沿 sequence/context 维切，EP 则分配不同专家。可以先用表格看各自切什么，再结合显存瓶颈和通信拓扑组合这些维度。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>并行</th><th>切分维度</th><th>主要通信/问题</th></tr></thead><tbody><tr><td>DP</td><td>batch</td><td>gradient all-reduce / reduce-scatter</td></tr><tr><td>TP</td><td>单层矩阵/heads</td><td>每层频繁 collective，依赖高速互联</td></tr><tr><td>PP</td><td>layers</td><td>pipeline bubble、microbatch scheduling</td></tr><tr><td>CP / sequence</td><td>sequence/context</td><td>attention/activation 跨设备通信</td></tr><tr><td>EP</td><td>experts</td><td>token dispatch/combine all-to-all</td></tr></tbody></table></div><p>选型时先看哪里放不下。单层矩阵过大，或希望多卡一起做 GEMM，可以用 TP；模型层数多，可以用 PP 把层分开。ZeRO/FSDP 分片的是参数状态，能与这些维度组合；MoE 再用 EP 把 experts 分给不同卡。</p><p>然后看卡之间怎样互联。TP/EP 通信频繁，更适合放在 NVLink/NVSwitch 域内；DP/PP 可以跨相对慢的网络。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>TP 为什么对高速互联敏感？</summary><div class="follow-answer"><p>每层都可能 all-reduce 或 all-gather，通信在 critical path 上。延迟和带宽会直接打到每 token latency。</p></div></details><details class="followup"><summary>PP 如何降低 bubble？</summary><div class="follow-answer"><p>增加 microbatches、1F1B 这类 schedule、virtual stages。但 microbatch 太多会增加调度和 activation 开销。</p></div></details><details class="followup"><summary>CP 与 sequence parallel 完全同义吗？</summary><div class="follow-answer"><p>不同框架术语不完全一致。一般 CP 更强调长 context 的 attention 跨设备；sequence parallel 常指把某些 activation 或 norm 按 sequence 维切开。</p></div></details></div>

---
id: sys-chunk-pd
section: systems
order: 10
level: A
title: Chunked Prefill 与 Prefill–Decode Disaggregation 在解决什么？
quick: >-
  大 prefill 会长时间占 GPU、阻塞 latency-sensitive decode。Chunked prefill 把长 prompt 分块与
  decode 混排；P/D disaggregation 则把 compute-heavy prefill 与 bandwidth-sensitive
  decode 分到不同资源池。
tags:
  - Serving
  - Prefill
  - Decode
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>大 prefill 会长时间占 GPU、阻塞 latency-sensitive decode。Chunked prefill 把长 prompt 分块与 decode 混排；P/D disaggregation 则把 compute-heavy prefill 与 bandwidth-sensitive decode 分到不同资源池。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>核心指标是 throughput、TTFT、TPOT、KV transfer cost 和资源利用率。</p><p>Disaggregation 需要把 prefill 生成的 KV 传给 decode worker；context 很长时 KV transfer 本身可能昂贵，因此网络拓扑和 cache placement 关键。Chunked prefill 不需要跨机 transfer，但同 GPU 上仍有 scheduling tradeoff。</p></div>

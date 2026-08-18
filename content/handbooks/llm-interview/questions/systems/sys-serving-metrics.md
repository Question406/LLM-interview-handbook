---
id: sys-serving-metrics
section: systems
order: 14
level: A
title: TTFT、TPOT、Throughput、Goodput 分别是什么？
quick: >-
  TTFT 是请求到第一个 token 的时间；TPOT 是后续 token 间平均时间；Throughput 是单位时间总
  tokens/requests；Goodput 是满足 latency SLO 的有效吞吐。
tags:
  - Serving
  - Metrics
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>TTFT 是请求到第一个 token 的时间；TPOT 是后续 token 间平均时间；Throughput 是单位时间总 tokens/requests；Goodput 是满足 latency SLO 的有效吞吐。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>TTFT 常受 queue + prefill；TPOT 常受 decode batch、KV/weight bandwidth；throughput 可以通过大 batching 提升但可能牺牲尾延迟。</p><p>产品比较不应只看 tokens/s。需要在给定 TTFT/TPOT SLO 下看 goodput，或画 latency-throughput frontier。</p></div>

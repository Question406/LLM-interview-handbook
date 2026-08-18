---
id: sys-cont-batch
section: systems
order: 9
level: A
title: Continuous Batching 为什么提升吞吐？
quick: >-
  不同请求生成长度不同。Static batch 中短请求完成后 slot 空等最长请求；continuous batching 在
  token/request 完成时动态加入新请求，提高 GPU 利用率。
tags:
  - Serving
  - Scheduling
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>不同请求生成长度不同。Static batch 中短请求完成后 slot 空等最长请求；continuous batching 在 token/request 完成时动态加入新请求，提高 GPU 利用率。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Serving scheduler 每个 decode iteration 重新选择 active sequences，完成的立即移出，waiting queue 的新 request 补入。</p><p>代价是更复杂的 KV block management、fairness、preemption、latency SLO；追求 throughput 过度 batching 可能恶化单请求 TPOT。</p></div>

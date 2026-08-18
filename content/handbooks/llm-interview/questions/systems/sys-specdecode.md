---
id: sys-specdecode
section: systems
order: 11
level: S
title: Speculative Decoding 为什么能保持 Target Distribution？
quick: >-
  Draft model 便宜提出多个 tokens，target model 并行验证，并通过 acceptance/rejection
  correction 使最终采样分布等价于 target policy；速度来自一次 target forward 接受多个 token。
tags:
  - Speculative Decoding
  - Inference
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Draft model 便宜提出多个 tokens，target model 并行验证，并通过 acceptance/rejection correction 使最终采样分布等价于 target policy；速度来自一次 target forward 接受多个 token。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>最直观的 greedy 情况：draft 提出 k 个 token，target 一次算出这些位置的 logits，连续接受与 target greedy 一致的前缀，遇到第一个不一致处回退 target token。</p><p>Sampling 情况不能简单“target 同意就收”，需要按 p/q acceptance probability 和 residual distribution 做校正，才能严格保持 target distribution。</p><p>Draft 越强 acceptance 越高，但 draft 自身 compute 越贵。Speedup 取决于 accepted tokens per target call、draft latency、verification batch efficiency、memory traffic。</p><p>EAGLE/MTP 类方法把 draft heads/feature prediction 集成进大模型，减少独立 draft model 开销，但训练复杂度与 acceptance quality 成为新 tradeoff。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>为什么一个很强的 draft 不一定最快？</summary><div class="follow-answer"><p>它可能接近 target compute，虽然 acceptance 高，但节省被 draft cost 抵消。</p></div></details><details class="followup"><summary>为什么 target 可以并行验证多个未来 token？</summary><div class="follow-answer"><p>Teacher-forcing 下给定 draft prefix，target 一次 forward 可同时得到这些位置的 conditional logits。</p></div></details></div>

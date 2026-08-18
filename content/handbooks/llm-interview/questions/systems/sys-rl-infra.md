---
id: sys-rl-infra
section: systems
order: 16
level: S
title: 为什么 RL Systems 比 SFT 复杂？
quick: >-
  SFT 是 dataset→forward/backward；RL 还需要 rollout
  engine、environment/verifier/RM、trajectory buffer、policy/reference/value、weight
  synchronization 与 freshness。Agent RL 再加入 sandbox/browser/API 和长 episode。
tags:
  - RL Infra
  - Post-training
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>SFT 是 dataset→forward/backward；RL 还需要 rollout engine、environment/verifier/RM、trajectory buffer、policy/reference/value、weight synchronization 与 freshness。Agent RL 再加入 sandbox/browser/API 和长 episode。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>典型 loop：current policy → rollout → reward/environment → trajectory store → trainer → new weights → sync 回 rollout workers。</p><p>瓶颈往往是 generation 而不是 backward：long-CoT / Agent rollout autoregressive、memory-bound、还要等外部 tool。Trainer 可能闲等 rollout；异步能提高利用率但带来 policy staleness。</p><p>Colocated 方案把 inference/training 在同一 GPU/节点切换，权重共享容易但资源切换复杂；disaggregated 让 rollout/trainer 独立扩容，吞吐更灵活但权重传输和版本管理更难。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>vLLM rollout 权重怎么同步？</summary><div class="follow-answer"><p>可周期性 checkpoint/load、直接 GPU/CPU tensor transfer、参数广播或共享存储；全量 100B 权重传输很贵，因此同步频率与 staleness tradeoff 关键。</p></div></details><details class="followup"><summary>异步 RL 怎么控制 trajectory age？</summary><div class="follow-answer"><p>记录 policy version，限制最大 version gap；按 age 降权/丢弃；监控 KL/logratio；或者采用更能容忍 off-policy 的算法。</p></div></details></div>

---
id: fund-onoff
section: fundamentals
order: 6
level: A
title: On-policy vs Off-policy；PPO/GRPO 为什么强调 Fresh Rollout？
quick: >-
  On-policy 用当前 policy 数据估当前 policy gradient；off-policy 用其他 behavior policy
  数据，需要 correction。LLM sequence distribution 维度极高，旧 trajectory 的 importance
  ratio 很快高方差。
tags:
  - RL
  - On-policy
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>On-policy 用当前 policy 数据估当前 policy gradient；off-policy 用其他 behavior policy 数据，需要 correction。LLM sequence distribution 维度极高，旧 trajectory 的 importance ratio 很快高方差。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>PPO/GRPO 可以在一小段时间内复用 old-policy samples，但 epoch 太多或 trainer 更新太快，ratio/clip fraction/KL 会恶化。</p><p>Off-policy 方法可以利用 replay 提高 sample efficiency，但要解决 distribution correction、value extrapolation、trajectory state mismatch；Agent 环境中更难。</p></div>

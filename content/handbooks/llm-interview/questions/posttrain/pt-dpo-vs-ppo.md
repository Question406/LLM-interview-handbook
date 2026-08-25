---
id: pt-dpo-vs-ppo
section: posttrain
order: 11
level: S
title: DPO vs PPO：真正的 tradeoff 是什么？
quick: >-
  DPO 是离线偏好优化：简单、稳，不需要显式 rollout、RM、Critic。PPO/RL 是 on-policy：系统复杂也更贵，但能持续在当前
  policy 分布上探索、优化新行为。
tags:
  - DPO
  - PPO
  - Alignment
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>DPO 是离线偏好优化：简单、稳，不需要显式 rollout、RM、Critic。PPO/RL 是 on-policy：系统复杂也更贵，但能持续在当前 policy 分布上探索、优化新行为。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>维度</th><th>DPO</th><th>PPO / On-policy RL</th></tr></thead><tbody><tr><td>数据</td><td>固定 preference pairs</td><td>当前 policy rollout</td></tr><tr><td>探索</td><td>弱，受 dataset support 限制</td><td>强，可产生新 trajectory</td></tr><tr><td>Reward</td><td>implicit preference objective</td><td>RM / verifier / environment reward</td></tr><tr><td>Critic</td><td>不需要</td><td>PPO 常需要</td></tr><tr><td>系统复杂度</td><td>接近 supervised training</td><td>rollout、reward、sync、freshness、value</td></tr><tr><td>稳定性</td><td>通常较高</td><td>更依赖超参和系统 freshness</td></tr><tr><td>适用</td><td>开放偏好、已有高质 pair</td><td>可验证 reasoning、环境交互、持续探索</td></tr></tbody></table></div><p>Reasoning RL 重新起来的一个重要原因，就是 math、code、可验证任务提供了便宜且客观的 reward。on-policy 的 search、selection、amplification 循环，可以突破固定 preference dataset 的覆盖。</p><p>两者不互斥。常见 pipeline 可以是 SFT，再到 DPO 或 preference warm start，再到 RLVR/GRPO。DPO 先把行为拉到更好的区域，RL 再在 current distribution 上探索。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>为什么 Online DPO 会出现？</summary><div class="follow-answer"><p>想保住 DPO 训练形式简单的优点，同时用当前 policy 新采的数据，缓解离线 distribution shift。</p></div></details><details class="followup"><summary>能不能 DPO 后接 GRPO？</summary><div class="follow-answer"><p>完全可以。关键是 reference 或 anchor、KL，以及数据分布怎么设计。DPO 给出较好的 initial policy，GRPO 再基于 verifier 做 on-policy 探索。</p></div></details><details class="followup"><summary>什么时候宁愿用 DPO 不用 RL？</summary><div class="follow-answer"><p>Reward 很难可靠定义、环境很贵、手上已有高质量 preference，或系统资源有限时，我更愿意先用 DPO。</p></div></details></div>

---
id: ali-ppo-dpo-grpo-ask
section: alibaba
order: 15
level: S
title: PPO 和 DPO 的主要区别？DPO 注意点？用过 GRPO 吗？
quick: >-
  DPO 用偏好对直接优化策略，无显式 RM/RL loop；PPO 先 RM 再 on-policy 优化，表达力强但复杂。DPO
  怕噪声偏好与分布过尖；GRPO 用组内相对奖励做 on-policy 更新。
tags:
  - Alibaba
  - DPO
  - GRPO
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>DPO 用偏好对直接优化策略，无显式 RM/RL loop；PPO 先 RM 再 on-policy 优化，表达力强但复杂。DPO 怕噪声偏好与分布过尖；GRPO 用组内相对奖励做 on-policy 更新。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th></th><th>DPO</th><th>PPO/RLHF</th><th>GRPO</th></tr></thead><tbody>
<tr><td>数据</td><td>preference pairs</td><td>偏好→RM + rollout</td><td>同题多样本 + reward/verifier</td></tr>
<tr><td>复杂度</td><td>低</td><td>高（四模型）</td><td>中（无 critic，要采样）</td></tr>
<tr><td>风险</td><td>噪声敏感、缺探索</td><td>RM hacking、不稳</td><td>空 group、credit 粗</td></tr>
</tbody></table></div>
<p>DPO 注意：数据质量、β、length bias、是否真提升 chosen 有用性而不只是压 rejected。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>

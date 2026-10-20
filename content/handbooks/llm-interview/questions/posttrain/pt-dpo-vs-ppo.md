---
id: pt-dpo-vs-ppo
section: posttrain
order: 11
level: S
title: DPO vs PPO：tradeoff 是什么？
quick: "DPO 用离线偏好对训练，实现较简单，通常较稳定，不需要在线采样、显式奖励模型或价值评估模型。PPO 用当前策略采样并更新，系统更复杂、成本更高，但能持续探索和改善新行为。"
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>DPO 用离线偏好对训练，实现较简单，通常较稳定，不需要在线采样、显式奖励模型或价值评估模型。PPO 用当前策略采样并更新，系统更复杂、成本更高，但能持续探索和改善新行为。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>维度</th><th>DPO</th><th>PPO / On-policy 强化学习（RL）</th></tr></thead><tbody><tr><td>数据</td><td>固定偏好对</td><td>当前策略生成的轨迹</td></tr><tr><td>探索</td><td>较弱，受已有数据覆盖范围限制</td><td>较强，可生成新轨迹</td></tr><tr><td>Reward</td><td>由偏好对定义的隐式奖励目标</td><td>奖励模型、验证器或环境奖励</td></tr><tr><td>Critic</td><td>不需要</td><td>PPO 常需要</td></tr><tr><td>系统复杂度</td><td>接近监督训练</td><td>采样、评分、参数同步、样本新鲜度和价值估计</td></tr><tr><td>稳定性</td><td>通常较高</td><td>更依赖超参数和样本是否来自足够新的策略</td></tr><tr><td>适用</td><td>开放偏好任务，已有高质量偏好对</td><td>可验证推理、环境交互和持续探索</td></tr></tbody></table></div><p>推理强化学习重新受到关注，一个原因是数学、代码等可验证任务提供了较便宜、客观的奖励。用当前策略生成候选、评分并强化高分行为，可以探索固定偏好数据未覆盖的回答。</p><p>两者不互斥。常见流程可以先做 SFT，再用 DPO 或其他偏好优化做准备，最后接 RLVR/GRPO。DPO 先改善已有行为，RL 再从当前策略生成的回答中继续探索。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>为什么 Online DPO 会出现？</summary><div class="follow-answer"><p>想保住 DPO 训练形式简单的优点，同时用当前策略新采样的数据，缓解离线数据与当前生成分布不一致的问题。</p></div></details><details class="followup"><summary>能不能 DPO 后接 GRPO？</summary><div class="follow-answer"><p>完全可以。要选好参考模型、KL 约束和数据分布。DPO 提供较好的初始策略，GRPO 再根据验证器评分生成新样本、继续探索。</p></div></details><details class="followup"><summary>什么时候宁愿用 DPO 不用 RL？</summary><div class="follow-answer"><p>奖励难以可靠定义、环境交互成本高、手上已有高质量偏好对，或系统资源有限时，我更愿意先用 DPO。</p></div></details></div>

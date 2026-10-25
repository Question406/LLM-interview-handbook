---
id: pt-dpo-vs-ppo
section: posttrain
order: 11
level: S
title: DPO vs PPO：tradeoff 是什么？
quick: "DPO 用离线偏好对训练，实现简单，通常更稳，不需要在线采样、显式奖励模型或价值评估模型。PPO 用当前策略采样再更新，系统更复杂、成本更高，但能持续探索、改进新行为。两者可以串起来用：先 DPO 改善已有行为，再接 RL 继续探索。"
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>DPO 用离线偏好对训练，实现简单，通常更稳，不需要在线采样、显式奖励模型或价值评估模型。PPO 用当前策略采样再更新，系统更复杂、成本更高，但能持续探索、改进新行为。两者可以串起来用：先 DPO 改善已有行为，再接 RL 继续探索。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>核心取舍是拿探索能力换简单和稳定。DPO 像监督训练一样在固定偏好对上学，便宜也稳，但只能在已有数据覆盖的范围里改；PPO 要自己采样、打分、更新，系统重得多，换来的是能探索固定数据里没有的回答。几个维度对照如下：</p><div class="table-wrap"><table><thead><tr><th>维度</th><th>DPO</th><th>PPO / On-policy 强化学习（RL）</th></tr></thead><tbody><tr><td>数据</td><td>固定偏好对</td><td>当前策略生成的轨迹</td></tr><tr><td>探索</td><td>较弱，受已有数据覆盖范围限制</td><td>较强，可生成新轨迹</td></tr><tr><td>Reward</td><td>由偏好对定义的隐式奖励目标</td><td>奖励模型、验证器或环境奖励</td></tr><tr><td>Critic</td><td>不需要</td><td>PPO 常需要</td></tr><tr><td>系统复杂度</td><td>接近监督训练</td><td>采样、评分、参数同步、样本新鲜度和价值估计</td></tr><tr><td>稳定性</td><td>通常较高</td><td>更依赖超参数和样本是否来自足够新的策略</td></tr><tr><td>适用</td><td>开放偏好任务，已有高质量偏好对</td><td>可验证推理、环境交互和持续探索</td></tr></tbody></table></div><p>推理强化学习重新受到关注，一个原因是数学、代码这类可验证任务提供了便宜又客观的奖励。比如一道数学题，用当前策略生成几个候选，对答案打分，再强化高分的那个，就能探索到固定偏好数据里没覆盖的解法。</p><p>两者也可以串起来用。常见流程是先做 SFT，再用 DPO 或其他偏好优化打底，最后接 RLVR/GRPO。DPO 先把已有行为改好，RL 再从当前策略生成的回答里继续探索。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>为什么 Online DPO 会出现？</summary><div class="follow-answer"><p>想保留 DPO 训练形式简单的好处，同时改用当前策略新采样的数据，缓解离线数据和当前生成分布对不上的问题。</p></div></details><details class="followup"><summary>能不能 DPO 后接 GRPO？</summary><div class="follow-answer"><p>完全可以，要选好参考模型、KL 约束和数据分布。DPO 提供一个比较好的初始策略，GRPO 再根据验证器的评分生成新样本、继续探索。</p></div></details><details class="followup"><summary>什么时候宁愿用 DPO 不用 RL？</summary><div class="follow-answer"><p>奖励很难可靠定义、环境交互成本高、手上已经有高质量偏好对，或者系统资源有限的时候，我会先用 DPO。</p></div></details></div>

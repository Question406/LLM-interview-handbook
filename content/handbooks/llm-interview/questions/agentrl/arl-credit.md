---
id: arl-credit
section: agentrl
order: 4
level: S
title: 最终只有一个 Outcome Reward，50-step Agent 怎么做 Credit Assignment？
quick: "把最终奖励分配给所有 token 可以训练，但方差大，也难分清每一步的贡献。可以用过程奖励、Critic/TD、事后分析或反事实比较来细化归因，也可以只强化关键步骤，或按对话轮次、动作边界优化策略。"
tags:
  - Credit Assignment
  - Agent RL
  - 真题
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ 淘天 Agent 面经
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>把最终奖励分配给所有 token 可以训练，但方差大，也难分清每一步的贡献。可以用过程奖励、Critic/TD、事后分析或反事实比较来细化归因，也可以只强化关键步骤，或按对话轮次、动作边界优化策略。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>最粗的做法：整条 trajectory $\tau$ 给一个 $R(\tau)$，所有 policy token 或 action 共用同一个 advantage。关键做对的 step、无关废话、甚至差点搞砸的 step，会被一起奖励。</p><p>常见方向：</p><ol><li><b>Process reward：</b>为中间步骤打分，提供更密集的信号，但步骤评分器可能有偏差。</li><li><b>Critic / TD：</b>学习 $V(s_t)$，用 future return 差异构造 step advantage。</li><li><b>Hindsight：</b>一轮任务完成后，利用完整的后续证据重新判断中间动作的贡献。</li><li><b>Counterfactual：</b>在关键 state 采 alternate actions，比较后续 success，估局部 Q 差异。</li><li><b>Step selection：</b>只强化信息量大或影响关键决策的步骤。</li><li><b>Action-aligned optimization：</b>让价值估计、概率比和裁剪操作与实际环境状态变化的边界对齐。</li></ol><p>credit estimator 要回答的是：这个 state 本来就容易成功，还是这个 action 真的提高了成功概率？</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>PRM 与 Critic 区别？</summary><div class="follow-answer"><p>PRM 更像逐步对不对、有没有帮助的 reward；Critic 是在当前 policy 下，从某个 state 出发的 expected future return。</p></div></details><details class="followup"><summary>Step reward 会不会增加 hacking？</summary><div class="follow-answer"><p>会。每增加一种密集的塑形奖励，就多一种被策略钻空子的机会。因此还要用最终结果约束、独立校验，并通过奖励消融检查效果。</p></div></details><details class="followup"><summary>Counterfactual 采样轨迹（rollout） 太贵怎么办？</summary><div class="follow-answer"><p>只在不确定性高、且动作对结果影响较大的状态上尝试不同分支；用学到的 价值评估模型（critic） 或 uncertainty 挑关键 state，或者离线复用相似 states。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 面经</a></div>

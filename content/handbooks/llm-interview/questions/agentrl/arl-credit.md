---
id: arl-credit
section: agentrl
order: 4
level: S
title: 最终只有一个 Outcome Reward，50-step Agent 怎么做 Credit Assignment？
quick: >-
  把最终 reward 广播给所有 token，能训，但方差大、credit 很粗。更好的做法有 process
  reward、critic/TD、hindsight 或 counterfactual 归因、挑 step、以及按 turn 或 action 做
  policy 优化。
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>把最终 reward 广播给所有 token，能训，但方差大、credit 很粗。更好的做法有 process reward、critic/TD、hindsight 或 counterfactual 归因、挑 step、以及按 turn 或 action 做 policy 优化。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>最粗的做法：整条 trajectory $\tau$ 给一个 $R(\tau)$，所有 policy token 或 action 共用同一个 advantage。关键做对的 step、无关废话、甚至差点搞砸的 step，会被一起奖励。</p><p>常见方向：</p><ol><li><b>Process reward：</b>为中间 step 打分，信号 dense，但 step grader 可能有 bias。</li><li><b>Critic / TD：</b>学习 $V(s_t)$，用 future return 差异构造 step advantage。</li><li><b>Hindsight：</b>episode 完成后利用完整未来证据重新判断中间 action 的贡献。</li><li><b>Counterfactual：</b>在关键 state 采 alternate actions，比较后续 success，估局部 Q 差异。</li><li><b>Step selection：</b>只强化 high-information / decision-critical steps。</li><li><b>Action-aligned optimization：</b>让 value/ratio/clipping 与实际 environment transition boundary 对齐。</li></ol><p>credit estimator 要回答的是：这个 state 本来就容易成功，还是这个 action 真的提高了成功概率？</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>PRM 与 Critic 区别？</summary><div class="follow-answer"><p>PRM 更像逐步对不对、有没有帮助的 reward；Critic 是在当前 policy 下，从某个 state 出发的 expected future return。</p></div></details><details class="followup"><summary>Step reward 会不会增加 hacking？</summary><div class="follow-answer"><p>会。每个 dense shaping signal 都多一块可被刷的表面，所以还要有最终 outcome 当锚、独立校验，以及 reward ablation。</p></div></details><details class="followup"><summary>Counterfactual rollout 太贵怎么办？</summary><div class="follow-answer"><p>只在不确定性高、杠杆也高的 state 上做 branching；用学到的 critic 或 uncertainty 挑关键 state，或者离线复用相似 states。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 面经</a></div>

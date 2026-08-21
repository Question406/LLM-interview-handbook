---
id: arl-credit
section: agentrl
order: 4
level: S
title: 最终只有一个 Outcome Reward，50-step Agent 怎么做 Credit Assignment？
quick: >-
  把 final reward 广播给所有 token 能训练但方差高、credit 粗。更好的方法包括 process
  reward、critic/TD、hindsight/counterfactual attribution、step
  selection、turn/action-level policy optimization。
tags:
  - Credit Assignment
  - Agent RL
  - 真题
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天 Agent 面经
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>把 final reward 广播给所有 token 能训练但方差高、credit 粗。更好的方法包括 process reward、critic/TD、hindsight/counterfactual attribution、step selection、turn/action-level policy optimization。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>最粗做法：对整个 trajectory $\tau$ 给 $R(\tau)$，所有 policy token/action 共享同一个 advantage。这会把关键正确 step、无关废话、甚至差点导致失败的 step 一起奖励。</p><p>常见方向：</p><ol><li><b>Process reward：</b>为中间 step 打分，信号 dense，但 step grader 可能有 bias。</li><li><b>Critic / TD：</b>学习 $V(s_t)$，用 future return 差异构造 step advantage。</li><li><b>Hindsight：</b>episode 完成后利用完整未来证据重新判断中间 action 的贡献。</li><li><b>Counterfactual：</b>在关键 state 采 alternate actions，比较后续 success，估局部 Q 差异。</li><li><b>Step selection：</b>只强化 high-information / decision-critical steps。</li><li><b>Action-aligned optimization：</b>让 value/ratio/clipping 与实际 environment transition boundary 对齐。</li></ol><p>真正的核心是：credit estimator 要回答“这个 state 本来就容易成功，还是这个 action 真正提高了成功概率？”</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>PRM 与 Critic 区别？</summary><div class="follow-answer"><p>PRM 更像 step correctness/helpfulness reward；Critic 是在当前 policy 下从 state 出发的 expected future return。</p></div></details><details class="followup"><summary>Step reward 会不会增加 hacking？</summary><div class="follow-answer"><p>会。每个 dense shaping signal 都新增 proxy surface，所以需要 final outcome anchor、独立校验和 reward ablation。</p></div></details><details class="followup"><summary>Counterfactual rollout 太贵怎么办？</summary><div class="follow-answer"><p>只在高 uncertainty / high leverage states 做 branching；用 learned critic/uncertainty 选关键 state，或 offline reuse 相似 states。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 面经</a></div>

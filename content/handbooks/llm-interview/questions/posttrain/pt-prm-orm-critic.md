---
id: pt-prm-orm-critic
section: posttrain
order: 21
level: S
title: Outcome Reward、Process Reward、PRM 与 Critic 有什么区别？
quick: >-
  ORM/Outcome reward 只评价最终结果；Process reward/PRM 给中间 reasoning step 质量信号；Critic
  不是“步骤正确性评分器”，而是当前 policy 下从 state 出发的 expected future return。
tags:
  - Reward
  - PRM
  - Credit Assignment
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>ORM/Outcome reward 只评价最终结果；Process reward/PRM 给中间 reasoning step 质量信号；Critic 不是“步骤正确性评分器”，而是当前 policy 下从 state 出发的 expected future return。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>对象</th><th>典型输出</th><th>回答的问题</th></tr></thead><tbody><tr><td>Outcome reward / ORM</td><td>R(trajectory) 或 r(x,y)</td><td>最后成功了吗？</td></tr><tr><td>Process reward / PRM</td><td>r_t 或 step score</td><td>这一步本身是否正确/有帮助？</td></tr><tr><td>Critic</td><td>V^π(s_t)</td><td>从当前 state 按当前 policy 继续，未来期望回报多少？</td></tr></tbody></table></div><p>PRM 能让 sparse outcome reward 变 dense，但代价是“正确过程”本身难标、可能不唯一，而且 step grader 也能被 hack。Critic 不需要每一步有人工 correctness label，它通过 return/TD target 学 future value，但会有 bootstrap error。</p><p>Agent RL 里经常同时需要：final environment outcome 作为最接近真实目标的 anchor；critic 处理 credit；某些安全/格式/process reward 只作为辅助。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>PRM 一定比 ORM 好吗？</summary><div class="follow-answer"><p>不一定。PRM 提供 dense credit，但错误过程标签会把错误 inductive bias 直接写进 policy；ORM 简洁客观但稀疏。</p></div></details><details class="followup"><summary>Critic 能不能从 PRM 学？</summary><div class="follow-answer"><p>可以把 process rewards 纳入 return target，但 critic 估计的是累计 future return，不等于单步 PRM 分数。</p></div></details></div>

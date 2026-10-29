---
id: arl-credit
section: agentrl
order: 4
level: S
title: 最终只有一个 Outcome Reward，50-step Agent 怎么做 Credit Assignment？
quick: 假设 Agent 做了 50 步，最后成功，但其中 20 次搜索没有帮助。只有最终成功奖励时，训练很难直接知道哪一步真正促成了结果。
tags:
  - Credit Assignment
  - Agent RL
  - 真题
  - 口述改写 2026-10-28
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources:
  - title: ↗ 淘天 Agent 面经
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---
<h2>回答思路</h2>
<blockquote>
<p><strong>问题与场景：</strong> 假设 Agent 做了 50 步，最后成功，但其中 20 次搜索没有帮助。</p>
<p><strong>做法与原因：</strong> 我会先用 return 或 advantage 给动作提供学习信号，再考虑 value baseline、可验证的中间事件，或从关键状态重跑的对照。</p>
<p><strong>检查与取舍：</strong> 过程奖励必须对应真实进展。</p>
</blockquote>
<h2>可以这样回答</h2>
<p>假设 Agent 做了 50 步，最后成功，但其中 20 次搜索没有帮助。只有最终成功奖励时，训练很难直接知道哪一步真正促成了结果。</p>
<p>我会先用 return 或 advantage 给动作提供学习信号，再考虑 value baseline、可验证的中间事件，或从关键状态重跑的对照。Value model 能降低估计噪声，但不会自动证明某一步对最终成功有因果贡献。</p>
<p>过程奖励必须对应真实进展。若只奖励“调用了工具”，模型可能学会反复调用；因此还要看最终成功、调用成本和失败后的恢复。</p>

<details class="design-reference"><summary>展开技术备查：原始说明、公式与实验细节</summary>
<div class="quick"><div class="mini-title">30 秒回答</div><p>可以把最终奖励分给所有 token 来训，但方差大，分不清每一步的贡献。要细化归因，可以用过程奖励、Critic/TD、事后重估或反事实比较，也可以只强化关键步骤，或按对话轮次、action boundaries 优化策略。核心是分清这个状态本来就容易成功，还是这个动作真的提高了成功概率。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>能训，但最粗的做法方差很大：整条 trajectory $\tau$ 只有一个 $R(\tau)$，所有 policy token 或 action 共用同一个 advantage，关键做对的 step、无关的废话、甚至差点搞砸的 step，都会被一起奖励。要把功劳分细，我会在过程奖励、Critic / TD、事后重估、反事实比较里挑，或者只强化关键步骤、按 action boundaries 做优化。</p><p>比如 50 步里，有一步选对了查询工具，另一步差点删错文件、侥幸没出事，最后任务成功了。共用一个 advantage 的话，这两步拿到的是一样的正信号。</p><p>几个方向各有代价。过程奖励（Process reward）给中间步骤打分，信号更密集，但步骤评分器本身可能有偏差。Critic / TD 学 $V(s_t)$，用 future return 的差异构造 step advantage。Hindsight 在一轮任务完成后，利用完整的后续证据重新判断中间动作的贡献。Counterfactual 在关键 state 采几个 alternate actions，比较后续的 success，估局部的 Q 差异。Step selection 只强化信息量大、或者影响关键决策的步骤。Action-aligned optimization 让价值估计、概率比和裁剪操作对齐实际 environment state transitions。</p><p>不管选哪个，credit estimator 要回答的都是同一个问题：这个 state 本来就容易成功，还是这个 action 真的提高了成功概率？</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>PRM 和 Critic 有什么区别？</summary><div class="follow-answer"><p>PRM 更像逐步的 reward，看这一步对不对、有没有帮助；Critic 估的是在当前 policy 下，从某个 state 出发的 expected future return。</p></div></details><details class="followup"><summary>Step reward 会不会增加 hacking？</summary><div class="follow-answer"><p>会。每多一种密集的塑形奖励，策略就多一个钻空子的地方，所以还要用最终结果约束、做独立校验，并通过奖励 ablation 检查效果。</p></div></details><details class="followup"><summary>Counterfactual sampling 轨迹（rollout） 太贵怎么办？</summary><div class="follow-answer"><p>只在不确定性高、动作对结果影响大的状态上试不同分支。可以用学到的价值评估模型（critic）或 uncertainty 挑关键 state，也可以离线复用相似的 states。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 面经</a></div>

</details>

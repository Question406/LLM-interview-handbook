---
id: arl-action-granularity
section: agentrl
order: 3
level: S
title: Agent 的 Action 粒度应该是 token、completion、tool-call 还是 semantic step？
quick: >-
  没有统一答案。Action granularity 应尽量与 environment transition、reward attribution 和
  optimization unit 对齐。Token-level 方便复用 LM 训练，但环境通常只在完整 tool action 后发生语义变化。
tags:
  - Agent RL
  - Credit Assignment
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>没有统一答案。Action granularity 应尽量与 environment transition、reward attribution 和 optimization unit 对齐。Token-level 方便复用 LM 训练，但环境通常只在完整 tool action 后发生语义变化。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>粒度</th><th>优点</th><th>问题</th></tr></thead><tbody><tr><td>Token</td><td>直接复用 autoregressive logprobs / PPO</td><td>一个 tool action 被拆成很多 token，共享同样 environment consequence</td></tr><tr><td>Completion / turn</td><td>与一次模型调用一致</td><td>一个 turn 可能同时含 thinking + action</td></tr><tr><td>Tool call</td><td>接近真实 environment transition</td><td>tool arguments 内部 credit 仍细粒度</td></tr><tr><td>Semantic step</td><td>最符合高层决策</td><td>边界难自动定义、logprob aggregation 复杂</td></tr></tbody></table></div><p>粒度会决定 critic 在哪里估、importance ratio 怎么聚合、clip 到哪个 unit、reward 如何传播。Agent RL 近年的一条主线正是从“所有 token 一个 outcome advantage”转向 step/action-aligned optimization。</p><p>一个实用折中：policy 仍在 token level parameterize，但 advantage/value 在 action/turn boundary 估计，然后把同一个 action-level advantage broadcast 到属于该 action 的 policy tokens。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Tool arguments 应视为一个 action 吗？</summary><div class="follow-answer"><p>Environment 通常只有完整参数解析成功后才 transition，因此语义上是一个 action；但 token-level gradient 仍可在 action 内分配。</p></div></details><details class="followup"><summary>Think+tool call 同一 completion 怎么办？</summary><div class="follow-answer"><p>可把 completion 分 segment：internal reasoning、structured action；value 在执行前后 boundary 估，policy loss 只覆盖模型生成 token。</p></div></details></div>

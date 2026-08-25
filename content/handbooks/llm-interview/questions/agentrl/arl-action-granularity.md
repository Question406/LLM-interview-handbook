---
id: arl-action-granularity
section: agentrl
order: 3
level: S
title: Agent 的 Action 粒度应该是 token、completion、tool-call 还是 semantic step？
quick: >-
  没有统一答案。Action 粒度尽量跟 environment transition、reward 怎么归因、以及优化单元对齐。Token-level
  方便复用 LM 训练，但环境通常要等完整 tool action 之后，语义才真正变。
tags:
  - Agent RL
  - Credit Assignment
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>没有统一答案。Action 粒度尽量跟 environment transition、reward 怎么归因、以及优化单元对齐。Token-level 方便复用 LM 训练，但环境通常要等完整 tool action 之后，语义才真正变。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>粒度</th><th>优点</th><th>问题</th></tr></thead><tbody><tr><td>Token</td><td>直接复用 autoregressive logprobs / PPO</td><td>一个 tool action 被拆成很多 token，共享同样 environment consequence</td></tr><tr><td>Completion / turn</td><td>与一次模型调用一致</td><td>一个 turn 可能同时含 thinking + action</td></tr><tr><td>Tool call</td><td>接近真实 environment transition</td><td>tool arguments 内部 credit 仍细粒度</td></tr><tr><td>Semantic step</td><td>最符合高层决策</td><td>边界难自动定义、logprob aggregation 复杂</td></tr></tbody></table></div><p>粒度会决定 critic 在哪估、importance ratio 怎么聚合、clip 作用到哪个 unit、reward 怎么往后传。Agent RL 这几年有一条主线，就是从「所有 token 共用一个 outcome advantage」转向按 step 或 action 对齐的优化。</p><p>一个能用的折中：policy 仍在 token 上参数化，advantage 和 value 在 action 或 turn 边界上估，再把同一个 action-level advantage broadcast 到属于这个 action 的 policy tokens。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Tool arguments 应视为一个 action 吗？</summary><div class="follow-answer"><p>环境通常要等参数解析成功才 transition，语义上是一个 action；但 action 内部仍可按 token 分梯度。</p></div></details><details class="followup"><summary>Think+tool call 同一 completion 怎么办？</summary><div class="follow-answer"><p>可以把 completion 切成段：内部 reasoning、structured action。value 在执行前后的边界上估，policy loss 只覆盖模型自己生成的 token。</p></div></details></div>

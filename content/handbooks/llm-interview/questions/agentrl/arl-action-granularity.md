---
id: arl-action-granularity
section: agentrl
order: 3
level: S
title: Agent 的 Action 粒度应该是 token、completion、tool-call 还是 semantic step？
quick: "动作粒度应对应环境怎样变化、奖励怎样归因，以及训练怎样更新。按 token 定义便于复用语言模型训练，但外部环境通常在完整工具调用解析并执行后才改变。可以在 action 或 turn 边界估计优势，再分配给对应的策略 token。"
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>动作粒度应对应环境怎样变化、奖励怎样归因，以及训练怎样更新。按 token 定义便于复用语言模型训练，但外部环境通常在完整工具调用解析并执行后才改变。可以在 action 或 turn 边界估计优势，再分配给对应的策略 token。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>粒度</th><th>优点</th><th>问题</th></tr></thead><tbody><tr><td>Token</td><td>直接复用 autoregressive logprobs / PPO</td><td>一个 tool action 被拆成很多 文本处理单位（token），共享同样 environment consequence</td></tr><tr><td>Completion / turn</td><td>与一次模型调用一致</td><td>一个 turn 可能同时含 thinking + action</td></tr><tr><td>Tool call</td><td>接近真实 environment transition</td><td>tool arguments 内部 credit 仍细粒度</td></tr><tr><td>Semantic step</td><td>最符合高层决策</td><td>边界难自动定义、logprob aggregation 复杂</td></tr></tbody></table></div><p>动作粒度会决定 critic 在哪些边界估值、重要性比率怎样聚合、clip 约束哪个单元，以及奖励怎样传回之前的决策。Agent 强化学习（RL） 这几年有一条主线，就是从「所有 token 共用一个 outcome advantage」转向按 step 或 action 对齐的优化。</p><p>一种折中做法是：策略仍逐 token 生成，在 action 或 turn 边界估计优势和价值，再把同一动作的优势分配给这个动作内由策略生成的 token。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Tool arguments 应视为一个 action 吗？</summary><div class="follow-answer"><p>环境通常在参数解析并执行后才改变状态，因此语义上可以视为一个动作；训练梯度仍可以按其中的 token 计算。</p></div></details><details class="followup"><summary>Think+工具调用 同一 completion 怎么办？</summary><div class="follow-answer"><p>可以把 completion 切成推理和结构化动作两段。价值在动作执行前后估计，策略 loss 只覆盖模型自己生成的 token。</p></div></details></div>

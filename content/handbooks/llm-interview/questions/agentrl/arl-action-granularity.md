---
id: arl-action-granularity
section: agentrl
order: 3
level: S
title: Agent 的 Action 粒度应该是 token、completion、tool-call 还是 semantic step？
quick: "动作粒度要对齐环境在哪里变化：外部状态通常在一次工具调用解析并执行后才改变，所以在 action 或 turn 边界估计优势和价值，再分给这个动作里由策略生成的 token。生成和梯度仍按 token 走，便于复用语言模型训练。"
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>动作粒度要对齐环境在哪里变化：外部状态通常在一次工具调用解析并执行后才改变，所以在 action 或 turn 边界估计优势和价值，再分给这个动作里由策略生成的 token。生成和梯度仍按 token 走，便于复用语言模型训练。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>我会让动作粒度对齐环境在哪里变化。外部环境通常要等一次工具调用解析完、执行了才改变状态，所以在 action 或 turn 边界估计优势和价值，再把这份优势分给该动作里由策略生成的 token。策略仍然逐 token 生成，梯度也按 token 算，这样能直接复用语言模型的训练。</p><p>比如模型写了几十个 token 的工具参数，环境要等整段参数解析完、工具执行了才返回结果。这几十个 token 共享同一个环境后果，按 token 一个个估值意义不大；可要是把整段对话轮次当一个动作，里面又可能同时混着思考和动作。四种粒度的取舍放在下面这张表里。</p><div class="table-wrap"><table><thead><tr><th>粒度</th><th>优点</th><th>问题</th></tr></thead><tbody><tr><td>Token</td><td>直接复用 autoregressive logprobs / PPO</td><td>一个 tool action 被拆成很多 文本处理单位（token），共享同样 environment consequence</td></tr><tr><td>Completion / turn</td><td>与一次模型调用一致</td><td>一个 turn 可能同时含 thinking + action</td></tr><tr><td>Tool call</td><td>接近真实 environment transition</td><td>tool arguments 内部 credit 仍细粒度</td></tr><tr><td>Semantic step</td><td>最符合高层决策</td><td>边界难自动定义、logprob aggregation 复杂</td></tr></tbody></table></div><p>粒度选在哪，会决定 critic 在哪些边界估值、重要性比率怎么聚合、clip 约束哪个单元，以及奖励怎样传回之前的决策。Agent 强化学习（RL）这几年有一条主线，就是从「所有 token 共用一个 outcome advantage」转向按 step 或 action 对齐的优化。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Tool arguments 应该算一个 action 吗？</summary><div class="follow-answer"><p>可以。环境通常在参数解析并执行后才改变状态，语义上它就是一个动作；训练梯度仍然可以按其中的 token 计算。</p></div></details><details class="followup"><summary>思考和工具调用在同一个 completion 里怎么办？</summary><div class="follow-answer"><p>把 completion 切成推理和结构化动作两段。价值在动作执行前后估计，策略 loss 只覆盖模型自己生成的 token。</p></div></details></div>

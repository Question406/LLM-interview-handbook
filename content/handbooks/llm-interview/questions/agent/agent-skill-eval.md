---
id: agent-skill-eval
section: agent
order: 9
level: S
title: 怎么评估一个 Agent Skill 写得好不好？
quick: >-
  不要只看 Skill 内容是否“合理”。做 no-skill / metadata-only / full-skill / optimized-skill
  ablation，测 task success、tokens、tool calls、latency、robustness 与 interference。
tags:
  - Skill
  - Eval
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>不要只看 Skill 内容是否“合理”。做 no-skill / metadata-only / full-skill / optimized-skill ablation，测 task success、tokens、tool calls、latency、robustness 与 interference。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>理想评测是同一组 tasks、同一模型/harness，只改变 Skill 条件：</p><div class="table-wrap"><table><thead><tr><th>条件</th><th>目的</th></tr></thead><tbody><tr><td>No skill</td><td>基础能力</td></tr><tr><td>Metadata only</td><td>检索/触发是否本身有提示效应</td></tr><tr><td>Full skill</td><td>Skill 的真实增益</td></tr><tr><td>Full skill + distractors</td><td>抗干扰能力</td></tr><tr><td>Old/new version</td><td>版本回归</td></tr></tbody></table></div><p>还要测 negative transfer：Skill 对目标任务提升 10%，但对相邻任务误触发后伤害 20%，并不是好 Skill。</p><p>效率指标可以用 success per token / per tool-call / per latency；程序性 Skill 的价值常在“减少无效探索”而不只是提高最终 accuracy。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>如何判断 Skill 只是把答案泄漏进去？</summary><div class="follow-answer"><p>用 held-out instances、task parameterization、隐藏答案和不同 domain variants；Skill 应描述 procedure 而不是 benchmark-specific solution。</p></div></details><details class="followup"><summary>不同模型对同一 Skill 效果不同怎么办？</summary><div class="follow-answer"><p>把 Skill 看成 model-conditioned artifact；可做 model-specific variants，或写得更结构化/可执行以降低语言理解差异。</p></div></details></div>

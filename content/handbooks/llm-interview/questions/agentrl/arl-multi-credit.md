---
id: arl-multi-credit
section: agentrl
order: 8
level: S
title: Multi-Agent RL 的 Credit Assignment 为什么更难？
quick: >-
  最终 team reward 同时由 orchestrator 的 decomposition、worker 的执行和信息共享决定；所有 agent
  同时更新还会让环境非平稳，因此“谁贡献了多少”更难识别。
tags:
  - Multi-Agent RL
  - Credit Assignment
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ Kimi K2.5
    url: 'https://arxiv.org/abs/2602.02276'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>最终 team reward 同时由 orchestrator 的 decomposition、worker 的执行和信息共享决定；所有 agent 同时更新还会让环境非平稳，因此“谁贡献了多少”更难识别。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>假设 orchestrator A 调 workers B/C/D，最终成功 R=1。Credit 可能来自 A 的正确拆分、B 找到关键资料、C 写对代码，也可能 D 基本无用。给所有 token 同一个 +1 会严重混淆。</p><p>简化方案之一：冻结 workers，只训练 orchestrator，把 workers 当环境能力；另一种是 alternating training，分阶段更新 orchestrator 与 workers。</p><p>更一般可借鉴 multi-agent RL 的 centralized critic、difference reward、counterfactual baseline，但 LLM agents 的 action space、通信文本和长 context 使成本更高。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>冻结 workers 的缺点？</summary><div class="follow-answer"><p>workers 能力不上升，而且 orchestrator 训练后可能 overfit 固定 worker behavior；换 worker 产生 distribution shift。</p></div></details><details class="followup"><summary>如何给 individual reward？</summary><div class="follow-answer"><p>可按 subtask verifier、artifact quality、downstream usefulness 打局部 reward；但要防局部指标与 team objective 不一致。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2602.02276" target="_blank" rel="noopener noreferrer">↗ Kimi K2.5</a></div>

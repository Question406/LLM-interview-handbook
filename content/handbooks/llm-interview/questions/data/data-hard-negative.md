---
id: data-hard-negative
section: data
order: 2
level: S
title: Preference Data 怎么构造 Hard Negative？
quick: >-
  高价值 rejected 应该 plausible but wrong，而不是“我不知道”。最好只在一个关键维度上比 chosen 差，让模型学真正
  decision boundary，同时控制长度、风格等 confound。
tags:
  - Preference Data
  - Hard Negative
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>高价值 rejected 应该 plausible but wrong，而不是“我不知道”。最好只在一个关键维度上比 chosen 差，让模型学真正 decision boundary，同时控制长度、风格等 confound。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>最简单的 negative 太容易：chosen 是完整正确答案，rejected 是“我不知道”。这种 pair 主要教模型避免废话，无法学习 subtle correctness。更有效的 hard negative 可以是：</p><ul><li>只错一个 reasoning step；</li><li>事实主体/时间/单位有细微错误；</li><li>代码整体正确但有边界 case bug；</li><li>tool 选对但 argument 错；</li><li>回答正确但违反用户格式/安全约束；</li><li>Agent 轨迹只在一个关键 decision 上选错文件/工具。</li></ul><p>还要控制 nuisance features。如果所有 chosen 都更长，模型可能学“长=好”；如果 rejected 总有奇怪语气，模型可能只学 style classifier。可以做 length-matched pairs、counterexample pairs、多维 rubric 与 pair difficulty 分桶。</p><p>Annotator disagreement 不一定要强行二值化。可以保留 tie、soft preference probability、多维评分，或者对高 disagreement 样本降低权重。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>如何构造 Agent trajectory negative？</summary><div class="follow-answer"><p>从成功轨迹复制，只替换一个关键 action，例如错误 repo 文件、错误 tool argument、过早 terminate；保持前后上下文相似，使 credit 集中。</p></div></details><details class="followup"><summary>Hard negative 太难会怎样？</summary><div class="follow-answer"><p>若人类/judge 自己都难稳定区分，会引入 label noise；所以要同时看 pair margin、annotator agreement 和 verifier confidence。</p></div></details></div>

---
id: data-teacher-bias
section: data
order: 11
level: A
title: Synthetic Data 的 Teacher Bias 怎么检测？
quick: >-
  比较不同 teacher/temperature/prompt 生成的数据在 style、length、错误类型、n-gram、reasoning
  pattern 上的分布，并用 cross-teacher / human / verifier 做独立评价；最终用 student ablation
  看是否把 teacher shortcut 蒸馏进去。
tags:
  - Synthetic Data
  - Distillation
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>比较不同 teacher/temperature/prompt 生成的数据在 style、length、错误类型、n-gram、reasoning pattern 上的分布，并用 cross-teacher / human / verifier 做独立评价；最终用 student ablation 看是否把 teacher shortcut 蒸馏进去。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>常见 teacher bias：过度 verbose、固定 headings、过度安全拒答、特定代码风格、同一种 reasoning 模板、事实 hallucination。可以训练 classifier 识别 teacher source，若过于容易说明数据有强风格 signature。</p><p>最可靠的判断仍是 downstream：同样 token budget 下，teacher-A data 与 teacher-B/mixed/human data 训练出的 student 在 target distribution 上是否更好，是否出现 style collapse 或 OOD regression。</p></div>

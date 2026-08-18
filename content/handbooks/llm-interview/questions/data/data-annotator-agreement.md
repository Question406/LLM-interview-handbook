---
id: data-annotator-agreement
section: data
order: 13
level: S
title: 偏好标注者分歧很大时，应该删数据、投票，还是保留不确定性？
quick: >-
  先分辨分歧来自任务本身、rubric、标注者能力还是界面/位置偏差。简单多数投票会丢掉不确定性；更稳妥的是记录重复标注、pair confidence
  和分层一致性，并把低一致性样本用于诊断或软标签。
tags:
  - Preference Data
  - Annotation
  - Quality
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: RewardBench
    url: 'https://arxiv.org/abs/2403.13787'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>分歧不是自动等于“脏数据”。它可能暴露任务描述模糊、正确答案不唯一，或某一维度（安全、简洁、事实性）没有被 rubric 明确约束。</p><ul><li><b>先测量：</b>在同一批锚点上做重复标注，按任务/语言/难度/标注者分层看 agreement，而不是只报一个总准确率。</li><li><b>再处理：</b>高置信一致样本可作强监督；低置信但有价值的边界样本可保留为软偏好、降低权重，或进入人工 adjudication。</li><li><b>最后闭环：</b>回看判别依据，补充 rubric 和反例；若不同标注者代表不同产品偏好，应先明确产品目标，而不是让模型平均所有人。</li></ul><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://arxiv.org/abs/2403.13787" target="_blank" rel="noreferrer">RewardBench</a></div></div>

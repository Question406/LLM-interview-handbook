---
id: fund-calibration
section: fundamentals
order: 19
level: S
title: 模型 Accuracy 很高但 Calibration 很差，产品决策会出什么问题？
quick: >-
  准确率只计对错，不检查置信度是否可信。若 0.9 置信度的样本实际只对 0.6，基于阈值的拒答、人工转交、风险控制和 best-of-N
  都会系统性误判；应结合 reliability、Brier/log loss 与业务成本选阈值。
tags:
  - Calibration
  - ML
  - Decision
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: Calibration paper
    url: 'https://arxiv.org/abs/1706.04599'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>Calibration 问的是“模型说 80% 时，长期来看是否真的约 80% 正确”。两个模型 accuracy 相同，过度自信的那个在高风险自动化里通常更危险。</p><ul><li><b>测量：</b>reliability diagram、ECE（注意分桶敏感）、Brier score 和 NLL；按领域、难度、语言和时间切片。</li><li><b>决策：</b>阈值应由错误成本决定。例如高风险写操作需要更高置信度，还可能需要独立 verifier；不能把 0.5 当通用边界。</li><li><b>修复：</b>温度缩放等后校准可改善概率解释，但不能补回 OOD 知识；校准数据必须独立且持续更新。</li></ul><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://arxiv.org/abs/1706.04599" target="_blank" rel="noreferrer">Calibration paper</a></div></div>

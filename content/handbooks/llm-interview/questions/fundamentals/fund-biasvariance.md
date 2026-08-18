---
id: fund-biasvariance
section: fundamentals
order: 10
level: A
title: Bias–Variance Tradeoff 在 RL 中有哪些具体例子？
quick: >-
  MC return 低 bootstrap bias 高 variance；TD/GAE 用 value 降 variance 引入
  bias；importance weight clipping、reward normalization、group normalization也都在
  estimator variance 与 objective distortion 之间折中。
tags:
  - RL
  - Statistics
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>MC return 低 bootstrap bias 高 variance；TD/GAE 用 value 降 variance 引入 bias；importance weight clipping、reward normalization、group normalization也都在 estimator variance 与 objective distortion 之间折中。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>RL 很多“稳定 trick”本质是在主动接受一些 bias 换更低 variance。面试时最好指出：所谓 unbiased estimator 如果 variance 高到训练不可用，也未必工程上更优。</p><p>反过来，过度 normalization/clipping 虽稳定，但可能悄悄改变你在优化的 length/difficulty weighting。</p></div>

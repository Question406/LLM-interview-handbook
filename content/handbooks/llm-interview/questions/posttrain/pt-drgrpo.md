---
id: pt-drgrpo
section: posttrain
order: 18
level: S
title: Dr.GRPO 认为 vanilla GRPO 有哪些 bias？
quick: >-
  核心讨论包括 response-level length weighting 与 group std normalization 带来的
  question-level reweighting。Dr.GRPO 去掉相关 normalization，使 estimator 更接近它定义的
  unbiased policy-gradient 目标。
tags:
  - Dr.GRPO
  - GRPO
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ Dr.GRPO
    url: 'https://arxiv.org/abs/2503.20783'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>核心讨论包括 response-level length weighting 与 group std normalization 带来的 question-level reweighting。Dr.GRPO 去掉相关 normalization，使 estimator 更接近它定义的 unbiased policy-gradient 目标。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p><b>Response-level length bias：</b>若每个 response 先做 $(1/|o_i|)\sum_t$ loss，则每条 response 总权重接近相同，长回答里单 token 权重更小。你实际上优化的是“每 response 平均 token objective”，而不是“所有 token 等权”。</p><p><b>Question-level difficulty/reweighting：</b>若 advantage 除以 group std，reward variance 小的 question 会被放大、variance 大的会被缩小，改变不同 prompt 对 global gradient 的自然权重。</p><p>Dr.GRPO 的关键价值不只是一个新公式，而是提醒：<b>loss reduction / normalization 本身就在定义隐式优化目标。</b></p><p>后续理论继续讨论 gradient unbiasedness 与 length invariance 的不可兼得/目标选择，因此不要把 Dr.GRPO 简化成“彻底解决 length bias”。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>“Unbiased”相对于什么？</summary><div class="follow-answer"><p>相对于某个明确的 sequence/token-level policy objective。先定义你想最大化的是 expected sequence reward、per-token average 还是别的，再谈 estimator 是否无偏。</p></div></details><details class="followup"><summary>Response-level averaging 和 token-level averaging哪个对？</summary><div class="follow-answer"><p>没有脱离目标的“绝对正确”。前者每条 response 等权，后者每个 token 等权；它们对应不同 length weighting。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2503.20783" target="_blank" rel="noopener noreferrer">↗ Dr.GRPO</a></div>

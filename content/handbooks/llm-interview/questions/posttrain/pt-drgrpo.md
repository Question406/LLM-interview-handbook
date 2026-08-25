---
id: pt-drgrpo
section: posttrain
order: 18
level: S
title: Dr.GRPO 认为 vanilla GRPO 有哪些 bias？
quick: >-
  核心讨论包括：按 response 长度加权，以及用 group std 做 normalization 带来的按题重加权。Dr.GRPO 去掉相关
  normalization，让 estimator 更接近它定义的无偏 policy-gradient 目标。
tags:
  - Dr.GRPO
  - GRPO
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ Dr.GRPO
    url: 'https://arxiv.org/abs/2503.20783'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>核心讨论包括：按 response 长度加权，以及用 group std 做 normalization 带来的按题重加权。Dr.GRPO 去掉相关 normalization，让 estimator 更接近它定义的无偏 policy-gradient 目标。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p><b>Response-level length bias：</b>若每个 response 先做 $(1/|o_i|)\sum_t$ loss，则每条 response 总权重接近相同，长回答里单个 token 权重更小。你实际优化的是「每条 response 的平均 token objective」，不是「所有 token 等权」。</p><p><b>Question-level difficulty/reweighting：</b>若 advantage 除以 group std，reward 方差小的题会被放大，方差大的会被缩小，不同 prompt 对 global gradient 的自然权重就被改了。</p><p>Dr.GRPO 的价值不只是一个新公式。它提醒：<b>loss 怎么 reduce、怎么 normalize，本身就在定义隐式优化目标。</b></p><p>后续理论还在讨论 gradient 无偏和长度不变性很难兼得，以及目标该怎么选。所以别把 Dr.GRPO 说成「彻底解决了 length bias」。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>“Unbiased”相对于什么？</summary><div class="follow-answer"><p>相对于某个明确的 sequence 或 token 级 policy 目标。先定义你想最大化的是 expected sequence reward、per-token average，还是别的，再谈 estimator 有没有偏。</p></div></details><details class="followup"><summary>Response-level averaging 和 token-level averaging哪个对？</summary><div class="follow-answer"><p>没有脱离目标的「绝对正确」。前者每条 response 等权，后者每个 token 等权，对应不同的长度加权。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2503.20783" target="_blank" rel="noopener noreferrer">↗ Dr.GRPO</a></div>

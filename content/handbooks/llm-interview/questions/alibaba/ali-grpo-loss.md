---
id: ali-grpo-loss
section: alibaba
order: 3
level: S
title: 阿里算法面：请写出 GRPO Loss，并解释每一项
quick: >-
  GRPO 用组内相对 advantage 的 clipped surrogate，再加相对参考策略的 KL。核心项是
  ρ_t（重要性比）、A_t（组内标准化优势）、clip、以及 β·KL。
tags:
  - Alibaba
  - GRPO
  - 真题
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>GRPO 用组内相对 advantage 的 clipped surrogate，再加相对参考策略的 KL。核心项是 ρ_t（重要性比）、A_t（组内标准化优势）、clip、以及 β·KL。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>可按 PPO 风格写出（面试白板够用）：</p>
<p><code>L = -E[ min(ρ_t A_t, clip(ρ_t, 1-ε, 1+ε) A_t) ] + β · KL(π || π_ref)</code></p>
<p>其中 <code>ρ_t = π_θ(y_t|x,y_&lt;t) / π_old(y_t|x,y_&lt;t)</code>。</p>
<ol>
<li><b>ρ_t：</b>当前策略相对采样策略的概率比，衡量更新幅度。</li>
<li><b>A_t：</b>GRPO 通常用同组样本 reward 做相对标准化得到优势，决定更新方向与强度。</li>
<li><b>clip：</b>限制单步更新，防止策略崩溃；min 取更保守一侧。</li>
<li><b>β KL：</b>约束别偏离 SFT/参考策略太远，抑制 reward hacking 与语言崩坏。</li>
</ol>
<p>回答时强调：GRPO 的“相对”发生在 group 内，不依赖单独 critic/value model，是相对 PPO 的工程简化。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>ε 一般取多少？</summary><div class="follow-answer"><p>常见从 0.1–0.2 起步；过大更新不稳，过小学习慢。应结合 KL、reward 方差与崩坏率调。</p></div></details><details class="followup"><summary>为什么要 π_ref？</summary><div class="follow-answer"><p>防止策略为刷高 reward 偏离自然语言/可用分布；也是对齐阶段的安全锚点。</p></div></details></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a></div>

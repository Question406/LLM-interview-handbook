---
id: ali-credit-token
section: alibaba
order: 7
level: S
title: 序列级最终奖励，在 GRPO 里如何分配到每个 token？
quick: >-
  最常见是把序列 advantage 广播到所有生成 token；更细可做 step/action 边界对齐、过程奖励或
  critic。粗广播能训但方差大，关键错误步与废话会被同等强化。
tags:
  - Alibaba
  - GRPO
  - Credit
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>最常见是把序列 advantage 广播到所有生成 token；更细可做 step/action 边界对齐、过程奖励或 critic。粗广播能训但方差大，关键错误步与废话会被同等强化。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>公开阿里算法面常问 credit assignment：</p>
<ol>
<li><b>序列广播：</b>整条 response 一个 R / A，每个 token 共享。实现简单，适合短 reasoning；长轨迹噪声大。</li>
<li><b>动作边界对齐：</b>Agent 多工具调用时，按 tool-call / turn 切段，只在 decision token 上优化。</li>
<li><b>过程奖励 / 验证器：</b>中间步骤可打分时用 denser signal。</li>
<li><b>Critic/TD：</b>需要 value 时再引入（GRPO 常刻意避免）。</li>
</ol>
<p>回答模板：先承认默认广播的局限 → 说明你任务长度与是否有 verifier → 给出可落地的更细 credit 方案。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Agent 多轮工具调用还有什么挑战？</summary><div class="follow-answer"><p>状态非平稳、工具失败重试、部分可观测、长 horizon credit、以及环境 reset/幂等。只靠 final success 往往不够。</p></div></details></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850" target="_blank" rel="noopener noreferrer">↗ 阿里国际大模型算法一面</a><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 社招一面</a></div>

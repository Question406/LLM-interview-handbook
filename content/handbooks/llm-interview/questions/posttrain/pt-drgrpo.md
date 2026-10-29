---
id: pt-drgrpo
section: posttrain
order: 18
level: S
title: Dr.GRPO 认为 vanilla GRPO 有哪些 bias？
quick: >-
  假设两个错误回答分别有 10 个和 100 个 tokens。如果先对每条回答的 token loss 求平均，长回答中每个 token
  分到的权重就更小。这与所有 tokens 等权的目标不同。
tags:
  - Dr.GRPO
  - GRPO
  - 口述改写 2026-10-28
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources:
  - title: ↗ Dr.GRPO
    url: 'https://arxiv.org/abs/2503.20783'
    type: legacy-reference
---
<h2>回答思路</h2>
<blockquote>
<p><strong>问题与场景：</strong> 假设两个错误回答分别有 10 个和 100 个 tokens。</p>
<p><strong>做法与原因：</strong> 另一项变化来自 advantage 除以 group standard deviation，它会改变不同题目对更新的相对权重。</p>
<p><strong>检查与取舍：</strong> 我会先说清希望优化哪个目标，再判断 estimator 对它是否有偏。</p>
</blockquote>
<h2>可以这样回答</h2>
<p>假设两个错误回答分别有 10 个和 100 个 tokens。如果先对每条回答的 token loss 求平均，长回答中每个 token 分到的权重就更小。这与所有 tokens 等权的目标不同。</p>
<p>另一项变化来自 advantage 除以 group standard deviation，它会改变不同题目对更新的相对权重。Dr.GRPO 针对这些 normalization 讨论长度与难度相关的偏差，并改变相应计算。</p>
<p>我会先说清希望优化哪个目标，再判断 estimator 对它是否有偏。不能说去掉所有 normalization 就在任何任务中绝对正确；具体公式与假设见后面的推导。</p>

<details class="design-reference"><summary>展开技术备查：原始说明、公式与实验细节</summary>
<div class="quick"><div class="mini-title">30 秒回答</div><p>主要有两个：按 response 长度加权，以及除以 group std 带来的按题重加权。Dr.GRPO 去掉这些 normalization，让 estimator 更接近它定义的无偏 policy-gradient 目标。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Dr.GRPO 指出的偏差主要有两个，一个来自长度，一个来自难度，根源都在 loss 怎么 reduce、怎么 normalize。</p><p>第一个是 <b>response-level length bias</b>。如果每个 response 先做 $(1/|o_i|)\sum_t$ 损失（loss），每条 response 的总权重就差不多一样，长回答里单个 token 的权重变小了。比如一条短的错误回答和一条长得多的错误回答，挨的总罚差不多，长的那条里每个 token 分到的就少得多。这时你实际优化的是「每条 response 的平均 token objective」，和「所有 token 等权」是两个目标。</p><p>第二个是 <b>question-level difficulty/reweighting</b>。如果 advantage 再除以 group std，奖励方差小的题会被放大，方差大的题会被缩小，不同 prompt 对整体梯度原本的权重就被改了。</p><p>所以更实际的提醒是：<b>loss 怎么 reduce、怎么 normalize，本身就在定义隐式的优化目标。</b></p><p>后续的理论工作还在讨论 gradient 无偏和长度不变性很难同时做到，以及目标到底该怎么选；length bias 也还没被彻底消掉。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>“Unbiased”相对于什么？</summary><div class="follow-answer"><p>相对于某个明确的 sequence 级或 token 级 policy 目标。先说清楚你想最大化的是预期序列 reward、per-token average 还是别的，再谈 estimator 有没有偏。</p></div></details><details class="followup"><summary>Response-level averaging 和 token-level averaging 哪个对？</summary><div class="follow-answer"><p>离开目标谈不上哪个「绝对正确」。前者让每条 response 等权，后者让每个 token 等权，对应的是不同的长度加权方式。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2503.20783" target="_blank" rel="noopener noreferrer">↗ Dr.GRPO</a></div>

</details>

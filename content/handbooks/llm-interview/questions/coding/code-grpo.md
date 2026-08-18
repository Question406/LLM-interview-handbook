---
id: code-grpo
section: coding
order: 6
level: S
title: 手写 GRPO group advantage：std≈0 怎么处理？
quick: >-
  Reward 按 prompt 分组，在 group 维求 mean/std；A=(r−mean)/(std+eps)。std≈0
  不只是数值除零问题，而表示一组没有 relative signal，应记录/过滤或改 sampling。
tags:
  - GRPO
  - PyTorch
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Reward 按 prompt 分组，在 group 维求 mean/std；A=(r−mean)/(std+eps)。std≈0 不只是数值除零问题，而表示一组没有 relative signal，应记录/过滤或改 sampling。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><pre><code data-lang="python">def group_advantage(rewards, eps=1e-6):
    # rewards [N_prompts, G]
    mean = rewards.mean(dim=1, keepdim=True)
    std = rewards.std(dim=1, keepdim=True, unbiased=False)
    adv = (rewards - mean) / (std + eps)
    informative = std.squeeze(1) &gt; eps
    return adv, informative</code></pre><p>对于 binary reward，全 0 或全 1 group 会得到零 centered reward。eps 只能防 NaN，不能制造学习信号。工程上应该监控 zero-variance group rate；DAPO Dynamic Sampling 的思想之一就是减少这些无效 group 占用训练 batch。</p><p>如果采用 Dr.GRPO 类 objective，可能去掉 std normalization；如果有多个 reward components，还要决定是先组合 reward 再 group normalize，还是每个 component 单独处理。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>torch.std 默认 unbiased=True 有什么影响？</summary><div class="follow-answer"><p>小 group 时样本标准差与 population std 数值不同；实现必须和论文/框架定义一致。G=1 时 unbiased std 甚至不可定义。</p></div></details></div>

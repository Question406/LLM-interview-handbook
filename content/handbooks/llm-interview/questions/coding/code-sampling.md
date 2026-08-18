---
id: code-sampling
section: coding
order: 12
level: S
title: 手写 Temperature + Top-p Sampling：顺序、数值稳定性和边界怎么处理？
quick: >-
  先按 temperature 缩放 logits，再做稳定 softmax；Top-p 应按概率从高到低累积，保留最小的累计质量不少于 p 的 token
  集合后重新归一化并采样。要处理 T→0、p 边界、NaN/Inf 和至少保留一个 token。
tags:
  - Coding
  - Sampling
  - Inference
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: Generation strategies
    url: 'https://huggingface.co/docs/transformers/main/en/generation_strategies'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>这题考的不只是会调 API，而是能说清“在什么分布上裁剪”。一个稳健实现应做到：</p><ol><li>对 logits 除以 T；T=0 或极小时显式走 argmax，避免数值爆炸；</li><li>减去最大 logit 后计算 softmax，并检查 NaN/Inf；</li><li>按概率降序排序，计算 cumulative probability，保留使累计质量首次达到 p 的最小前缀（至少一个 token）；</li><li>把被滤掉的 token mask 后重新归一化，再用随机数从 categorical 分布采样。</li></ol><p>追问：repetition penalty、min-p、top-k 与 temperature 的先后顺序必须由实现定义并测试；不同顺序会得到不同分布。</p><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://huggingface.co/docs/transformers/main/en/generation_strategies" target="_blank" rel="noreferrer">Generation strategies</a></div></div>

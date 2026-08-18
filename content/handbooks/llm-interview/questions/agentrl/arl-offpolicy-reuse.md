---
id: arl-offpolicy-reuse
section: agentrl
order: 18
level: S
title: 旧 Agent Trajectory 能不能反复拿来训练？什么时候会变成 Off-Policy 问题？
quick: >-
  可以复用作 SFT、replay 或离线评估，但若把旧 policy、旧工具/网页状态下的轨迹当 current-policy
  policy-gradient 数据，就出现分布偏移。重要性权重会高方差，裁剪虽稳定却引入 bias。
tags:
  - Agent RL
  - Off-Policy
  - Replay
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: WebArena
    url: 'https://arxiv.org/abs/2307.13854'
    type: legacy-reference
  - title: DeepSeekMath / GRPO
    url: 'https://arxiv.org/abs/2402.03300'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>只要行为 policy 与待优化 policy 不同，且你想估计 current policy 的回报梯度，就需要面对 off-policy correction。Agent 任务里偏移更大：policy 变了、检索索引变了、网页变了、工具版本也可能变了。</p><ul><li><b>先记录 behavior：</b>完整 policy/version、采样参数、action log-prob、环境版本和 reward 规则；没有 support 信息就很难做可靠 correction。</li><li><b>明确用途：</b>旧成功轨迹做 SFT/replay 通常合理；做严格 on-policy RL 更新时应限制 freshness 或采用有理论边界的 correction。</li><li><b>监控覆盖：</b>importance ratio 分布、有效样本量、被裁剪比例和按 trajectory length 的 return；这些比“replay buffer 很大”更重要。</li></ul><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://arxiv.org/abs/2307.13854" target="_blank" rel="noreferrer">WebArena</a><a href="https://arxiv.org/abs/2402.03300" target="_blank" rel="noreferrer">DeepSeekMath / GRPO</a></div></div>

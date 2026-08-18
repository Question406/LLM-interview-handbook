---
id: company-minimax
section: companies
order: 7
level: A
title: MiniMax：Agent-Native Post-Training 该准备什么？
quick: >-
  重点理解 LLM policy 与 environment boundary、interleaved agent SFT
  trajectory、executable environment / artifact-aligned reward、long-horizon Agent
  RL 与训练-推理-Agent 解耦系统。
tags:
  - MiniMax
  - Agent RL
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ MiniMax M2
    url: 'https://arxiv.org/abs/2605.26494'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>重点理解 LLM policy 与 environment boundary、interleaved agent SFT trajectory、executable environment / artifact-aligned reward、long-horizon Agent RL 与训练-推理-Agent 解耦系统。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>MiniMax M2 系列适合用来回答“Agent RL 为什么不是 model.generate()+reward”这类题：rollout 需要 sandbox/browser/tools，trajectory 很长，policy/environment token ownership、state reset、reward 和 weight sync 都更复杂。</p><p>面试时可以把它和 reasoning GRPO 对照：单 response outcome RL 省 critic 的经验，不能机械迁移到 100-step Agent；长 horizon 下 action-level value/credit 可能重新重要。</p></div>
          
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2605.26494" target="_blank" rel="noopener noreferrer">↗ MiniMax M2</a></div>

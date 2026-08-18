---
id: ali-attention-agent-limit
section: alibaba
order: 12
level: A
title: Agent 多轮对话里，Attention 的局限性体现在哪？
quick: 上下文长度与噪声、长程依赖被稀释、工具结果与历史混杂导致 distraction、计算/显存随序列平方或线性增长，且无法替代显式状态/记忆系统。
tags:
  - Alibaba
  - Agent
  - Attention
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>上下文长度与噪声、长程依赖被稀释、工具结果与历史混杂导致 distraction、计算/显存随序列平方或线性增长，且无法替代显式状态/记忆系统。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>结合 Agent 场景回答：</p>
<ul>
<li>多轮 tool observation 堆积，真正关键证据被冲淡；</li>
<li>需要跨很早之前的约束/用户偏好时，纯 attention 不可靠；</li>
<li>无法天然提供可审计的外部状态、权限与终止条件；</li>
<li>因此要有 Memory/State/Skill/Harness 等系统层补偿。</li>
</ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>

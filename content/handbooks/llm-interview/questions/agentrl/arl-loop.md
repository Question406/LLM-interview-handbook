---
id: arl-loop
section: agentrl
order: 13
level: A
title: 怎么检测 Agent 死循环或无进展？
quick: >-
  同时看 repeated action、semantic repeat、state no-progress 与预算。只设 max turns
  能止损，但不能判断“已经没有进展”。
tags:
  - Failure Recovery
  - Loop Detection
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>同时看 repeated action、semantic repeat、state no-progress 与预算。只设 max turns 能止损，但不能判断“已经没有进展”。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>可维护最近 k 个 action/state：exact hash 发现完全重复；embedding/AST 发现语义重复；environment delta 衡量是否真正改变状态。若 action 高相似且 state delta≈0，触发 strategy switch、reflection、replan 或 terminate。</p><p>Budget 包括 max turns、tokens、tool cost、wall-clock。对于 search/research 任务还可以维护 novelty score：连续多轮没有新证据时停止。</p></div>

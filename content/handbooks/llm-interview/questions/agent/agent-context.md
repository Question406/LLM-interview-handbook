---
id: agent-context
section: agent
order: 13
level: S
title: 为什么 Context Window 很大仍需要 Context Engineering？
quick: >-
  Context capacity 不等于有效利用。长历史会带来 attention dilution、stale/conflicting
  state、tool noise、context rot、prefill 成本与 latency；目标是最小但高信号的 context。
tags:
  - Context Engineering
  - Agent
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ Anthropic Context Engineering
    url: >-
      https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Context capacity 不等于有效利用。长历史会带来 attention dilution、stale/conflicting state、tool noise、context rot、prefill 成本与 latency；目标是最小但高信号的 context。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Agent context 里往往混有 user instruction、old plan、tool outputs、logs、memory、skills、documents。把所有历史原样追加会产生：</p><ul><li><b>Signal dilution：</b>关键约束占比越来越低；</li><li><b>Stale state：</b>旧计划/旧环境值继续影响决策；</li><li><b>Conflict：</b>新旧信息互相矛盾；</li><li><b>Tool ambiguity：</b>过多 schema/skills 增加误选；</li><li><b>Cost：</b>prefill tokens、TTFT、缓存压力上升。</li></ul><p>常见方法：truncation、summarization、structured state、external retrieval、sub-agent context isolation、tool-result compaction。最值得推荐的是把“当前可执行状态”显式结构化，而不是只靠自然语言 summary。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Summary 自己 hallucinate 怎么办？</summary><div class="follow-answer"><p>保留可追溯 source pointers，对关键约束用 structured fields 而非生成摘要；对 summary 做 factual retention tests，必要时允许回读 raw logs。</p></div></details><details class="followup"><summary>Structured state 由谁维护？</summary><div class="follow-answer"><p>模型可提出更新，但 runtime 可以用 schema validation、environment truth merge；关键 state 如文件修改/test status最好来自工具事实。</p></div></details><details class="followup"><summary>Tool result 很长怎么压缩？</summary><div class="follow-answer"><p>先结构化提取 machine-readable facts/error class；保留摘要+原始结果 handle，需要时按需展开，而不是把 10k log 永久留在 context。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents" target="_blank" rel="noopener noreferrer">↗ Anthropic Context Engineering</a></div>

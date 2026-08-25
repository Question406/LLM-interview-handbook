---
id: agent-context
section: agent
order: 13
level: S
title: 为什么 Context Window 很大仍需要 Context Engineering？
quick: >-
  Context 大不等于用得好。历史一长，attention 会被稀释，还会堆 stale 或互相打架的 state、tool
  noise、context rot，prefill 和 latency 也上去。目标是尽量小、信号尽量高的 context。
tags:
  - Context Engineering
  - Agent
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ Anthropic Context Engineering
    url: >-
      https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Context 大不等于用得好。历史一长，attention 会被稀释，还会堆 stale 或互相打架的 state、tool noise、context rot，prefill 和 latency 也上去。目标是尽量小、信号尽量高的 context。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Agent context 里经常混着 user instruction、旧 plan、tool 输出、logs、memory、skills、documents。把历史原样往上叠，会出现：</p><ul><li><b>Signal dilution：</b>关键约束占比越来越低；</li><li><b>Stale state：</b>旧计划/旧环境值继续影响决策；</li><li><b>Conflict：</b>新旧信息互相矛盾；</li><li><b>Tool ambiguity：</b>过多 schema/skills 增加误选；</li><li><b>Cost：</b>prefill tokens、TTFT、缓存压力上升。</li></ul><p>常见做法是 truncation、summarization、structured state、external retrieval、sub-agent 隔离 context、压缩 tool result。我更倾向把「当前可执行状态」显式结构化，别只靠自然语言 summary。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Summary 自己 hallucinate 怎么办？</summary><div class="follow-answer"><p>关键约束用 structured fields，并留可追溯的 source pointers，别只生成摘要。summary 要做 factual retention tests，必要时允许回读 raw logs。</p></div></details><details class="followup"><summary>Structured state 由谁维护？</summary><div class="follow-answer"><p>模型可以提更新，runtime 再用 schema validation、跟 environment 真相 merge。文件改没改、test 过没过，最好来自工具事实。</p></div></details><details class="followup"><summary>Tool result 很长怎么压缩？</summary><div class="follow-answer"><p>先抽出 machine-readable facts 和 error class；摘要加上原始结果 handle，要用再展开。别把 10k log 永久搁在 context 里。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents" target="_blank" rel="noopener noreferrer">↗ Anthropic Context Engineering</a></div>

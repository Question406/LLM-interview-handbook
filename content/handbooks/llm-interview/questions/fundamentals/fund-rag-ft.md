---
id: fund-rag-ft
section: fundamentals
order: 16
level: A
title: RAG vs Fine-tuning 怎么选？
quick: 频繁更新、需要引用证据、外部私有知识更适合 RAG；稳定通用行为、格式、技能、低延迟自动化更适合 fine-tuning。常见系统二者结合。
tags:
  - RAG
  - Fine-tuning
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>频繁更新、需要引用证据、外部私有知识更适合 RAG；稳定通用行为、格式、技能、低延迟自动化更适合 fine-tuning。常见系统二者结合。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Fine-tuning 把行为/知识写进 weights，更新慢、难审计但无需每次检索；RAG 外部化知识，易更新/可溯源但依赖 retrieval/context。</p><p>不要用 fine-tuning 替代实时事实数据库，也不要指望 RAG 自动教模型稳定的复杂 procedure——那更像 Skill/SFT 的职责。</p></div>

---
id: ali-latency-3tools
section: alibaba
order: 20
level: S
title: 场景题：Agent 链路含 3 个工具且高频请求，延迟如何优化？
quick: 并行可并行的工具、缓存高频路径、意图分流到轻量模板、缩小 prompt/工具集、投机/小模型草稿、超时降级与限流。先量测再改。
tags:
  - Alibaba
  - Agent
  - 性能
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>并行可并行的工具、缓存高频路径、意图分流到轻量模板、缩小 prompt/工具集、投机/小模型草稿、超时降级与限流。先量测再改。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>建议按依赖图优化：</p>
<ol>
<li>画清 3 个工具的串并行依赖，能并行就并行；</li>
<li>高频 query 走缓存或固定 workflow，绕开多轮 LLM；</li>
<li>首包分类用小模型，复杂再上大模型；</li>
<li>压缩上下文与 tool schema，减少 prefill；</li>
<li>设 SLA：超时跳过非关键工具或降级 FAQ；</li>
<li>看 p95/p99、工具 RT、LLM RT、排队，避免盲目换更大模型。</li>
</ol></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>

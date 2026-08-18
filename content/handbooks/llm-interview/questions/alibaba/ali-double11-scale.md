---
id: ali-double11-scale
section: alibaba
order: 26
level: S
title: 淘天场景：把 Agent Demo 改造成支撑“双十一”级流量，最大挑战是什么？
quick: 不是换更大模型，而是：限流与降级、缓存高频路径、异步化与削峰、状态外置、可观测与熔断、成本预算。先保证正确的关键路径可降级存活。
tags:
  - Alibaba
  - Agent
  - 高并发
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天 Agent 开发技术面
    url: 'https://www.nowcoder.com/feed/main/detail/4c8da8a740e64eb5827fb1b962928eda'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>不是换更大模型，而是：限流与降级、缓存高频路径、异步化与削峰、状态外置、可观测与熔断、成本预算。先保证正确的关键路径可降级存活。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>架构挑战可按层答：</p>
<ol>
<li><b>流量：</b>网关限流、队列削峰、关键/非关键分流；</li>
<li><b>算力：</b>小模型/模板兜底，大模型只服务复杂单；</li>
<li><b>状态：</b>会话与记忆外置，避免单机亲和；</li>
<li><b>依赖：</b>工具超时、舱壁隔离、缓存商品/订单热点；</li>
<li><b>发布：</b>灰度、熔断、回滚、审计。</li>
</ol>
<p>面试官听的是：你懂电商大流量下 AI 系统的工程约束。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/4c8da8a740e64eb5827fb1b962928eda" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 开发技术面</a></div>

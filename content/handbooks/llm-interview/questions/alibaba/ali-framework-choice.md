---
id: ali-framework-choice
section: alibaba
order: 27
level: A
title: Agent 编排选 LangChain 类开源还是自研？
quick: PoC 可用开源加速；生产看可控性、可观测、权限与性能。核心业务链路往往自研状态机/图编排，开源作外围。关键是 trade-off，不是站队。
tags:
  - Alibaba
  - Agent
  - 架构
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天 Agent 开发技术面
    url: 'https://www.nowcoder.com/feed/main/detail/4c8da8a740e64eb5827fb1b962928eda'
    type: legacy-reference
  - title: ↗ 淘宝闪购 Agent 算法一面
    url: 'https://www.nowcoder.com/discuss/879393838081597440'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>PoC 可用开源加速；生产看可控性、可观测、权限与性能。核心业务链路往往自研状态机/图编排，开源作外围。关键是 trade-off，不是站队。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>对比维度：开发速度、可调试性、版本锁定、性能开销、安全合规、团队熟悉度。</p>
<p>淘天/闪购面经共同点：能说清“为何选/为何不选”，并承认企业内数据不出域、私有化约束。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/4c8da8a740e64eb5827fb1b962928eda" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 开发技术面</a><a href="https://www.nowcoder.com/discuss/879393838081597440" target="_blank" rel="noopener noreferrer">↗ 淘宝闪购 Agent 算法一面</a></div>

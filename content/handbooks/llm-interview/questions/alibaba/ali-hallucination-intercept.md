---
id: ali-hallucination-intercept
section: alibaba
order: 29
level: A
title: 幻觉或不合规内容，工程上如何在生成前后拦截？
quick: 前：检索强制、工具结果优先、拒答策略；中：schema/规则校验；后：事实核对、敏感词/合规模型、引用存在性检查。关键路径可双模型复核。
tags:
  - Alibaba
  - Hallucination
  - 安全
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>前：检索强制、工具结果优先、拒答策略；中：schema/规则校验；后：事实核对、敏感词/合规模型、引用存在性检查。关键路径可双模型复核。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>可落地机制：</p>
<ul>
<li>生成前：必须先查知识库/订单系统，禁止空上下文臆造；</li>
<li>生成中：结构化输出与工具参数校验失败则重试；</li>
<li>生成后：NLI/规则核对、敏感分类、人工抽检队列；</li>
<li>高风险域：默认检索增强 + 拒答，而不是强行回答。</li>
</ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/4c8da8a740e64eb5827fb1b962928eda" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 开发技术面</a></div>

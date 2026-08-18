---
id: ali-guardrail
section: alibaba
order: 28
level: S
title: 如何控制 Agent 自主性边界？Safety Guardrail 怎么设计？
quick: 规则引擎管硬约束，LLM 管柔推理；工具分级（只读/可逆/不可逆）；不可逆前人工确认；输出过滤与策略引擎双闸门。
tags:
  - Alibaba
  - Safety
  - Agent
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>规则引擎管硬约束，LLM 管柔推理；工具分级（只读/可逆/不可逆）；不可逆前人工确认；输出过滤与策略引擎双闸门。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>退换货等明确规则场景：优先规则/工作流，LLM 负责理解与填槽，不负责改规则。</p>
<p>Guardrail 分层：输入安全 → 工具权限 → 执行确认 → 输出合规检查 → 审计。自主性随风险升高而降低。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/4c8da8a740e64eb5827fb1b962928eda" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 开发技术面</a><a href="https://www.nowcoder.com/discuss/879393838081597440" target="_blank" rel="noopener noreferrer">↗ 淘宝闪购 Agent 算法一面</a></div>

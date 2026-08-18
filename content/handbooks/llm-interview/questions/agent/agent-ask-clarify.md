---
id: agent-ask-clarify
section: agent
order: 16
level: A
title: Agent 什么时候应该主动 Ask Clarification？
quick: 当不同合理解释会导致高成本/不可逆/显著不同的行动，而当前信息不足以安全选择时应问；低成本可逆探索则可先执行信息收集。
tags:
  - Agent
  - Planning
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>当不同合理解释会导致高成本/不可逆/显著不同的行动，而当前信息不足以安全选择时应问；低成本可逆探索则可先执行信息收集。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>可以把问题看成 value of information：若询问用户的时间成本小于错误行动的 expected cost，就应该 clarify。</p><p>特别应问：目标/范围缺失、不可逆 side effect、权限/身份不明、多个对象同名、预算/时间约束决定方案。可以不问：搜索/读取/列出候选等低风险可逆步骤。</p><p>训练上可把“ask user”视为一个 action，并构造 ambiguity benchmark：同一 prompt 的隐藏目标不同，模型只有澄清后才能稳定成功。</p></div>

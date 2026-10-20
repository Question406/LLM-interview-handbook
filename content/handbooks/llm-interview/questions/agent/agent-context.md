---
id: agent-context
section: agent
order: 13
level: S
title: 为什么 Context Window 很大仍需要 Context Engineering？
quick: "上下文能放得下，不代表模型用得好。长历史会混入过期状态、矛盾信息和工具噪声，关键约束更难被注意到，处理输入的成本与延迟也会增加。Context Engineering 要保留当前任务需要的高价值信息，并明确记录可执行状态。"
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>上下文能放得下，不代表模型用得好。长历史会混入过期状态、矛盾信息和工具噪声，关键约束更难被注意到，处理输入的成本与延迟也会增加。Context Engineering 要保留当前任务需要的高价值信息，并明确记录可执行状态。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Agent 上下文经常同时包含用户指令、旧计划、工具输出、日志、记忆、技能和文档。如果只不断追加历史，会出现：</p><ul><li><b>Signal dilution：</b>关键约束占比越来越低；</li><li><b>Stale state：</b>旧计划/旧环境值继续影响决策；</li><li><b>Conflict：</b>新旧信息互相矛盾；</li><li><b>Tool ambiguity：</b>过多 schema/skills 增加误选；</li><li><b>Cost：</b>prefill tokens、首个 token 的等待时间（TTFT）、缓存压力上升。</li></ul><p>可以截断或摘要历史，把状态存成结构化字段，按需检索外部内容，让子代理使用独立上下文，并压缩工具结果。当前可执行状态最好用明确字段记录，不要只靠自然语言摘要。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Summary 自己 hallucinate 怎么办？</summary><div class="follow-answer"><p>关键约束存成结构化字段，并保留原始来源位置。检查摘要是否遗漏或改写事实，需要时允许重新读取原始日志。</p></div></details><details class="followup"><summary>Structured state 由谁维护？</summary><div class="follow-answer"><p>模型提出更新，由运行程序验证 schema，再与环境里的真实状态核对合并。文件是否改过、测试是否通过，应以工具结果为准。</p></div></details><details class="followup"><summary>Tool result 很长怎么压缩？</summary><div class="follow-answer"><p>先抽取程序可读取的事实和错误类型，再给摘要附上原始结果的引用，需要时展开。不要让 10k 日志一直占据上下文。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents" target="_blank" rel="noopener noreferrer">↗ Anthropic Context Engineering</a></div>

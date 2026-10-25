---
id: agent-context
section: agent
order: 13
level: S
title: 为什么 Context Window 很大仍需要 Context Engineering？
quick: "上下文放得下，不代表模型用得好。历史一长，过期状态、矛盾信息和工具噪声都混进来，关键约束越来越难被注意到，处理输入的成本和延迟也跟着涨。Context Engineering 要只留当前任务需要的高价值信息，并把可执行状态记成明确的字段。"
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>上下文放得下，不代表模型用得好。历史一长，过期状态、矛盾信息和工具噪声都混进来，关键约束越来越难被注意到，处理输入的成本和延迟也跟着涨。Context Engineering 要只留当前任务需要的高价值信息，并把可执行状态记成明确的字段。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>窗口再大也要做 Context Engineering，因为放得下和用得好是两回事。只往上下文里不断追加历史，信息会越来越杂，模型越来越难挑出当前该用的那几条，成本也一直在涨。</p><p>Agent 的上下文经常同时装着用户指令、旧计划、工具输出、日志、记忆、技能和文档。比如一个排障 Agent 跑了很多步，用户一开始说的约束被埋在大段日志下面，占比越来越低，这是 signal dilution；旧计划和旧的环境值还留在里面，继续影响决策，这是 stale state；新旧信息互相矛盾，这是 conflict；挂了太多 schema 和 skills，选错工具的概率上升，这是 tool ambiguity；最后 prefill tokens、首个 token 的等待时间（TTFT）和缓存压力都会上升，这是 cost。</p><p>做法上，可以截断或摘要历史，把状态存成结构化字段，外部内容按需检索，让子代理用独立的上下文，并压缩工具结果。当前可执行的状态最好用明确的字段记录，别只靠一段自然语言摘要。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Summary 自己 hallucinate 怎么办？</summary><div class="follow-answer"><p>把关键约束存成结构化字段，同时保留原始来源的位置。检查摘要有没有漏掉或改写事实，需要时允许回去重读原始日志。</p></div></details><details class="followup"><summary>Structured state 由谁维护？</summary><div class="follow-answer"><p>模型提出更新，运行程序先验证 schema，再和环境里的真实状态核对后合并。文件改没改过、测试过没过，以工具结果为准。</p></div></details><details class="followup"><summary>Tool result 很长怎么压缩？</summary><div class="follow-answer"><p>先抽出程序能读的事实和错误类型，摘要后面附上原始结果的引用，需要时再展开。别让一份 10k 的日志一直占着上下文。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents" target="_blank" rel="noopener noreferrer">↗ Anthropic Context Engineering</a></div>

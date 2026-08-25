---
id: agent-skill-diff
section: agent
order: 6
level: S
title: Skill、Tool、MCP、Workflow、Agent 五者如何区分？
quick: >-
  Tool 是能做什么 action；Skill 是一类任务该怎么做的 procedural package；MCP
  是应用怎么标准地接上外部能力和上下文；Workflow 是预定义控制路径；Agent 是动态决定下一步的 policy。
tags:
  - Skill
  - Tool
  - MCP
  - 真题
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ 字节 Agent Eval 面经
    url: 'https://www.nowcoder.com/discuss/867788300126347264'
    type: legacy-reference
  - title: ↗ Anthropic Agent Skills
    url: >-
      https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Tool 是能做什么 action；Skill 是一类任务该怎么做的 procedural package；MCP 是应用怎么标准地接上外部能力和上下文；Workflow 是预定义控制路径；Agent 是动态决定下一步的 policy。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>概念</th><th>一句话</th><th>示例</th></tr></thead><tbody><tr><td>Tool</td><td>What can I do?</td><td>send_email、run_sql、search_repo</td></tr><tr><td>Skill</td><td>How should I solve this class of tasks?</td><td>“发布事故排查流程”+脚本+参考资料</td></tr><tr><td>MCP</td><td>How do I connect/exchange capabilities?</td><td>MCP server 暴露 tools/resources</td></tr><tr><td>Workflow</td><td>What fixed route should run?</td><td>parse→classify→approve→execute</td></tr><tr><td>Agent</td><td>Who decides the next action dynamically?</td><td>LLM 根据 observation 继续 search/edit/test</td></tr></tbody></table></div><p>Skill 不是「更长一点的 prompt」。它通常是可发现、可复用、可版本化、按需加载的程序性知识包，里面还可以带 scripts、references、templates。一个 Skill 可以指导怎么组合多个 MCP 暴露出来的 tools。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Skill 和 RAG 区别？</summary><div class="follow-answer"><p>RAG 更偏事实和证据检索；Skill 更偏程序性知识和 procedure。现实里 Skill 内部也可以做 RAG。</p></div></details><details class="followup"><summary>Skill 和 Sub-agent 区别？</summary><div class="follow-answer"><p>Skill 是知识或流程包，本身不一定有独立 policy 和 context；sub-agent 是独立执行主体，可以加载 Skill。</p></div></details><details class="followup"><summary>Skill 能调用 MCP tool 吗？</summary><div class="follow-answer"><p>可以。Skill 的 procedure 可以写清何时、按什么顺序去调外部 tools。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/867788300126347264" target="_blank" rel="noopener noreferrer">↗ 字节 Agent Eval 面经</a><a href="https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills" target="_blank" rel="noopener noreferrer">↗ Anthropic Agent Skills</a></div>

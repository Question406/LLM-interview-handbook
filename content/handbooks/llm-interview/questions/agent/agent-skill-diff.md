---
id: agent-skill-diff
section: agent
order: 6
level: S
title: Skill、Tool、MCP、Workflow、Agent 五者如何区分？
quick: >-
  Tool=能做什么 action；Skill=一类任务应如何做的 procedural
  package；MCP=应用如何标准连接外部能力/上下文；Workflow=预定义控制路径；Agent=动态决定下一步的 policy。
tags:
  - Skill
  - Tool
  - MCP
  - 真题
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 字节 Agent Eval 面经
    url: 'https://www.nowcoder.com/discuss/867788300126347264'
    type: legacy-reference
  - title: ↗ Anthropic Agent Skills
    url: >-
      https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Tool=能做什么 action；Skill=一类任务应如何做的 procedural package；MCP=应用如何标准连接外部能力/上下文；Workflow=预定义控制路径；Agent=动态决定下一步的 policy。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>概念</th><th>一句话</th><th>示例</th></tr></thead><tbody><tr><td>Tool</td><td>What can I do?</td><td>send_email、run_sql、search_repo</td></tr><tr><td>Skill</td><td>How should I solve this class of tasks?</td><td>“发布事故排查流程”+脚本+参考资料</td></tr><tr><td>MCP</td><td>How do I connect/exchange capabilities?</td><td>MCP server 暴露 tools/resources</td></tr><tr><td>Workflow</td><td>What fixed route should run?</td><td>parse→classify→approve→execute</td></tr><tr><td>Agent</td><td>Who decides the next action dynamically?</td><td>LLM 根据 observation 继续 search/edit/test</td></tr></tbody></table></div><p>Skill 不是简单“更长 prompt”。它通常是可发现、可复用、可版本化、按需加载的 procedural knowledge package，并可包含 scripts、references、templates。一个 Skill 可以指导如何组合多个 MCP-exposed tools。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Skill 和 RAG 区别？</summary><div class="follow-answer"><p>RAG 更偏事实/证据 retrieval；Skill 更偏程序性知识/procedure。现实中 Skill 内部也可以做 RAG。</p></div></details><details class="followup"><summary>Skill 和 Sub-agent 区别？</summary><div class="follow-answer"><p>Skill 是知识/流程包，本身不一定拥有独立 policy/context；sub-agent 是独立执行主体，可以加载 Skill。</p></div></details><details class="followup"><summary>Skill 能调用 MCP tool 吗？</summary><div class="follow-answer"><p>当然可以。Skill 的 procedure 可以说明何时、按什么顺序调用外部 tools。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/867788300126347264" target="_blank" rel="noopener noreferrer">↗ 字节 Agent Eval 面经</a><a href="https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills" target="_blank" rel="noopener noreferrer">↗ Anthropic Agent Skills</a></div>

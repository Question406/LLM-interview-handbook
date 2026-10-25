---
id: agent-skill-diff
section: agent
order: 6
level: S
title: Skill、Tool、MCP、Workflow、Agent 五者如何区分？
quick: "Tool 是可以执行的动作，Skill 说明一类任务该怎么做，MCP 规定应用怎么连接外部工具与上下文，Workflow 预先定好执行路线，Agent 根据当前结果动态选下一步。"
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>Tool 是可以执行的动作，Skill 说明一类任务该怎么做，MCP 规定应用怎么连接外部工具与上下文，Workflow 预先定好执行路线，Agent 根据当前结果动态选下一步。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>五个概念各回答一个问题：Tool 是能做什么，Skill 是这类任务该怎么做，MCP 是怎么连上外部能力，Workflow 是走哪条固定路线，Agent 是下一步由谁临场决定。对照表如下：</p><div class="table-wrap"><table><thead><tr><th>概念</th><th>一句话</th><th>示例</th></tr></thead><tbody><tr><td>Tool</td><td>What can I do?</td><td>send_email、run_sql、search_repo</td></tr><tr><td>Skill</td><td>How should I solve this class of tasks?</td><td>“发布事故排查流程”+脚本+参考资料</td></tr><tr><td>MCP</td><td>How do I connect/exchange capabilities?</td><td>MCP server 暴露 tools/resources</td></tr><tr><td>Workflow</td><td>What fixed route should run?</td><td>parse→classify→approve→execute</td></tr><tr><td>Agent</td><td>Who decides the next action dynamically?</td><td>LLM 根据 观测结果（observation） 继续 search/edit/test</td></tr></tbody></table></div><p>Skill 一般把操作知识打成一个可发现、可复用、能管理版本、按需加载的包，里面有步骤，也可以带脚本、参考资料和模板。比如一个「发布事故排查流程」Skill，可以写清先用哪个 MCP 工具、再用哪个，把多个工具组合起来用。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Skill 和 检索增强生成（RAG） 区别？</summary><div class="follow-answer"><p>RAG 主要检索事实和证据，Skill 主要描述操作方法和步骤，Skill 内部也可以用 RAG。</p></div></details><details class="followup"><summary>Skill 和 Sub-agent 区别？</summary><div class="follow-answer"><p>Skill 是知识或流程包，本身不一定独立决定动作或维护上下文；sub-agent 是独立执行任务的代理，它可以加载 Skill。</p></div></details><details class="followup"><summary>Skill 能调用 MCP tool 吗？</summary><div class="follow-answer"><p>可以。Skill 的步骤里可以写清楚什么时候、按什么顺序调用外部工具。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/867788300126347264" target="_blank" rel="noopener noreferrer">↗ 字节 Agent Eval 面经</a><a href="https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills" target="_blank" rel="noopener noreferrer">↗ Anthropic Agent Skills</a></div>

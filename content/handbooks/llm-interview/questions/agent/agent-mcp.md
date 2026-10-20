---
id: agent-mcp
section: agent
order: 5
level: S
title: MCP、Function Calling、Agent Framework 有什么区别？
quick: "Function Calling 让模型生成结构化的函数名和参数；MCP 让应用通过统一协议发现和获取外部工具、资源及提示模板；Agent Framework 负责运行循环、规划、记忆和失败恢复。三者处理的是不同层次的问题。"
tags:
  - MCP
  - Tool
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ MCP 官方
    url: 'https://modelcontextprotocol.io/'
    type: legacy-reference
  - title: ↗ MCP Specification
    url: 'https://modelcontextprotocol.io/specification/'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Function Calling 让模型生成结构化的函数名和参数；MCP 让应用通过统一协议发现和获取外部工具、资源及提示模板；Agent Framework 负责运行循环、规划、记忆和失败恢复。三者处理的是不同层次的问题。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>概念</th><th>解决的问题</th><th>不负责什么</th></tr></thead><tbody><tr><td>Function calling</td><td>模型如何表达“调用哪个函数、参数是什么”</td><td>外部服务发现、完整 Agent loop</td></tr><tr><td>MCP</td><td>应用如何按统一协议连接外部工具和上下文提供方</td><td>不决定如何规划、保存记忆或重试</td></tr><tr><td>Agent framework/harness</td><td>如何组织状态、模型决策、工具执行和结果反馈的循环</td><td>协议本身可由 MCP/OpenAPI/自定义接口实现</td></tr></tbody></table></div><p>所以把 MCP 说成「统一 Tool API」不够准。MCP server 可以提供 tools、resources 和 prompts；host 决定怎样将这些能力放进 Agent 的上下文与执行流程。</p><p>安全上，外部 MCP server 返回的工具描述和资源可能含提示注入，工具执行也可能改变外部状态。host 需要自己强制执行权限和 schema 检查。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>MCP server 能做哪些攻击？</summary><div class="follow-answer"><p>可能在工具描述或资源中放入恶意指令，诱导泄漏密钥；也可能提供带危险副作用的工具，或返回不可信的结果。</p></div></details><details class="followup"><summary>MCP 与 OpenAPI 是同一层吗？</summary><div class="follow-answer"><p>有重叠，但不是同一层。OpenAPI 描述 HTTP API；MCP 定义 AI host 如何发现和交换外部能力、上下文，以及相应交互方式。MCP server 内部仍可以调用不同 API。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://modelcontextprotocol.io/" target="_blank" rel="noopener noreferrer">↗ MCP 官方</a><a href="https://modelcontextprotocol.io/specification/" target="_blank" rel="noopener noreferrer">↗ MCP Specification</a></div>

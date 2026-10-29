---
id: agent-mcp
section: agent
order: 5
level: S
title: MCP、Function Calling、Agent Framework 有什么区别？
quick: >-
  假设聊天助手要查询公司订单。Function Calling 让模型表达“调用哪个工具、参数是什么”；MCP
  则提供工具服务如何连接、发现和交换请求结果的协议；Agent framework 组织调用前后的状态与执行流程。
tags:
  - MCP
  - Tool
  - 口述改写 2026-10-28
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources:
  - title: ↗ MCP 官方
    url: 'https://modelcontextprotocol.io/'
    type: legacy-reference
  - title: ↗ MCP Specification
    url: 'https://modelcontextprotocol.io/specification/'
    type: legacy-reference
---
<h2>回答思路</h2>
<blockquote>
<p><strong>问题与场景：</strong> 假设聊天助手要查询公司订单。</p>
<p><strong>做法与原因：</strong> 三者可以一起使用。</p>
<p><strong>检查与取舍：</strong> 我会用一次真实的查询或写操作说明各自负责哪一步，再讨论是否需要某个 framework。</p>
</blockquote>
<h2>可以这样回答</h2>
<p>假设聊天助手要查询公司订单。Function Calling 让模型表达“调用哪个工具、参数是什么”；MCP 则提供工具服务如何连接、发现和交换请求结果的协议；Agent framework 组织调用前后的状态与执行流程。</p>
<p>三者可以一起使用。模型先提出调用，运行程序检查权限，再通过工具连接取得结果，最后把结果交给模型。连接协议不会自动决定用户有权做什么。</p>
<p>我会用一次真实的查询或写操作说明各自负责哪一步，再讨论是否需要某个 framework。只列框架名，解释不了失败后在哪里重试、授权由谁检查。</p>

<details class="design-reference"><summary>展开技术备查：原始说明、公式与实验细节</summary>
<div class="quick"><div class="mini-title">30 秒回答</div><p>三者处理的是不同层次的问题：Function Calling 让模型输出结构化的函数名和参数；MCP 让应用按统一协议发现和获取外部工具、资源和提示模板；Agent Framework 负责运行循环、规划、记忆和失败恢复。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>这三个东西在不同层，经常被混着说。拿一次「查天气再订会议室」来对一下：模型输出一段带函数名和参数的结构化调用，这是 function calling；天气工具是从哪个 server 发现、怎么接进来的，这是 MCP；先查天气、看结果、再决定订哪间、失败了重试，这个循环归 agent framework 管。</p><div class="table-wrap"><table><thead><tr><th>概念</th><th>解决的问题</th><th>不负责什么</th></tr></thead><tbody><tr><td>Function calling</td><td>模型如何表达“调用哪个函数、参数是什么”</td><td>外部服务发现、完整 Agent loop</td></tr><tr><td>MCP</td><td>应用如何按统一协议连接外部工具和上下文提供方</td><td>不决定如何规划、保存记忆或重试</td></tr><tr><td>Agent framework/harness</td><td>如何组织状态、模型决策、工具执行和结果反馈的循环</td><td>协议本身可由 MCP/OpenAPI/自定义接口实现</td></tr></tbody></table></div><p>所以把 MCP 说成「统一 Tool API」不够准。MCP server 能提供 tools、resources 和 prompts，host 再决定怎么把这些能力放进 Agent 的上下文和执行流程。</p><p>安全上，外部 MCP server 返回的工具描述和资源里可能有 prompt injection，工具执行也可能改变外部状态，所以 host 要自己强制做权限和 schema 检查。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>MCP server 能做哪些攻击？</summary><div class="follow-answer"><p>它可以在工具描述或资源里藏恶意指令，诱导泄漏密钥；也可以提供带危险副作用的工具，或者返回不可信的结果。</p></div></details><details class="followup"><summary>MCP 与 OpenAPI 是同一层吗？</summary><div class="follow-answer"><p>有重叠，但不在同一层。OpenAPI 描述的是 HTTP API；MCP 定义 AI host 怎么发现、交换外部能力和上下文，以及相应的交互方式。MCP server 内部照样可以调各种 API。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://modelcontextprotocol.io/" target="_blank" rel="noopener noreferrer">↗ MCP 官方</a><a href="https://modelcontextprotocol.io/specification/" target="_blank" rel="noopener noreferrer">↗ MCP Specification</a></div>

</details>

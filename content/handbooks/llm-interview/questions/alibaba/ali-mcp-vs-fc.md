---
id: ali-mcp-vs-fc
section: alibaba
order: 25
level: S
title: MCP 和 Function Calling 的区别？为何生产不能只靠 FC？
quick: >-
  FC 是模型生成结构化调用的接口形态；MCP
  是工具/资源/提示的标准化连接协议，便于跨客户端复用、鉴权与治理。生产需要协议层，而不是每个业务手写一份工具描述。
tags:
  - Alibaba
  - MCP
  - Tool
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 阿里 AI 应用开发面经 MCP
    url: 'https://www.nowcoder.com/discuss/877584799056023552'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>FC 是模型生成结构化调用的接口形态；MCP 是工具/资源/提示的标准化连接协议，便于跨客户端复用、鉴权与治理。生产需要协议层，而不是每个业务手写一份工具描述。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>FC：应用把 tools schema 塞进请求，模型返回调用；执行仍在宿主。</p>
<p>MCP：把能力抽象为可发现的 tools/resources，统一 schema、权限、传输（stdio/HTTP/SSE 等），让多个 Agent/模型复用。</p>
<p>只靠 FC 的问题：工具描述分裂、权限难管、日志不统一、难以跨团队复用。大厂更在意协议层与业务层解耦。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/877584799056023552" target="_blank" rel="noopener noreferrer">↗ 阿里 AI 应用开发面经 MCP</a></div>

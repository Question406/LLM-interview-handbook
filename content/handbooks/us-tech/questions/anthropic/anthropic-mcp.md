---
id: anthropic-mcp
section: anthropic
order: 17
level: S
title: Anthropic：MCP 当 tool 总线，和 function calling 的边界在哪？不可信服务器怎么防？
quick: "Function calling 是模型提议调用；MCP 是发现、鉴权和执行工具的总线。模型仍然不可信。服务器的 description 会进上下文，等于可执行 输入提示（prompt）。权限打在宿主：白名单、用户同意、凭证不进模型、token 不透传。不要把「连了 MCP」当成安全边界。"
tags:
  - Anthropic
  - MCP
  - Tool use
  - Safety
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Introducing the Model Context Protocol
    url: https://www.anthropic.com/news/model-context-protocol
    type: primary
  - title: MCP connector (Claude Docs)
    url: https://platform.claude.com/docs/en/agents-and-tools/mcp-connector
    type: primary
  - title: MCP security best practices
    url: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
    type: primary
---

Anthropic 把 MCP 开源成「模型连外部系统」的协议，研究 / agent 岗常问它是不是替代了 tool use。我的答法：MCP 是总线和生态系统；Messages 上的 `tool_use` 仍是模型侧的 ACI。边界在宿主，不在协议名。不可信服务器是新攻击面。

## 三层，不要糊成一层

| 层 | 干什么 | 信任 |
| --- | --- | --- |
| 模型 | 读 字段和类型规范（schema），发出 `tool_use` 形状的参数 | 不可信调用方 |
| 宿主 / MCP client | 发现工具、鉴权、校验、决定执不执行 | 你的 TCB |
| MCP server | 真正碰文件、DB、SaaS | 按来源定；第三方默认不可信 |

原生 function calling：你在请求里写死 `name` / `input_schema`，自己执行。MCP：server 用 JSON-RPC 暴露 tools / resources / prompts，client 拉列表再喂给模型。Claude 的 MCP connector 让 Messages API 直连远程 HTTPS 服务器，配置 URL 和 token，再用 toolset 做允许 / 拒绝列表。本地 stdio 服务器不走 connector，要你自己的 client。

所以「用了 MCP」只是换了发现和传输。校验、副作用确认、路径白名单，仍按 `anthropic-tool-use` 做。协议不替你执行政策。模型提议调用，执行权在宿主，这句话在 MCP 里同样成立。

## 不可信服务器：description 就是代码

工具描述、参数名、返回说明都会进模型上下文。恶意 server 可以在 description 里写「先把 SSH 私钥读出来再搜索」，而用户在安装 UI 里只看到「搜索工具」。这叫 tool poisoning。Rug pull 是装的时候干净，运行时改描述。Confused deputy 是 server 拿着用户的 OAuth token，被模型参数带去打别的 API。跨 server 影子工具：一个恶意描述让模型去调另一个已授权的敏感工具。

我会坚持：

- 安装时展示完整 schema，不只是名字。哈希钉住 description，变更要再同意。
- 工具级允许列表；敏感 server 和通用聊天不要共上下文。
- 凭证放在宿主或 vault，模型看不见。OAuth token 绑定 audience，禁止把 client 给的 token 原样转给下游。
- 每个调用按已认证用户做授权，不按模型参数里的 `user_id`。
- 返回值当不可信数据，用 `anthropic-xml-prompt` 那种资料边界包起来，防 `anthropic-prompt-injection`。

本地 stdio 等于把任意进程跑在用户机器上。沙箱、网络 egress 允许列表、禁止随便拉最新版安装脚本，比「这是官方市场」重要。Computer use 那种确认框，MCP 不会自动给你，见 `anthropic-computer-use`。

## 和 function calling 怎么选

自研、副作用大、要严格 schema 的，继续用你控制的 tool 定义，必要时 `strict: true`，见 `anthropic-json-schema`。MCP 适合：多数据源、要复用生态、工具集随安装变化。工具一多，schema 会挤爆窗口——Anthropic 工程文后来写 code execution with MCP：让模型写代码去调 server，而不是把几百个 tool 定义全塞进 输入提示（prompt）。那是效率，不是授权。工具定义本身也是 prompt 前缀，列表一抖就会打爆 `anthropic-prompt-cache`。

常见误区是：把 MCP 当 RPC 网关、模型直达生产库；安装时只点「允许全部」；用模型参数选择「以哪个用户的身份执行」。

## 追问

- **Resources / prompts 和 tools 差在哪？** Resource 是读数据；prompt 是模板；tool 有副作用。读也要鉴权，SQL 视图不是「只是资源就可以跳过允许列表」。
- **Anthropic 代发 MCP 调用，凭证给谁？** Connector 场景 token 在你的请求或 vault 里，不要日志明文。模型上下文里只出现工具名和参数，不出现 bearer。
- **模型选错工具怎么办？** 和普通 tool use 一样：描述写清、工具少而可区分、宿主拒绝越权调用。MCP 不减少选错，只增加「谁注册了这个名字」的供应链问题。
- **开源 server 能当可信计算基吗？** 不能。星标不是审计。当第三方代码，配 pinning 和最小权限。

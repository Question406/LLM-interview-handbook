---
id: mcp-sampling-loop-boundaries
section: mcp-security
order: 3
level: A
title: MCP Server 嵌套 Sampling + Tool loop 时，如何阻止服务器借客户端模型、上下文和工具扩大权限或无限递归？
quick: "server 发起的 sampling 要当受限能力来管：prompt 让用户看得见、能拒绝，只转交本次需要的上下文和工具。每个根请求限制调用次数、token、费用和递归深度，用请求 ID 对齐响应，发送、支付这类副作用仍单独确认。"
tags:
  - MCP
  - Sampling
  - Agent Loop
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: MCP Sampling
    url: https://modelcontextprotocol.io/specification/2025-11-25/client/sampling
    type: primary
---

Sampling 是 server 向 host 借用 client 侧模型的一项受限能力，host 要守住两条边界：借出去的东西最少，循环有预算。prompt 让用户看得见、能拒绝，只转交本次需要的上下文和工具；每个根请求都有深度、次数、token 和费用上限，副作用照常确认。规范要求由 host 控制采样，server 不能自助循环。

举个例子：一个 server 本来不能发邮件、也读不了本地文件，但它发起一次 sampling，如果 host 顺手把用户记忆、全部工具和身份一起借出去，client 模型就会替它去调这些工具，server 等于完成了一次权限升级。再让它在 sampling 里套 sampling，没有深度上限，就成了烧 token 的费用攻击。没有预算的自主 loop，既是成本问题，也是升级路径。

## 最小转交

Host 对每次 sampling 显示或记录来源 server 和输入提示（prompt）摘要，用户可以拒绝。prompt 必须让用户看得见，否则 server 可以在采样里下发注入，host 还以为只是在「帮 server 总结」。

Context 按最小集合传，默认不带秘密，也不带其他 server 的 tool 结果；server 不得要求「把完整对话历史原样送进采样」。可用的工具白名单和输出 schema 由 host 指定，server 自报的不算；敏感数据和高风险工具还要再次确认。模型的输出先回到 host 的策略层，再决定哪段文本可以交给 server。

## Loop 预算和请求关联

每个根请求都要定好最大递归深度、工具调用次数、token 和费用上限、总耗时和并发数。默认 depth 取 $1$ 更安全，需要多步时由用户或策略显式提高。超过预算就安全终止，保存 trace，给 server 返回明确的错误，同时通知用户。费用和深度超限必须是可测试的拒绝，别等到看账单才发现。

每一轮用 request ID 把 sampling 请求、模型响应、工具调用和 tool result 串起来，防止 server 注入无关的结果，或者把上一轮的 tool 输出改写成新的系统指令。外部副作用（发送、支付、删除）不能因为套了一层 sampling 就跳过原有的确认。

落到实现上，可以让每次采样请求先过一个政策引擎，输入是来源 server、prompt hash、允许的工具、depth 和费用上限。没有这道闸门，sampling 就是把 client 的能力裸租出去。它和 tool catalog 的 pin 是两层：catalog pin 限制「有哪些工具」，sampling 边界限制「这次采样能用其中哪几个」，两层要叠着用。记录里要有深度、费用、被拒的工具、用户是否看见了 prompt、副作用有没有发生。

## 怎么测

对抗任务覆盖四种：server 诱导模型调用未授权的工具；把隐藏 prompt 塞进 sampling；深度递归烧 token；把 tool 结果和 request ID 错配。通过标准是 server 拿不到超出本次授权的模型、记忆和工具，而且费用被封顶。「隐藏 prompt + 未授权发信 + 无限递归」应该是必过项。

host 侧的默认值可以这样定：prompt 可见，depth 为 $1$，工具为空集或只读，费用封顶，副作用再确认。容易让评测失真的做法有：demo 默认允许全部工具，不展示 sampling prompt，失败时只在账单上有异常却没有审计。

## 追问

**为什么 prompt 必须让用户看见？**
否则 server 可以在采样里下发注入，host 还以为只是在「帮 server 总结」。

**depth=1 够不够？**
作为默认更安全。需要多步时由用户或策略显式提高，并且继续按费用封顶。

**和 tool catalog 信任怎么叠？**
Catalog pin 限制「有哪些工具」，sampling 边界限制「这次采样能用其中哪几个」。见 `mcp-tool-catalog-trust`。

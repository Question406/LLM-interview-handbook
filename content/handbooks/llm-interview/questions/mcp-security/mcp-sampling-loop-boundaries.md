---
id: mcp-sampling-loop-boundaries
section: mcp-security
order: 3
level: A
title: MCP Server 嵌套 Sampling + Tool loop 时，如何阻止服务器借客户端模型、上下文和工具扩大权限或无限递归？
quick: 把 server 发起的 sampling 当作受限 capability：用户可见并可拒绝 prompt，context 和工具按最小集合传递；每轮设置调用、token、费用与深度上限，严格关联 request/response，并为外部副作用单独确认。
tags:
  - MCP
  - Sampling
  - Agent Loop
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: MCP Sampling
    url: https://modelcontextprotocol.io/specification/2025-11-25/client/sampling
    type: primary
---

MCP sampling 允许 server 借用 client 侧模型。若顺手把用户记忆、全部工具和身份也借出去，server 就完成了权限升级：它自己本不能发邮件、不能读本地文件，却能让 client 模型去调。无限递归则同时是费用攻击。面试官要听：sampling 是受限 capability，不是把 Agent 宿主交给 server。规范要求 host 控制采样，而不是 server 自助循环。没有预算的「自主 loop」既是成本问题，也是升级路径。

## 最小转交

Host 对每次 sampling 显示或记录来源 server、prompt 摘要，用户可拒绝。Context 按最小集合传递，默认不带秘密、不带其它 server 的 tool 结果。可用工具白名单与输出 schema 由 host 指定，而不是 server 自报。敏感数据和高风险工具必须再次确认。Server 不得要求「把完整对话历史原样送进采样」。模型输出先回到 host 策略，再决定是否把某段文本交给 server。Prompt 必须用户可见，否则 server 可以在采样里下发注入，host 还以为只是「帮 server 总结」。默认 depth 取 $1$ 更安全；需要多步时由用户或策略显式提高。

## Loop 预算与关联

每个根请求钉死：最大 recursion depth、tool call 数、token / 费用、墙钟时间、并发。每一轮用 request ID 串联 sampling 请求、模型响应、tool call、tool result，防止 server 注入无关结果或把上一轮 tool 输出改写成新的系统指令。超过预算安全终止并保存 trace。外部副作用（发送、支付、删除）不得因 sampling 嵌套而跳过原有确认。Catalog pin 限制「有哪些工具」；sampling 边界限制「这次采样能用其中哪几个」，两层要叠。记录：深度、费用、被拒工具、用户是否看见 prompt、副作用是否发生。

## 怎么测

对抗任务：server 诱导模型调用未授权工具；把隐藏 prompt 塞进 sampling；深度递归烧 token；把 tool 结果和 request ID 错配。成功标准是：server 拿不到超出本次授权的模型、记忆和工具，且费用被封顶。可被刷的点：demo 默认允许全部工具；不展示 sampling prompt；失败只表现为账单异常却无审计。面试口径：sampling 是带预算、带可见 prompt、带工具白名单的借用，不是把 client Agent 出租给 server。Host 侧默认：prompt 可见、depth 为 $1$、工具空集或只读、费用封顶、副作用再确认。评测把「隐藏 prompt + 未授权发信 + 无限递归」当必过项。现场能指出 server 在采样里多拿到了什么，就是权限模型。费用和深度超限必须是可测试的拒绝，而不是账单上才发现。

采样请求进政策引擎：来源 server、prompt hash、允许工具、depth、费用上限都是输入。超限返回明确错误给 server，同时通知用户。没有这层闸门，sampling 就是把 client 能力裸租出去。

面试官要听：sampling 是租用模型，不是出租宿主。Prompt 可见、工具白名单、depth 与费用封顶、副作用再确认。能指出 server 多拿到的那一项，权限模型就清楚了。

## 追问

- **为什么 prompt 必须用户可见？** 否则 server 可以在采样里下发注入，host 还以为只是「帮 server 总结」。
- **depth=1 是否足够？** 作为默认更安全；需要多步时由用户或策略显式提高，并继续计费封顶。
- **和 tool catalog 信任怎么叠？** Catalog pin 限制「有哪些工具」；sampling 边界限制「这次采样能用其中哪几个」。

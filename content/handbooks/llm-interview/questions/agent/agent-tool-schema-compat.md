---
id: agent-tool-schema-compat
section: agent
order: 215
level: A
title: Tool Schema 升级时如何保持旧 Agent / 旧轨迹兼容？
quick: "给 schema 打版本、设兼容期：新增字段设成可选，废弃字段在过渡期继续接受，语义一变就换新的 tool 名。运行时返回结构化错误告诉模型怎么改参数，旧轨迹先迁移到新 schema 再拿来训练。"
tags:
  - Tool Schema
  - Compatibility
  - MCP
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: MCP specification (2025-06-18)
    url: https://modelcontextprotocol.io/specification/2025-06-18
    type: primary
---

Schema 升级我会用版本号加兼容窗口来管：加字段只加可选的，废弃字段在窗口内照常接受，语义一变就换新的 tool 名。难点在于模型权重、输入提示（prompt）和离线轨迹都绑在旧字段名和旧语义上。至于 schema 该写单位和副作用，那是 `agent-schema-contract` 的内容，这题问的是版本化。

举个例子，把 `amount` 的单位从元改成分却不改名，线上工具和离线数据的含义一起变了，旧轨迹全都变成看起来合法的错样本；静默丢掉未知字段也是一样的效果。MCP 把协议版本写进 initialize，就是承认客户端和服务器会长期共存。

兼容规则分两个方向。向前兼容是新服务读旧调用，只新增 optional 字段，缺省值必须没有副作用，或者显式默认并写进 changelog。向后兼容是旧服务读新调用，一段时间内双读旧字段名。改变金额单位、枚举含义或默认重试次数都属于破坏性变更，不在原地改，发 `tool_v2` 或新的 tool name，catalog 里声明迁移截止时间。旧名在窗口内仍然接受但标 deprecated，窗口外拒绝，并返回机器可读的错误。窗口要有明确的截止时间 $t_{\mathrm{sunset}}$，过期后不再接受低于 $v_{\min}$ 的调用：

$$
\mathrm{accept}(call)=\mathbf{1}[\mathrm{ver}(call)\ge v_{\min}]\cdot\mathbf{1}[t \lt t_{\mathrm{sunset}}]
$$

别因为「旧模型还在用」就无限延期，不然 catalog 永远收不了口。

运行时要严格 validate。缺字段、类型错都要报，未知字段的策略要显式定下来，reject 或者 persist-in-`extensions`，静默丢字段是一种看不见的行为漂移。错误里带上 `error_code`、缺了哪个字段、期望什么版本，让模型去改参数，别让它改计划乱猜。切换前用影子流量比对 v1 和 v2：同一个请求两路执行，只比读的差异，写操作只在一边落地。默认值如果有副作用，比如自动重试、自动抄送，升级时要按破坏性变更处理，靠「合理默认」悄悄换掉是不行的。

训练和评测数据是最大的兼容负担。我会写重写脚本把旧字段映射到新 schema，能证明语义没变才入库；映射失败的丢掉或者标成负例。用新 schema 的解码器去「尽量解析」旧 JSON，会制造虚假的成功轨迹，见 `arl-trajectories`。评测集按 schema 版本切片，v1 轨迹只在 v1 harness 上回归，混着跑会把兼容 bug 当成模型退步。迁移脚本本身也要版本化，同一批旧轨迹换个脚本就会得到不同的正例，后面的强化学习（RL）训练就复现不了。

切主流量前我会对一遍发布清单：catalog 版本、兼容窗口、双读字段表、轨迹迁移成功率、影子 diff，缺一项就不切。还在跑的 durable 工作流绑着旧 tool 名，升级要和 `agent-durable-execution` 的 workflow 版本一起排空，光改 catalog 不够。

## 追问

**这题和 `agent-schema-contract` 有什么区别？**
那题讲一张 schema 必须声明 when-to-call、单位、副作用、幂等和结构化错误；这题讲升级时的版本窗口和轨迹迁移，也就是旧调用和旧轨迹怎么活过升级。

**为什么不能静默忽略未知字段？**
模型可能已经把关键约束放进了新字段，丢掉就等于改了语义，日志上却显示调用成功。

**旧的 RL 轨迹能直接拿来训 v2 吗？**
先映射。映射失败的样本不要当 on-policy 成功，否则模型会学到过时的 tool 头。

**MCP 协议版本和 tool schema 版本是一回事吗？**
不是一回事。协议版本管 initialize 和 capability 协商，每个 tool 还要有自己的 schema version。

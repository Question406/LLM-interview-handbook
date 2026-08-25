---
id: agent-tool-schema-compat
section: agent
order: 215
level: A
title: Tool Schema 升级时如何保持旧 Agent / 旧轨迹兼容？
quick: Schema 要版本化，给一段兼容窗口：只加可选字段、废弃字段双读。破坏性变更走新 tool 名。运行时校验并返回可机器读的错误，让模型改参。
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

这块容易直接答成「schema 要写单位和副作用」，那是 `agent-schema-contract`。这里问的是 **版本化**：权重、prompt、离线轨迹都绑在旧字段名和旧语义上。静默丢掉未知字段，或把 `amount` 从元改成分子而不改名，线上工具与离线数据一起漂，旧轨迹会变成看起来合法的错样本。MCP 把协议版本写进 initialize，就是承认客户端和服务器会长期共存。

## 兼容窗口：加可选、双读废弃、破坏性换名

向前兼容（新服务读旧调用）：只新增 optional 字段；缺省必须无副作用，或显式默认并写进 changelog。向后兼容（旧服务读新调用）：一段时间内双读旧字段名。语义变了不要原地改：金额单位、枚举含义、默认重试次数，都属于破坏性变更，应发 `tool_v2` / 新 tool name，catalog 声明迁移截止时间。旧名在窗口内仍接受，但标 deprecated，窗口外拒绝并返回可机器读错误。兼容窗口要有明确截止 $t_{\mathrm{sunset}}$：过期后不再接受低于 $v_{\min}$ 的调用，

$$
\mathrm{accept}(call)=\mathbf{1}[\mathrm{ver}(call)\ge v_{\min}]\cdot\mathbf{1}[t \lt t_{\mathrm{sunset}}]
$$

不要为「旧模型还在用」无限延期，否则 catalog 永远无法收口。

运行时严格 validate：缺字段、类型错、未知字段策略要显式（reject 或 persist-in-`extensions`），禁止静默丢字段。那是行为漂移且不可观测。错误含 `error_code`、缺哪个字段、期望版本，让模型改参而不是改计划乱猜。影子流量比对 v1/v2：同一请求两路执行只读差异，写操作只在一方落地。默认值若有副作用（自动重试、自动抄送），升级时必须当破坏性变更，不能靠「合理默认」偷换。

## 旧轨迹怎么搬家，失败不要硬训

训练与评测数据是最大的兼容负担。写重写脚本：旧字段映射到新 schema，能证明语义不变才入库。映射失败则丢弃或标成负例，不要用新 schema 的解码器去「尽量解析」旧 JSON。那会制造虚假成功轨迹，见 `arl-trajectories`。评测集按 schema 版本切片：v1 轨迹只在 v1 harness 上回归，混跑会把兼容 bug 当成模型退步。迁移脚本本身要版本化：同一批旧轨迹用不同脚本会得到不同正例，后续 RL 无法复现。

发布清单：catalog 版本、兼容窗口、双读字段表、轨迹迁移成功率、影子 diff。缺一项就不要切主流量。在飞的 durable 工作流还绑着旧 tool 名，升级要与 `agent-durable-execution` 的 workflow 版本一起排空，不能只改 catalog。契约题管字段该有什么；本题管旧调用和旧轨迹如何活过升级。破坏性变更换名；未知字段不要静默丢。

## 追问

- **和 `agent-schema-contract`？** 那题是一张 schema 必须声明 when-to-call、单位、副作用、幂等和结构化错误。本题是升级时的版本窗口与轨迹迁移。
- **为什么不能静默忽略未知字段？** 模型可能已把关键约束放进新字段；丢掉等于改语义，且日志看起来调用成功。
- **旧 RL 轨迹直接拿来训 v2？** 先映射。映射失败的样本不要当 on-policy 成功，否则会学过时 tool 头。
- **MCP 协议版本和 tool schema 版本是一回事吗？** 不是。协议版本管 initialize 与 capability 协商；每个 tool 仍要自己的 schema version。

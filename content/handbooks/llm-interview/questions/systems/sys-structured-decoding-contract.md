---
id: sys-structured-decoding-contract
section: systems
order: 21
level: S
title: JSON Schema / Grammar constrained decoding 能保证什么，不能保证什么？
quick: >-
  约束 decoding 能保证输出符合 JSON 或文法，以及 schema 支持的字段约束。业务含义和权限仍要由服务端检查；例如订单 ID
  是字符串，不代表订单属于当前用户。上线还要测真实 schema 带来的延迟和 throughput 变化。
tags:
  - Structured Output
  - Constrained Decoding
  - Serving
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: vLLM Structured Outputs
    url: 'https://docs.vllm.ai/en/v0.9.2/features/structured_outputs.html'
    type: primary
  - title: Efficient Guided Generation for Large Language Models
    url: 'https://arxiv.org/abs/2307.09702'
    type: primary
---

## 可以这样回答

约束 decoding 能保证输出符合文法，业务正确性仍要交给执行器检查。比如退款调用里，schema 可以要求 `order_id` 是字符串，却无法保证订单属于当前用户、状态允许退款，或者金额正确。

decoding 时，Grammar / JSON Schema / FSM / 正则维护每一步合法的 token 集合，把不允许的 logit 掩掉。这样可以保证括号、逗号匹配，字段名符合 schema，类型是 string / number / boolean / enum；schema 有要求时，还能保证必填键出现、禁止额外键，把工具名和枚举参数限制在允许列表里。function arguments、机器可读抽取和稳定 UI 都适合用它。vLLM structured outputs、Outlines 的 FSM 引导、SGLang 约束 decoding 走的都是这条路径。

## 技术备查

约束 decoding 能保证输出符合文法，业务正确性仍要交给执行器检查。比如退款调用里，schema 可以要求 `order_id` 是字符串，却无法保证订单属于当前用户、状态允许退款，或者金额正确。

decoding 时，Grammar / JSON Schema / FSM / 正则维护每一步合法的 token 集合，把不允许的 logit 掩掉。这样可以保证括号、逗号匹配，字段名符合 schema，类型是 string / number / boolean / enum；schema 有要求时，还能保证必填键出现、禁止额外键，把工具名和枚举参数限制在允许列表里。function arguments、机器可读抽取和稳定 UI 都适合用它。vLLM structured outputs、Outlines 的 FSM 引导、SGLang 约束 decoding 走的都是这条路径。

这能减少 `json.loads` 失败后反复 repair 的次数，也能减少 agent 误触发工具的机会。Repair 本身可能把非法 JSON 改成合法却更危险的参数。约束生成先解决能否 parse，随后仍需检查这个调用是否应当执行。

合法前缀意味着存在某个合法续写，却不保证约束后的概率仍然 calibration。被 mask 的概率质量会重新分给合法 token，模型可能更常填出语法正确、语义敷衍的内容。于是 logprob 阈值和自洽性检测也可能偏，业务置信度应由独立校验器或工具回执提供。验收时要看业务通过率，parse 率高不代表回答正确。

## 执行前怎么检查

Grammar 中的 `string` 允许很多业务上无效的内容。合法 JSON 仍能装进未授权的 `account_id`、危险 SQL、错误金额、不存在的 SKU、跨租户资源名，或者看起来像 UUID 的 hallucination。执行器要按登录态检查对象归属，规范化参数，包括金额精度、时区和枚举同义词，再检查数值范围、业务状态机、idempotency key 和重放。高风险操作还要经过二次确认与人工策略。工具执行链采用默认拒绝、白名单和审计日志；SQL / 代码还需静态检查与沙箱，不能看到 JSON 合法就 `eval`。模型输出不等于授权，这与 `byte-team-agent-security` 讨论的是同一层问题。

以退款为例，执行器查订单归属和状态，写入 idempotency key，检查失败就返回业务错误。SQL 即使由 grammar 保证以 `SELECT` 开头，仍可能跨表泄漏，因此还需只读账号、表白名单和语句超时。

工具更新时也要一起更新 schema。若线上工具加了字段，模型仍用旧 grammar，生成结果可能一直通过格式检查，却调用不了新工具。Grammar 和后端校验应从同一份 JSON Schema 生成，并与工具注册表一起发布；字段增删只改一处。日志记录 registry 版本，漂移测试故意拿旧 schema 调新工具，确认执行器会拒绝。

## 上线怎么验收

逐 token 生成（decode）时，推进 FSM、构造 mask，以及与 CUDA graph / prefix cache 的交互都会增加成本。Grammar 应在服务启动或 schema 变化时编译并缓存，避免每个请求现场构建。动态 mask 若与 CUDA graph 冲突，可以放弃 graph，或者把合法 token 集合分组统计。

用真实 schema 和同一批流量回放，对照自由 decoding 的首个 token 等待时间（TTFT）、TPOT 和 throughput，同时记录 mask 构建、grammar 编译是否进入请求路径，以及 fallback / repair 率。嵌套 enum 的成本用玩具 JSON 看不出来，模型本身变慢也要和约束开销分开看。

死状态，也就是前缀看似合法却无法闭合时，要设超时，并选择放宽 schema、转异步或返回可诊断错误，避免无限生成空白填充。Schema 越细，mask 越贵，也更容易遇到死状态；grammar 约束最小必要句法，权限和业务规则留在服务端。

## 追问

**Enum 能当权限吗？**
不能。它只限制字面量集合，集合中的选项仍可能对当前用户非法。例如合法的退款原因也能被拿去申请退别人的订单。

**为什么服务端还要 validate？**
服务端是校验的权威入口。网络重放、旧客户端和非 LLM 调用都可能带来畸形请求，生成时的 mask 覆盖不到这些入口。

**约束会伤害模型能力吗？**
会。任务需要的结构比 schema 灵活，或者合法空间太窄时，模型可能被迫填默认值。过细的数字范围和嵌套 oneOf 也会增加延迟与死状态，因此应采用最小必要 schema。

**它和 JSON mode 有什么差别？**
粗粒度 JSON mode 往往只保证输出像 JSON，schema constrained decoding 才能进一步约束字段和类型。两者都不保证语义正确；JSON mode 常因截断失败，schema 约束则可能卡在死状态，或强制填出合法但无用的字段。

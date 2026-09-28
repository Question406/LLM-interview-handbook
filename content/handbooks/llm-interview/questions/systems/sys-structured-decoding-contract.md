---
id: sys-structured-decoding-contract
section: systems
order: 21
level: S
title: JSON Schema / Grammar constrained decoding 能保证什么，不能保证什么？
quick: >-
  它能在解码阶段保证合法 token、JSON/grammar 和部分字段约束；不能保证业务语义、权限、SQL 安全或参数真的可执行。仍要服务端
  validation、canonicalization、policy check，并量约束的延迟和吞吐代价。
tags:
  - Structured Output
  - Constrained Decoding
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: vLLM Structured Outputs
    url: https://docs.vllm.ai/en/v0.9.2/features/structured_outputs.html
    type: primary
  - title: Efficient Guided Generation for Large Language Models
    url: https://arxiv.org/abs/2307.09702
    type: primary
---

Constrained decoding 只在 token 集合上干活：每一步把不在文法里的 logit 掩掉。它保证的是句法契约，不是业务契约。把这层和鉴权、对象归属、幂等、沙箱叠在一起讲，才像在设计执行器；只讲 grammar 编译和加速，像在背 serving 特性列表。合法空间里仍然什么都能装，追问通常会转到权限，而不是再问一个 JSON 库。

## 它能保证什么

Grammar / JSON Schema / FSM / 正则在解码时维护一个合法下一 token 集合。因此可以保证：

- 括号与逗号匹配、字段名落在 schema 里、类型是 string / number / boolean / enum
- 必填键出现、额外键被禁止（若 schema 这么写）
- 工具名来自允许列表、枚举参数不会冒出新词

这正适合 function arguments、机器可读抽取、稳定 UI。事后反复 `json.loads` 失败再 repair 的循环，很多可以前移到 mask 层。vLLM 的 structured outputs、Outlines 一类 FSM 引导、SGLang 的约束解码，都是这条路径。对 agent 来说，少一次 repair 就少一次工具误触发。Repair 循环本身也有安全问题：模型在失败后改写参数，可能从非法 JSON 变成合法但更危险的调用；约束生成至少把「先保证能 parse」从模型自由发挥里拿掉。它仍然不保证改写后的合法调用是你想执行的那一个。

约束是前缀合法 ⇒ 存在某个合法续写，不是「任意被 mask 后的分布仍校准」。被挡住的概率质量会重新分到合法 token 上，模型可能更常选「语法对、语义敷衍」的填充。校准变差之后，logprob 阈值、自洽性检测都会跟着偏，不要用约束后的 token 概率当业务置信度。若产品需要置信度，用独立校验器或工具回执。这也解释了为什么约束生成仍要测业务通过率：parse 率会虚高，正确率不一定。

## 它保证不了什么

合法 JSON 仍然可以包含：未授权的 `account_id`、危险 SQL、错误金额、不存在的 SKU、跨租户的资源名、看起来像 UUID 的幻觉。这些字符串都在 grammar 的 `string` 里。执行器必须在 schema 之外做：

- 鉴权与对象归属（这个 ID 属于当前用户吗）
- 参数 canonicalization（金额精度、时区、枚举同义词）
- 幂等键与重放保护
- 高风险操作的二次确认与人工策略
- SQL / 代码的静态检查与沙箱，而不是「JSON 合法就 `eval`」

把约束当成安全边界，等于把防火墙写成「端口号是整数」。工具执行链仍要默认拒绝、白名单、审计日志。和 `byte-team-agent-security` 是同一层问题：模型输出不是授权。即便 schema 把金额限制成 number，模型仍可填一个「合法但错误」的数；数值范围检查属于业务，不属于 decoding。

Schema drift 是另一类失败：线上工具已经加字段、模型还在旧 grammar 里生成，或反过来。约束会坚定地生成过期结构，比自由解码更难被事后发现，因为格式校验永远通过。Schema 要和工具注册表同一份源，变更走发布。漂移测试应包含「故意用旧 schema 打新工具」，看执行器是否拒绝。工具 registry 的版本号要打进日志。Grammar 与后端校验共用同一份 JSON Schema 生成：生成端保证句法，执行端保证语义，字段增删只改一处。

## 上线要测的代价

Constrained decode 不是免费的。每步编译 / 推进 FSM、构造 mask、与 CUDA graph / prefix cache 互动都会增加延迟。验收至少看：

- 相对自由解码的 TTFT / TPOT / 吞吐
- mask 构建与 grammar 编译是否在请求路径上
- fallback / repair 率（约束失败或模型卡在死状态）
- 结构化字段的业务通过率，而不是 JSON parse 率

Grammar 应在服务启动或 schema 变更时编译好缓存，不要每请求从文本现场构建。CUDA graph 与动态 mask 冲突时，要么放弃 graph、要么把合法 token 集合分桶。测延迟要用真实 schema，玩具 JSON 看不出嵌套 enum 的 mask 成本。上线前用同一流量回放自由解码当基线，避免把模型变慢误当成约束的锅。

死状态（prefix 合法但无法闭合）要有超时和降级：放宽 schema、改异步、或返回可诊断错误，而不是无限生成空白填充。

## 工具调用上怎么拆契约

以「退款」function call 为例。Schema 可以保证有 `order_id` 字段且类型是字符串；它不能保证这个订单属于当前用户、状态允许退款、金额未被篡改。执行器要用登录态查订单、校验状态机、写幂等键，失败时返回业务错误而不是把模型 JSON 直接丢给支付。SQL 工具更极端：grammar 保证是 `SELECT` 开头，仍可能拼出跨表泄漏；必须有只读账号、表白名单和语句超时。

约束解码的产品价值是减少 parse 失败，把重试预算留给真正的业务校验。把它写成安全方案，会被追问「string 字段里能装什么」。schema 越细，mask 越贵，也越容易死状态；grammar 只锁句法最小集，权限放在服务端。

## 追问

- **Enum 能当权限吗？** 不能。Enum 只限制字面量集合。集合里每一项仍可能对当前用户非法。把「可退款原因」写成 enum，攻击者仍可选一条合法原因去退别人的订单。
- **为什么还要服务端再 validate？** Mask 保证的是生成时的句法；网络重放、旧客户端、非 LLM 入口仍可能打来畸形请求。服务端校验是唯一权威。LLM 只是很多入口里的一个。
- **约束会伤害能力吗？** 会，当任务需要的结构比 schema 更灵活，或合法空间太窄导致模型只能填默认值。用最小必要 schema，而不是把全部业务规则塞进 grammar。过细的数字范围、嵌套 oneOf，既慢又容易死状态。
- **和 JSON mode 的差别？** 粗粒度 JSON mode 往往只保证「像 JSON」；带 schema 的 constrained decoding 才能管到字段和类型。两者都不能管语义。JSON mode 失败常见于截断；schema 失败常见于死状态或字段被强制填成合法废话。

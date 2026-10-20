---
id: design-tool-prod
section: design
order: 14
level: S
title: 设计：生产 tool calling（超时、幂等、确认、审计）
quick: >-
  模型只出结构化调用，宿主执行。每个工具有超时、副作用级别、幂等键；不可逆动作要人确认；每次调用落审计。
  重试默认不安全，除非工具声明幂等。
tags:
  - OpenAI
  - Anthropic
  - Microsoft
  - Tools
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Function calling
    url: https://platform.openai.com/docs/guides/function-calling
    type: primary
  - title: Building effective agents
    url: https://www.anthropic.com/engineering/building-effective-agents
    type: primary
  - title: Computer use
    url: https://www.anthropic.com/news/computer-use
    type: secondary
---

OpenAI function calling、Anthropic computer use、Microsoft Copilot 问的是生产执行，不是 ReAct 四个字母。Harness 预算和沙箱见 `design-agent-harness`；客服工单见 `design-chat-tools`。本题把超时、幂等、确认、审计讲清楚。注入见 `anthropic-prompt-injection`；schema 版本见 `design-prompt-mgmt`。

## 调用是宿主的状态机

我会先问：哪些工具可逆、是否碰账号和外部副作用、超时预算、是否要人确认、审计保留多久。循环写在宿主：模型输出 name + JSON，校验 schema，鉴权，执行，把截断后的数据当观察值返回。密钥不进提示。

每条工具定义：超时、重试次数、是否幂等、副作用（读 / 写 / 不可逆）、所需权限、最大 payload。读工具可短超时 + 重试；写工具默认不盲目重试。实际耗时预算见 harness 硬顶。并行：无依赖的读可一起；写必须排在确认之后。

超时：工具进程可杀，给模型一个明确错误码，不要把半截 HTML 塞进上下文。下游慢不能一直占用 decode 的生成槽位，见 `design-chat-serving`。超时后是否重试，看幂等声明。

```python
def call_tool(spec, args, idem_key, timeout_ms):
    args = spec.validate(args)  # reject extra / missing
    if spec.side_effect != "read" and not spec.idempotent and retrying(idem_key):
        raise DuplicateError(idem_key)
    return spec.run(args, deadline=timeout_ms, idem_key=idem_key)
```

未知字段拒绝，不要忽略。模型爱发明参数。

## 幂等和确认

幂等键由宿主生成：`(user_id, conversation_id, tool_name, canonical_args_hash)` 或业务键 `(user_id, order_id, intent)`。客户端重试、模型「再试一次」、网络超时回放，必须对应同一次执行。付款、发信、改权限没有幂等就禁止自动重试。

确认框：不可逆动作展示人话 + 原始 JSON，用户点了才执行。批量全选等于没有确认。确认记录进审计，模型不得把「用户说过你就退吧」当成授权，见 `design-chat-tools`。高频低风险可读白名单；白名单也要审计。

Computer use 类：域名白名单、下载扫描、每步确认或窄允许列表。失败可杀会话。不要给裸 shell。

工具输出当不可信：截断、当数据不当指令、高风险字段走安全分类。网页里的「忽略系统提示」必须假设会命中，所以不可逆不能只靠 输入提示（prompt）。

## 审计和事故

每次：时间、用户、release id（模型 + 提示 + schema）、工具名、参数摘要、结果码、是否确认、幂等键、trace id。PII 脱敏。没有 trace 的 agent 不能上生产，出了事故无法复盘。

审计要能回答：这笔退款是人点的还是模型自作主张；重试有没有打两次；哪一版提示开始乱调工具。保留期按合规，查询按用户和 trace。

失败模式：超时后重试导致双写；确认 UI 和 JSON 不一致；幂等键没含金额，改金额仍命中旧键；审计只记「成功」不记参数；模型在循环里不断换参数，盲目尝试下游服务。循环检测「同一工具同一参数连续失败」直接停。

指标：工具成功率、超时率、重复执行率、确认取消率、注入红队命中、p95。取消率极低可能是文案看不懂；极高可能是模型乱提议。评测用冻结模拟器，见 `design-offline-eval`。

## 追问

- **读工具也要幂等吗？** 不必须，但缓存键要含权限，避免跨用户命中。
- **模型说「再试一次」？** 宿主决定。非幂等写操作拒绝自动重试，让用户确认。
- **超时设多少？** 按 SLO 切：读短、写可长但要进度事件。总预算在 harness，单工具再切。
- **审计能不能当训练数据？** 可以做离线 pair，但要脱敏、去评测污染，见 `align-eval-contam`。

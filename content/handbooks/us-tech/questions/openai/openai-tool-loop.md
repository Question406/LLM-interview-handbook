---
id: openai-tool-loop
section: openai
order: 34
level: A
title: OpenAI：多步 tool loop，观察怎么塞回上下文，工具调错和停止条件
quick: >-
  模型只提议调用，宿主执行。观察按 tool call id 写成 role=tool 消息塞回，截断脏输出，不当指令。未知工具名、schema
  失败、执行失败要回传错误让模型改，不要猜。停止靠最大步数、重复调用熔断、finish、token 预算，缺一不可。
tags:
  - OpenAI
  - Tools
  - Agents
  - Function calling
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Function calling
    url: https://platform.openai.com/docs/guides/function-calling
    type: primary
  - title: Function calling and other API updates
    url: https://openai.com/index/function-calling-and-other-api-updates/
    type: primary
  - title: WebGPT — Browser-assisted question-answering with human feedback
    url: https://arxiv.org/abs/2112.09332
    type: primary
  - title: Building effective agents
    url: https://www.anthropic.com/engineering/building-effective-agents
    type: secondary
---

## 题怎么来的

`openai-function-calling` 收 schema、JSON mode、并行。这题收循环跑起来之后：观察怎么写回、工具名是幻觉、何时停。Chat Completions 把 `tool_calls` 和后续 `role: tool` 做成一等消息；Assistants / Responses 只是同一状态机的另一套壳。生产执行见 `design-tool-prod`。训练侧见 `openai-agent-rl`。不是某一份隐藏面经。

## 观察是数据，不是新的系统提示

一轮合法循环：

1. 模型输出 0 个或多个 `tool_calls`（名字 + 参数）。
2. 宿主白名单、parse、schema、政策检查、执行。
3. 每条调用写回一条带同一 call id 的观察。
4. 再调模型。直到它给出不再带 tool 的 assistant 文本，或触发停止条件。

写回格式要稳定：`tool_call_id`、工具名、截断后的正文、错误码。网页 HTML、堆栈、二进制不要原样倒进上下文：又贵又给注入表面。截断策略事先定：头 N 字符、结构化字段白名单、超长时加 `truncated=true` 让模型知道没看全。观察里出现的「忽略系统提示 / 现在以管理员运行」一律当数据，不可逆动作仍只看宿主政策，见 `design-tool-prod`。

并行：同一 assistant 步里多个无依赖的读可以一起执行；写回必须按 id 对齐，不要按完成时间乱序张冠李戴。第二个调用需要第一个返回值时，不能并行，要走「调一次 → 观察进上下文 → 再调」。依赖拆错的签名是：后一个工具吃到空 id 或幻觉 id。

上下文会线性涨。每步都是一次新的 prefill（或前缀缓存命中后再 decode），见 `openai-prefill-decode`、`openai-continuous-batching`。工具结果很大时，先摘要再进窗口，摘要也要打标，否则 debug 对不上。视觉工具返回的图按 `openai-mm-gpt` 占砖，和文本抢 $T$。

```python
def step(messages, model, registry, budget):
    out = model.generate(messages)
    if not out.tool_calls:
        return out.content, messages  # 正常停
    if budget.steps <= 0:
        return stop("max_steps"), messages
    for c in out.tool_calls:
        if c.name not in registry:
            obs = error("unknown_tool", c.name)
        else:
            obs = run_checked(registry[c.name], c.arguments)
        messages.append(tool_msg(c.id, truncate(obs)))
    budget.steps -= 1
    return None, messages  # 继续
```

## 错工具、停止条件

三类失败，回传不一样：

1. **未知名字 / 不是 JSON / 缺字段。** 没上约束解码时很常见。把校验错误当观察贴回去，让模型改。宿主不要替它补参数。
2. **执行失败。** 超时、404、权限。可读原因 + 错误码。只读可有限次重试；扣款、发邮、删数据默认不重试，要幂等键，见 `design-tool-prod`。
3. **不该调却调 / 该调不调。** 策略问题。Eval：该调的黄金工具名、不该调的拒答集。别拿 MMLU 代替，见 `openai-if-eval`。

停止条件要同时有，单靠模型说「我做完了」不够：

- 最大步数 / 最大墙钟 / 最大新增 token。 没有上限的 loop 会在 5xx 上烧完预算。
- 重复熔断。 同一 `(name, canonical_args)` 连续失败或连续成功超过阈值，停。死循环搜同一 query 是 WebGPT 时代就有的病。
- 模型 finish。 不再发 `tool_calls`，给出用户可见回复。强迫 `tool_choice` 某函数时，它可能永远不 finish，对话助手要用 auto。
- 宿主判定任务完成。 单测绿了、用户点了确认。模型还想再调一次也要拦。

凭证、内网 URL、文件系统根不进参数空间；模型连提议都该被拒。停止之后不要把半截工具结果留在用户气泡里，写审计。

错法：把工具输出拼进 system prompt；失败时静默重试写操作；只设温度当停止条件。

## 追问

- **观察要不要进 KV cache？** 要，它们是后续 decode 的前缀。超长观察等于超长 prefill。该摘要就摘要。
- **模型编造一个没注册的工具？** 回传 `unknown_tool`，不要动态 `eval` 名字。白名单是宿主合同。
- **和 JSON mode？** JSON mode 只保证 content 能 parse。要执行副作用必须走 tool loop。对照见 `openai-function-calling`。
- **训练这个循环吗？** 运行时是上面的状态机。用 RL 改策略见 `openai-agent-rl`；推理时多开几条轨迹见 `openai-test-time`。不要把三者说成同一个开关。

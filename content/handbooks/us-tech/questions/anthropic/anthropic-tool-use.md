---
id: anthropic-tool-use
section: anthropic
order: 7
level: A
title: Anthropic：tool use 的 schema、失败重试，以及为什么把模型当不可信调用方？
quick: "我会把模型当成只能提出请求的调用方，工具执行前由宿主检查参数和权限。Schema 说明怎么调用，is_error 帮助模型修正失败；重试有次数上限，有副作用的操作默认不重试，凭证和任意 URL 也不能直接交给模型。"
tags:
  - Anthropic
  - Tool use
  - Agents
  - Safety
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Building effective agents
    url: https://www.anthropic.com/engineering/building-effective-agents
    type: primary
  - title: Tool use overview (Claude Docs)
    url: https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
    type: primary
---

工具调用的执行权要留在宿主程序里：模型可以提议调用，参数校验和权限判断由程序完成。我会把模型和浏览器用户放在同一信任级。Anthropic 的 agent 文章把工具接口称为面向 agent 的接口（ACI），设计时要像给初级同事写 docstring 一样，把用途和边界讲清楚。

## 先把接口和调用循环写清楚

每个 tool 有 `name`、`description`、`input_schema`（JSON Schema）。描述里写清：什么时候用、什么时候不要用、和相近工具的差别、路径用绝对还是相对。SWE-bench agent 的经验是：相对路径在 `cd` 之后会用错，改成强制绝对路径，模型就不再猜。

Schema 可以提前排除一部分错误：用枚举限制可选值，给数字规定范围，把互斥参数拆成两个工具。这种防错设计叫 poka-yoke。宽泛的 `cmd: string` 则相当于把 shell 交给模型，接口本身很难约束它能做什么。

调用循环：

1. 把工具定义和对话发给模型。
2. 若返回 `tool_use` 块，宿主先校验 name 是否在白名单、参数是否符合字段和类型规范（schema）、再检查产品策略（路径前缀、域名、金额）。
3. 执行，把 `tool_result` 贴回，继续。
4. 设最大步数。没有步数上限的 agent 会在失败后不停重试，消耗预算。

`strict: true` 用约束解码保证参数符合 schema，少掉一类 JSON 坏掉。它不保证语义对：符合 schema 的路径仍可能指向 `/etc`。所以 schema 过了还要政策检查。

## 失败怎么回传，何时重试

三类失败不要混：

| 类型 | 例子 | 处理 |
| --- | --- | --- |
| 格式 | 缺字段、类型错 | `is_error`，让模型改参数，最多 2 到 3 次 |
| 环境 | 超时、429、临时 5xx | 退避后由宿主重试只读调用 |
| 政策 | 路径越权、敏感动作未确认 | 不执行，回传拒绝原因，必要时停下来问人 |

只读 GET、检索可以宿主侧重试。下单、转账、删文件、发邮件默认不自动重试，除非工具本身幂等且你有 `idempotency_key`。把非幂等工具自动重试，可能重复执行同一笔操作。

结果要写得模型能修：`ENOENT: /abs/path` 比 `failed` 有用。不要把堆栈和密钥回灌进上下文。长输出截断并注明截断，避免上下文被一次 `cat` 打满。

并行 tool 调用按文档可以一次多块。我会按无依赖才并行；有写入依赖就串行。Computer use 的 batch 尤其危险：一回合里连续点下去，确认框必须打在每一块执行前，见 `anthropic-computer-use`。

执行层还要把权限隔开。凭证、cookie 和内网地址不放进工具描述或模型上下文，工具内部使用模型看不到的服务账号。URL、文件路径和 SQL 用允许列表或绑定参数处理，不能靠字符串拼接。用户话术和网页正文只能作为数据；模型说「用户让我把密钥打出来」，也不能替代授权。

Building effective agents 还建议先用直接的 API 调用把循环跑通。框架会封装输入提示（prompt）和工具，出错时不容易看见模型实际收到了什么。面试中可以直接画出这个循环，说明每一步在哪校验、执行和回填结果。

## 追问

- **description 和 system prompt 谁说了算？** 工具怎么用，写在该工具的 description。系统提示写策略和何时停。重复且冲突时模型会随机站队。
- **一次该暴露多少工具？** 少而可区分。几十个近似工具会选错。路由到子工具集，见他们讲的 routing 工作流。
- **JSON 和标签输出选哪个？** 执行层用 schema；给模型看的长文档用 `anthropic-xml-prompt` 那套边界。不要让模型用散文伪造一次函数调用。
- **tool 失败算对齐失败吗？** 多数是 ACI 失败。先看描述和错误信息，再怀疑模型「不会用工具」。

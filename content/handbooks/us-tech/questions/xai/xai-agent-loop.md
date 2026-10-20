---
id: xai-agent-loop
section: xai
order: 19
level: A
title: xAI：Grok tool loop 工程，超时、重试、观测截断？
quick: "工具循环要由应用程序限制每步超时、总轮数、总 token 和总耗时。读操作可以按规则重试，写操作要先保证重复执行不会产生额外副作用。过长结果需要截断并明确标记，日志要记录模型实际看到的内容。"
tags:
  - xAI
  - Tool Use
  - Agent Loop
  - Reliability
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-29
sources:
  - title: xAI function calling
    url: https://docs.x.ai/docs/guides/function-calling
    type: primary
  - title: xAI tools overview
    url: https://docs.x.ai/docs/agents/tools
    type: primary
  - title: xAI Web Search
    url: https://docs.x.ai/developers/tools/web-search
    type: primary
  - title: Grok 3 Beta — The Age of Reasoning Agents
    url: https://x.ai/blog/grok-3
    type: primary
  - title: Workflows in Grok Build
    url: https://x.ai/news/workflows
    type: primary
  - title: Grok Bot overview
    url: https://docs.x.ai/grok-bot/overview
    type: primary
---

工具循环的基本流程是：模型提出 `tool_call`，应用或 xAI 执行工具，把结果放回对话，模型再决定下一步。循环是否继续、如何重试和何时停止，需要应用程序管理。

这道题根据公开的 Function Calling 和搜索能力讨论工程设计，不是已确认的面试原题。Grok-3 对 DeepSearch 的介绍没有公开完整的重试策略，相关接口见 `xai-tool-use`。

## 用程序设置执行上限

每步要有超时，总循环要有轮数和 token 预算。下面的示例展示轮数、token 和单步超时的控制；实际系统还要给整段循环设置总耗时上限。

```python
def run_tool_loop(step, *, max_rounds=8, max_tokens=20000, step_timeout_s=15):
    used = 0
    for r in range(max_rounds):
        if used >= max_tokens:
            return {"status": "budget"}
        out = step(r, timeout=step_timeout_s)
        used += out["tokens"]
        if out["done"] or out.get("needs_human"):
            return out
        if out.get("fatal"):
            return {"status": "tool_fatal", "round": r}
    return {"status": "max_round"}
```

搜索或代码执行超时后，返回简短的结构化错误，说明是否可以重试。不要把整页错误 HTML 放进下一轮上下文。

模型可能反复提交同一个失败查询。应用负责计数，超过上限时返回 `retryable=false`，停止继续执行并交还控制权，见 `xai-rate-limiter`。

写操作默认不自动重试。例如，两个 `create_ticket` 如果没有幂等控制，就可能创建两张工单。幂等键用于识别同一请求，使重复执行不会再次写入，见 `xai-tool-use`。

xAI 内置搜索的单次超时由服务侧处理，应用仍需限制整个任务的总时间。语音场景中，无上限的长搜索可能让用户长时间听不到回复，见 `xai-realtime`。

## 结果截断后，模型和日志要能对得上

工具结果应作为不可信数据处理。过长内容可以截到 $N$ 个字符或 $M$ 个 token，但要带上 `truncated=true`、原始字节数和内容哈希。

如果日志保存全文，而模型只看到了前 2k 内容，排查错误时就可能误以为模型见过关键证据。应明确记录模型实际看到的版本。网页结果还需要检查提示注入，见 `xai-search-agent`。

错误状态可以使用 `timeout`、`empty`、`denied` 和 `retryable` 等字段。执行是否成功以实际系统状态为准，不能把超时或模糊回复当成成功。

## 缓存和评测也需要跟上

工具定义和系统说明可以组成稳定的公共前缀。字段顺序应稳定，变化的网页结果放在公共前缀之后，避免破坏前缀缓存，见 `xai-prompt-cache`。

评测不仅看任务完成，还要统计工具选择、参数合法性、误调用、重复写入，以及失败后是否编造成功。截断后是否仍有证据支持结论，也要单独检查。每条轨迹记录步数和总耗时。

权限检查仍要执行，不能为 Agent 提供绕过鉴权的管理员工具。

## 多任务和持久运行时也适用

原始公开材料描述 Grok Build workflows 会保存进度，使暂停后继续时不用重做已完成的子任务。每个子任务仍需要超时和写操作规则。公开帖给出的并行规模是默认 128 个 Agent、大任务 1,024 个，并在最终报告前做独立检查。

Grok Bot 可以在笔记本关闭后继续工作，同账户的 Bots 共享计算机环境。因此，虚拟机上的凭据需要按账户内 Bots 都可能访问来管理。产品背景见 `xai-spacexai-now`。

## 面试追问

- **并行调用中只有一个超时怎么办？** 返回已完成调用的结果，并给失败调用返回对应错误。每个结果都要匹配调用 ID，不能漏掉一个。
- **模型一直调用同一个失败工具怎么办？** 统计失败次数，达到上限后设置 `retryable=false` 并停止。只写提示词劝它换方法不可靠。
- **代码输出特别长怎么办？** 截断并标记；需要完整文件时放入对象存储，返回可读取的 URI。
- **同时使用内置搜索和自有数据库呢？** 搜索在 xAI 侧执行，数据库在应用侧执行。分别管理超时、权限和结果格式。

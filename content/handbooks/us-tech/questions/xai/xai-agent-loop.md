---
id: xai-agent-loop
section: xai
order: 19
level: A
title: xAI：Grok tool loop 工程，超时、重试、观测截断？
quick: >-
  循环在宿主：每步超时、总轮数、总 token。只读可重试，写要幂等键否则不自动重试。工具 stdout 必须截断并留下「已截断」标记，否则你对着模型没看见的世界排障。不要靠
  prompt 写「请不要死循环」。
tags:
  - xAI
  - Tool Use
  - Agent Loop
  - Reliability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
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
---

## 题怎么来的

Grok 工具循环的公开层在 function calling 和内置搜索：模型出 `tool_call`，你执行或 xAI 执行，结果回对话。Grok-3 把 DeepSearch 写成会搜会跑代码的 agent，没有公布重试表。工程题是超时、重试、观测截断。底座合同见 `xai-tool-use`。`realInterview: false`。

## 三道硬顶

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

- 每步超时。搜索和代码解释器最容易挂。超时回 `retryable=true` 的短错误，不要把半页 HTML 塞回去。
- 总轮数 / 总 token。模型会反复搜同一个失败查询。宿主计数，超过就对模型说 `retryable=false`，把控制权交还用户。限流见 `xai-rate-limiter`。
- 写操作。默认不自动重试。并行两个 `create_ticket` 没有幂等就是两张单，见 `xai-tool-use`。

内置搜索的超时是 xAI 侧的；你仍要给整段循环一个墙钟，否则 DeepSearch 风格轨迹会在语音里变成长静音，见 `xai-realtime`。

## 观测必须显示截断

工具结果当不可信输入，进下一轮前截断到 $N$ 字符或 $M$ token。要留下标记：`truncated=true`、原始字节数、哈希。否则日志里是全文，模型看见的是前 2k，你无法复现幻觉。网页注入发生在未截断的尾巴里更常见，见 `xai-search-agent`。

回给模型的错误要短、结构化：`timeout` / `empty` / `denied` / `retryable`。禁止「好像成功了」。状态以系统记录为准。

Prompt cache：工具 schema 和系统说明是公共前缀，字段顺序要稳，见 `xai-prompt-cache`。每轮把不同的巨型网页粘在前缀前面，缓存全废。截断后的观测放在分叉之后。

评测：工具选对率、参数合法率、误调、写重复、失败后幻觉、截断后是否仍接地。只报任务完成会把「编造成功」算进正例。轨迹还要报步数和墙钟。

错法：靠 prompt 防循环；截断不打标；超时当成功；为 agent 开一条绕过鉴权的管理员工具。

## 追问

- **并行 tool_call 超时一个怎么办？** 已完成的结果照回；失败的回 error。缺一块 id 对话非法。
- **模型一直调同一个失败工具？** 计失败次数，超限 `retryable=false`。不要再靠「请换一种方法」写在 system 里。
- **代码解释器输出很长？** 先截断；需要文件就存对象存储只回 URI。别把整段 stdout 当下一轮 prompt。
- **和内置搜索混用？** 执行域不同：搜索在 xAI，数据库在你这边。超时和引用格式不要写成一条管道。

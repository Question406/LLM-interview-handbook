---
id: stepfun-react-io-blocks
section: agentrl
order: 121
level: S
title: 阶跃星辰：以 ReAct 为例，Plan / Action / Observation 的输入输出是什么？
quick: >-
  假设用户问订单到哪里了。模型自己看不到订单数据库，但可以输出一个结构化请求，例如选择查询订单的工具，并填入订单号。Function Calling
  解决的就是让模型表达这种动作。
tags:
  - StepFun
  - ReAct
  - Tool Use
  - Agent RL
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 阶跃星辰agent算法面经分享
    url: 'https://www.nowcoder.com/feed/main/detail/d01a17cf25344f4bb73eff2dbbaf6eee'
    type: candidate-first-hand
---

## 回答思路

> **问题与场景：** 假设用户问订单到哪里了。
>
> **做法与原因：** 真正调用 API 的是程序。
>
> **检查与取舍：** 所以我会把模型生成的动作与程序实际执行的动作分开检查。

## 可以这样回答

假设用户问订单到哪里了。模型自己看不到订单数据库，但可以输出一个结构化请求，例如选择查询订单的工具，并填入订单号。Function Calling 解决的就是让模型表达这种动作。

真正调用 API 的是程序。程序检查参数和用户权限，执行查询，再把查询结果放回模型上下文。模型随后才能根据这个结果回答，或决定是否还需要下一步操作。

所以我会把模型生成的动作与程序实际执行的动作分开检查。调用格式正确，不代表订单号存在，更不代表用户有权读取该订单。

## 技术备查

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：Agent 算法
- 届别 / 流程：原帖未披露
- 面试时间：原帖未披露；帖子发布于 2026-03-30
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“训练 agent 调用工具，以 react 框架为例，plan 是什么，提示怎么设计，Obersevation 是什么？Action 是什么？每一块的输入输出都是什么？长什么样的？”**

拿一次「调用搜索」来说：Plan 读入任务和已有轨迹，写出「需要官方文档里的 API 限制，准备搜索」这样的意图；Action 把它落成一条能被 parser 校验的搜索调用；Observation 是执行器返回的命中列表或错误，写回上下文给下一步用。原帖把 Observation 拼成了 Obersevation，这里按 ReAct 的 Thought / Action / Observation 来答。这题最怕空谈「模型自己想想」，阶跃要听的是每块的输入、输出和落盘的形状。

三块的契约我会这样讲：

| 块 | 输入 | 输出与形状 |
| --- | --- | --- |
| Plan（Thought） | 用户任务、已有轨迹、工具目录短描述、剩余步数 / 预算 | 下一步意图，自然语言或短 JSON；不必对用户可见 |
| Action | Plan + 工具 JSON schema | 可被 parser 校验的调用，如 `search(query="rate limit", k=5)`；单行 JSON / XML 标签，不写散文 |
| Observation | 执行器对 Action 的返回（命中列表、错误码、超时） | 写回上下文的文本或结构化摘要，带来源 ID，如 `{"ok": true, "results": [...], "error": null}` |

每块还有各自的约束。Plan 的提示里要禁止编造还没观察到的事实，可以让它声明终止条件。Action 的非法字段在 harness 层直接失败，别靠模型「差不多」对就放过去，对照 `agent-schema-contract`。Observation 超长就抽字段、留句柄；空结果、超时、权限失败必须分得清，不然模型会学坏，见 `arl-retry`。

三块串起来，Plan 决定意图，Action 落地成一次环境转移，Observation 成为下一步的 $s_{t+1}$。每条轨迹按 Plan / Action / Observation / 环境版本落盘：SFT 模仿合法转移；RL 只在可执行环境里给分，Plan 的文笔不单独奖励；Action 失败时 Observation 带上错误类型，训练才学得会 recovery；评测回放时用同一个 schema 重跑，不让模型重新「讲故事」。没有固定的记录字段，就难以用合法转移做 SFT，也没法回放 RL 轨迹。training feedback loop 见同一场面试的 `stepfun-agent-tool-training`。和 `byte-react-tool-select` 比，这题更抠 I/O 的形状，路由策略是那题的重点。

## 追问

**Plan 一定要输出吗？**
不一定，可以隐式地融进 Action。但训练和调试的时候，需要能分开看「想干什么」和「调了什么」。

**Observation 做摘要会不会丢证据？**
会。摘要要留能回源的 ID 或句柄，需要时再拉全文。只留散文摘要，hallucination 率会涨。

**多个工具并行调用怎么记？**
每个 Action 还是一条结构化调用；并行就是多条 Action 对应多条 Observation，按 ID 对齐，别合成一段糊在一起的文本。

**和普通 chatbot 的 function calling 有什么区别？**
多了必须写回的 Observation 和环境转移。没有写回，就算不上 ReAct 轨迹。

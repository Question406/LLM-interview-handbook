---
id: stepfun-react-io-blocks
section: agentrl
order: 121
level: S
title: 阶跃星辰：以 ReAct 为例，Plan / Action / Observation 的输入输出是什么？
quick: "Plan 读任务、历史轨迹和预算，输出下一步意图；Action 按工具 schema 输出一条能被 parser 校验的结构化调用；Observation 是执行后的原始结果或带来源 ID 的摘要，写回上下文供下一步使用。日志里三块分字段记录，才能拿来训练和回放。"
tags:
  - StepFun
  - ReAct
  - Tool Use
  - Agent RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阶跃星辰agent算法面经分享
    url: https://www.nowcoder.com/feed/main/detail/d01a17cf25344f4bb73eff2dbbaf6eee
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：Agent 算法
- 届别 / 流程：原帖未披露
- 面试时间：原帖未披露；帖子发布于 2026-03-30
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“训练agent调用工具，以react框架为例，plan是什么，提示怎么设计，Obersevation是什么？Action是什么？每一块的输入输出都是什么？长什么样的？”**

拿一次「调用搜索」来说：Plan 读入任务和已有轨迹，写出「需要官方文档里的 API 限制，准备搜索」这样的意图；Action 把它落成一条能被 parser 校验的搜索调用；Observation 是执行器返回的命中列表或错误，写回上下文给下一步用。原帖把 Observation 拼成了 Obersevation，这里按 ReAct 的 Thought / Action / Observation 来答。这题最怕空谈「模型自己想想」，阶跃要听的是每块的输入、输出和落盘的形状。

三块的契约我会这样讲：

| 块 | 输入 | 输出与形状 |
| --- | --- | --- |
| Plan（Thought） | 用户任务、已有轨迹、工具目录短描述、剩余步数 / 预算 | 下一步意图，自然语言或短 JSON；不必对用户可见 |
| Action | Plan + 工具 JSON schema | 可被 parser 校验的调用，如 `search(query="rate limit", k=5)`；单行 JSON / XML 标签，不写散文 |
| Observation | 执行器对 Action 的返回（命中列表、错误码、超时） | 写回上下文的文本或结构化摘要，带来源 ID，如 `{"ok": true, "results": [...], "error": null}` |

每块还有各自的约束。Plan 的提示里要禁止编造还没观察到的事实，可以让它声明终止条件。Action 的非法字段在 harness 层直接失败，别靠模型「差不多」对就放过去，对照 `agent-schema-contract`。Observation 超长就抽字段、留句柄；空结果、超时、权限失败必须分得清，不然模型会学坏，见 `arl-retry`。

三块串起来，Plan 决定意图，Action 落地成一次环境转移，Observation 成为下一步的 $s_{t+1}$。每条轨迹按 Plan / Action / Observation / 环境版本落盘：SFT 模仿合法转移；RL 只在可执行环境里给分，Plan 的文笔不单独奖励；Action 失败时 Observation 带上错误类型，训练才学得会 recovery；评测回放时用同一个 schema 重跑，不让模型重新「讲故事」。没有固定的记录字段，就难以用合法转移做 监督微调（SFT），也没法回放 强化学习（RL） 轨迹。训练闭环见同一场面试的 `stepfun-agent-tool-training`。和 `byte-react-tool-select` 比，这题更抠 I/O 的形状，路由策略是那题的重点。

## 追问

**Plan 一定要输出吗？**
不一定，可以隐式地融进 Action。但训练和调试的时候，需要能分开看「想干什么」和「调了什么」。

**Observation 做摘要会不会丢证据？**
会。摘要要留能回源的 ID 或句柄，需要时再拉全文。只留散文摘要，幻觉率会涨。

**多个工具并行调用怎么记？**
每个 Action 还是一条结构化调用；并行就是多条 Action 对应多条 Observation，按 ID 对齐，别合成一段糊在一起的文本。

**和普通 chatbot 的 function calling 有什么区别？**
多了必须写回的 Observation 和环境转移。没有写回，就算不上 ReAct 轨迹。

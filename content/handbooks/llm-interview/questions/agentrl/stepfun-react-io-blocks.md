---
id: stepfun-react-io-blocks
section: agentrl
order: 121
level: S
title: 阶跃星辰：以 ReAct 为例，Plan / Action / Observation 的输入输出是什么？
quick: >-
  Plan 吃任务与历史，输出下一步意图；Action 是对工具 schema 的结构化调用；Observation
  是环境返回的原始或摘要结果，必须写回上下文。三者要有固定日志字段，才能训练和回放。
tags:
  - StepFun
  - ReAct
  - Tool Use
  - Agent RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
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

原帖把 Observation 拼成了 Obersevation，按 ReAct 的 Thought / Action / Observation 答。这题最怕空谈「模型自己想想」。阶跃要听 **每块的输入、输出、落盘形状**。用一次「调用搜索」写具体。训练闭环见同面 `stepfun-agent-tool-training`。

## 三块的合同

**Plan（Thought）**  
- 输入：用户任务、已有轨迹、工具目录短描述、剩余步数 / 预算。  
- 输出：下一步意图，例如「需要官方文档里的 API 限制，准备搜索」。可以是自然语言或短 JSON。  
- Prompt 约束：禁止编造尚未观察到的事实；可以声明终止条件。Plan 不必对用户可见。

**Action**  
- 输入：Plan + 工具 JSON schema。  
- 输出：可被 parser 校验的调用，如 `search(query="rate limit", k=5)`。  
- 形状：单行 JSON / XML 标签，不是散文。非法字段应在 harness 层失败，不要靠模型「差不多」。对照 `agent-schema-contract`。

**Observation**  
- 输入：执行器对 Action 的返回（命中列表、错误码、超时）。  
- 输出：写回上下文的文本或结构化摘要，带来源 ID；超长则抽字段、留句柄。  
- 形状：`{"ok": true, "results": [...], "error": null}`。必须区分空结果、超时、权限失败，否则模型会学坏，见 `arl-retry`。

三者串起来：Plan 决定意图，Action 落地为环境转移，Observation 成为下一步的 $s_{t+1}$。缺固定字段就无法 SFT 合法转移，也无法 RL 回放。

## 训练与回放只认这些字段

每条轨迹按 Plan / Action / Observation / 环境版本落盘。SFT 模仿合法转移；RL 只在可执行环境给分，Plan 不单独奖文笔。Action 失败时 Observation 必须带错误类型，训练才能学 recovery。评测回放时用同一 schema 重跑，而不是让模型重新「讲故事」。和 `byte-react-tool-select` 比，本题更抠 I/O 形状，而不是路由策略。

面试收口：Plan 吃任务与历史、输出意图；Action 是合法 schema 调用；Observation 是环境回包并写回上下文。没有固定日志字段，就没有可训练的 Agent。

## 追问

- **Plan 一定要输出吗？** 不是。可以隐式融进 Action。但训练和调试需要能分开看「想干什么」和「调了什么」。
- **Observation 摘要会丢证据？** 会。摘要必须留可回源的 ID / 句柄，需要时再拉全文。只留散文摘要，幻觉率会涨。
- **多工具并行怎么记？** 每个 Action 仍是一条结构化调用；并行则多条 Action 对应多条 Observation，按 ID 对齐，不要合成一段糊文本。
- **和普通 chatbot function calling？** 多了必须写回的 Observation 和环境转移。没有写回，就不是 ReAct 轨迹。

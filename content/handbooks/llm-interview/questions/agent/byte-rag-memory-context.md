---
id: byte-rag-memory-context
section: agent
order: 205
level: A
title: 字节实习一面：RAG、Memory、Context Engineering 各解决什么，Coding Agent 里怎么配合？
quick: >-
  RAG 挂外部只读知识；Memory 存跨任务状态与偏好；Context Engineering
  决定当前窗口放什么。Coding Agent 里仓库检索是 RAG，已确认约束是 Memory，当前 diff
  与测试日志是精心挑选的上下文，三者不要合成一个向量库。
tags:
  - ByteDance
  - RAG
  - Memory
  - Context Engineering
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 字节实习 agent开发一面
    url: https://www.nowcoder.com/feed/main/detail/075c06bf50a143a785c039f9951624f6
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：Agent 开发实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“你怎么看 RAG、Memory 和 Context Engineering？这三者分别解决什么问题？在你的 Coding Agent 里是怎么配合的？”**

陷阱是把三者塞进同一个向量库，或者把对话摘要既当检索证据又当长期事实。RAG、Memory、Context Engineering 解决的问题不同：外部只读知识、跨任务可写状态、当前窗口的预算与选择。混用后污染无法归因——是索引脏、记忆写错，还是窗口塞错了。概念对照也可看 `meituan-memory-vs-rag`；Agent 与 RAG 的原理差见 `jd-agent-vs-rag`。

## 三者分别解决什么

**RAG**：按需取仓库或文档里的只读证据，降低「参数里背代码」造成的过时和幻觉。Coding Agent 里主要是符号检索、`grep`、文件切片，而不是先把整仓 embed 再聊。

**Memory**：存跨任务仍应成立的状态与偏好——仓库规范、用户确认过的约束、已验证结论。它可写、必须带来源和失效条件，见 `byte-short-long-memory`。对话过程吐槽不是 Memory。

**Context Engineering**：在有限窗口里决定放什么：当前失败测试、相关文件切片、规格、刚拿到的工具观察。它不生产新知识，只做选择、排序、压缩与隔离。压缩策略见 `byte-three-level-compress`。

一句话：RAG 回答「去哪读」，Memory 回答「什么必须记住」，Context 回答「这一步窗口里放得下什么」。

## Coding Agent 里怎么配合

改代码前用 RAG / grep 找符号和调用点；Memory 注入「这个仓库禁止改生成目录」这类已确认约束；Context 只塞当前失败测试、相关文件切片和规格，不把整个 `git log` 塞进去。短记忆（本轮 diff、失败用例）走工作区，不要写成长期向量。

顺序通常是：权限与任务目标 → 检索相关代码 → 把命中切片和硬约束装进窗口 → 改 → 跑测试 → 观察进短记忆。长记忆只在检索命中或任务类型匹配时注入，避免每次都把用户偏好清单顶满窗口。

## 混用的病和评测怎么拆

典型病：把对话摘要当 RAG 证据（摘要没有行号，无法跳转）；把检索到的 README 当长期记忆（文档改了摘要不过期）；把整个检索结果当 Context（噪声挤掉当前 diff）。污染纠错见 `byte-memory-pollution`。

评测必须分开：检索看命中率与证据 ID；Memory 看约束是否在后续任务仍被遵守、过期是否失效；Context 看窗口 token、硬约束是否还在、无关文件占比。合成一个「问答准确率」会把三种失败糊在一起。面试里主动说「我会分三条曲线看」，比强调用了向量库更像做过。

## 追问

- **仓库检索算 RAG 还是 Memory？** 按需读代码是 RAG；「上次确认禁止改生成目录」才是 Memory。读过一遍不等于记住。
- **为什么不能只用一个向量库？** 读写语义、失效策略、权限和评测都不同。合成之后无法单独回滚错误结论，也无法对检索做金标。
- **Context 和压缩是一回事吗？** 压缩是 Context Engineering 的手段之一；还要决定优先级、引用格式、是否保留句柄而不是全文。
- **和 Harness 什么关系？** 组装窗口、写入记忆、调用检索都是 Harness 的职责，模型只在给定上下文里选动作，见 `byte-harness-engineering`。

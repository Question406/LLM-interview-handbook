---
id: byte-rag-memory-context
section: agent
order: 205
level: A
title: 字节实习一面：RAG、Memory、Context Engineering 各解决什么，Coding Agent 里怎么配合？
quick: "检索增强生成（RAG）提供外部只读资料，Memory 保存跨任务的状态和偏好，Context Engineering 决定当前窗口放什么。Coding Agent 用 RAG 检索仓库，用 Memory 注入已确认的约束，再挑当前相关的 diff 和测试日志放进窗口。三者要分开管理、分开评测。"
tags:
  - ByteDance
  - RAG
  - Memory
  - Context Engineering
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
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

三者管的东西不一样。检索增强生成（RAG）提供外部的只读资料，回答「去哪读」；Memory 保存跨任务仍然成立的可写状态和偏好，回答「什么必须记住」；Context Engineering 管当前窗口的预算和选择，回答「这一步窗口里放得下什么」。Coding Agent 里用 RAG / grep 找代码，用 Memory 注入已确认的约束，再挑当前相关的 diff、失败测试和规格放进窗口。三者要分开存、分开评；塞进同一个向量库，或者把对话摘要既当检索证据又当长期事实，出了问题就分不清是索引脏、记忆写错，还是窗口塞错了。

分开说一下。RAG 按需从仓库或文档里取只读证据，减少「参数里背代码」带来的过时和幻觉；在 Coding Agent 里主要是符号检索、`grep`、文件切片，用不着先把整仓 embed 再聊。Memory 存跨任务仍该成立的状态和偏好，比如仓库规范、用户确认过的约束、已验证的结论；它可写，必须带来源和失效条件，见 `byte-short-long-memory`，对话过程里的吐槽不算 Memory。Context Engineering 在有限窗口里决定放什么，当前失败的测试、相关文件切片、规格、刚拿到的工具观察；它不生产新知识，只做选择、排序、压缩和隔离，压缩策略见 `byte-three-level-compress`。概念对照也可以看 `meituan-memory-vs-rag`，Agent 与 RAG 的原理差别见 `jd-agent-vs-rag`。

举个例子，修一个失败的测试。顺序通常是先确认权限和任务目标，用 RAG / grep 找到相关符号和调用点；Memory 注入「这个仓库禁止改生成目录」这类已确认的约束；Context 里只放当前失败的测试、相关文件切片和规格，整个 `git log` 不塞进去。然后改代码、跑测试，观察结果进短记忆。本轮的 diff、失败用例这类短记忆走工作区，别写成长期向量。长记忆只在检索命中或者任务类型匹配时注入，免得每次都被用户偏好清单把窗口顶满。

混用会出几种典型问题：把对话摘要当 RAG 证据，摘要没有行号，没法跳转；把检索到的 README 当长期记忆，文档改了，摘要却不过期；把检索结果整个当 Context，噪声挤掉了当前 diff。污染纠错见 `byte-memory-pollution`。所以评测也要分开：检索看命中率和证据 ID；Memory 看约束在后续任务里是否还被遵守、过期了有没有失效；Context 看窗口的 token 用量、硬约束有没有保留、无关文件占比多少。合成一个「问答准确率」，三种失败就糊在一起了，定位不到失败发生在哪一步。

## 追问

**仓库检索算 RAG 还是 Memory？**
按需读代码是 RAG，「上次确认禁止改生成目录」才是 Memory。读过一遍不等于记住了。

**只用一个向量库为什么不行？**
读写语义、失效策略、权限和评测都不一样。合在一起之后，没法单独回滚错误结论，也没法给检索做金标。

**Context 和压缩是一回事吗？**
压缩只是 Context Engineering 的手段之一，它还要决定优先级、引用格式，以及要不要只保留句柄、不放全文。

**和 Harness 什么关系？**
组装窗口、写入记忆、调用检索都是 Harness 的职责，模型只在给定的上下文里选动作，见 `byte-harness-engineering`。

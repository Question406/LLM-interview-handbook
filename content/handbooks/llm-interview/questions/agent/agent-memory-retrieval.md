---
id: agent-memory-retrieval
section: agent
order: 12
level: A
title: Memory Retrieval 怎么评估？
quick: >-
  除了 Recall@K，还要测是否召回了不该用的记忆、召回后任务是否改善，以及错误或过期记忆是否导致失败。评测要分别检查
  记忆写入和记忆读取。
tags:
  - Memory
  - Eval
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: LoCoMo — Evaluating Very Long-Term Conversational Memory of LLM Agents
    url: https://arxiv.org/abs/2402.17753
    type: primary
---

常见误区是：把 Memory 当成普通 检索增强生成（RAG），只报 Recall@$K$。Memory 至少有 write policy、storage/compaction、retrieval、usage 四步；评测必须拆开读写，并问「召回了不该召的」会不会伤任务。LoCoMo 把长对话记忆评成跨会话事实一致性，不是单轮检索命中。分类与冲突处理见 `agent-memory`。

## 拆成 read / write 两个子问题

Write：该不该写入、字段是否带 timestamp / source / confidence / scope、冲突如何 supersede、敏感字段是否脱敏。一次错误写入会污染后续所有会话。Read：该不该召回、top-$k$ 是否含正确条目、过期 / 冲突 / distractor 是否被滤掉、注入上下文后下游任务是否变好。

构造五类任务：需要 memory 的（上次偏好、已确认约束）、不需要 memory 的 distractor、互相冲突的条目、已过期事实、敏感 / 权限外条目。金融或客服场景还要测「记了什么、谁能看」。分层存储与查询路由见 `ant-long-memory-retrieve`。

## 指标不要只看 Recall@$K$

同时报：retrieval recall / precision；downstream success delta（有无 memory 的任务差）；false-memory harm（错误或过期条目导致的失败、违规、错误承诺）；freshness accuracy；额外 token 开销；privacy violation rate。Recall 很高但总把无关历史塞进 context 的系统可能更差：挤掉当前指令、引入过期制度、把网页里的「新系统指令」当记忆。污染与注入路径见 `byte-memory-pollution`、`agent-prompt-injection`。

## 评测协议

固定模型与 harness，只改 memory 模块。时间切分：写入发生在 $t_0$，查询在 $t_1$，中间插入冲突更新或用户更正。Poisoning：把 tool / RAG 输出里的指令写入后，新会话是否执行高风险动作。还要测 compaction：摘要是否丢掉关键约束、是否把低置信推断写成事实。没有 write 评测的 retrieval 数字，不能说明系统可上线。

评测结果应分别说明是否写入了合适的记忆、是否召回了合适的条目，以及这些条目对任务结果的影响。Recall@$K$ 只反映读取环节的一部分；无关历史和过期事实即使命中，也可能干扰当前任务。

## 追问

- **和 RAG 评测差在哪？** RAG 评外部文档是否召回；Memory 还评 Agent 自己写进去的条目是否该存在、是否过期、会不会跨会话伤任务。
- **$K$ 很大 recall 就好看？** 会。必须配 precision、token overhead 和下游 delta；只优化 recall 等于鼓励把整本历史塞进窗口。
- **用户更正了旧偏好怎么办？** 旧条目应失效而不是并列召回让模型猜。评测集里要有 explicit correction 后再问同一偏好。
- **摘要压缩算 write 还是 read？** 算 write 的副作用。压缩后要回归：关键约束还在、敏感字段没泄漏、错误推断没被写实。

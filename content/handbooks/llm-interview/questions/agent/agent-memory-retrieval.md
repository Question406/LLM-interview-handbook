---
id: agent-memory-retrieval
section: agent
order: 12
level: A
title: Memory Retrieval 怎么评估？
quick: "要把记忆写入和读取分开评，Recall@K 只覆盖读取的一部分。还要测召回了不该用的记忆会不会伤任务、有无 memory 时任务成功率差多少，以及错误或过期的记忆造成了多少失败。"
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

评估 Memory Retrieval 要把写入和读取拆开测，Recall@$K$ 只覆盖读取里的一小块。还要看召回了不该召的条目会不会伤任务、有 memory 和没有 memory 的任务成功率差多少、错误或过期的记忆造成了多少失败。

Memory 和普通的检索增强生成（RAG）差在条目是 Agent 自己写进去的，至少要经过 write policy、storage/compaction、retrieval、usage 四步。比如用户几个月前说「报销走旧系统」，后来换了系统，这条记忆没失效。检索时它稳稳命中，Recall 很好看，Agent 却照着过期的制度答错了。LoCoMo 也把长对话记忆评成跨会话的事实一致性，单轮检索命中不是它看的东西。分类和冲突处理见 `agent-memory`。

所以我会拆成 read 和 write 两个子问题。Write 看该不该写入、字段里有没有 timestamp / source / confidence / scope、冲突怎么 supersede、敏感字段有没有脱敏，一次错误写入会污染后面所有会话。Read 看该不该召回、top-$k$ 里有没有正确条目、过期 / 冲突 / distractor 有没有被滤掉、注入上下文之后下游任务有没有变好。

评测集构造五类任务：需要 memory 的（上次的偏好、已确认的约束）、不需要 memory 的 distractor、互相冲突的条目、已过期的事实、敏感或权限外的条目。金融或客服场景还要测记了什么、谁能看到。分层存储和查询路由见 `ant-long-memory-retrieve`。

指标一起报：retrieval recall / precision；downstream success delta，也就是有无 memory 的任务差；false-memory harm，错误或过期条目导致的失败、违规、错误承诺；freshness accuracy；额外的 token 开销；privacy violation rate。一个 Recall 很高、却总把无关历史塞进 context 的系统可能更差：它会挤掉当前指令、引入过期制度，甚至把网页里的「新系统指令」当成记忆。污染和注入的路径见 `byte-memory-pollution`、`agent-prompt-injection`。

协议上，固定模型和 harness，只改 memory 模块。按时间切分：写入发生在 $t_0$，查询在 $t_1$，中间插入冲突更新或用户更正。做 poisoning 测试：把 tool / RAG 输出里的指令写进记忆，看新会话会不会执行高风险动作。还要测 compaction：摘要有没有丢掉关键约束、有没有把低置信的推断写成事实。最后报结果时分别说清楚三件事：写入的记忆合不合适，召回的条目合不合适，这些条目对任务结果有什么影响。没有 write 评测的 retrieval 数字，说明不了系统可以上线。

## 追问

**和 RAG 评测差在哪？**
RAG 评外部文档有没有召回；Memory 还要评 Agent 自己写进去的条目该不该存在、过没过期、会不会跨会话伤任务。

**$K$ 开得很大，recall 是不是就好看了？**
会。所以必须配上 precision、token overhead 和下游 delta。只优化 recall，等于鼓励把整本历史塞进窗口。

**用户更正了旧偏好怎么办？**
旧条目要失效，别和新条目并列召回让模型去猜。评测集里要有 explicit correction 之后再问同一偏好的用例。

**摘要压缩算 write 还是 read？**
算 write 的副作用。压缩后要回归三件事：关键约束还在，敏感字段没泄漏，错误推断没被写成事实。

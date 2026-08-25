---
id: ant-long-memory-retrieve
section: agent
order: 140
level: A
title: 蚂蚁：Agent 长期记忆如何存，历史很大时怎么查？
quick: >-
  热数据放会话 state，冷数据按用户或任务做成可检索记忆条目，带时间和权限。量大时用分层索引、摘要和过期，别把全文历史每次塞进
  prompt。查询要按意图路由，不能只靠向量相似度。
tags:
  - Ant Group
  - Memory
  - Agent
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁大模型一面（被问懵版）
    url: https://www.nowcoder.com/feed/main/detail/1a1a229b1d9f4a5bbfcb6ea6c9857339
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“你是怎么设计agent的记忆系统？”**；**“长期记忆如何存储？如果历史记录量非常大，怎么优化查询效率？”**

原帖连问设计和大规模查询。这块容易直接答成「上了 LangChain Memory」或「全量 embedding 每次 top-k」。蚂蚁场景还要审计「记了什么、谁能看」。分类见 `agent-memory`，检索评估见 `agent-memory-retrieval`，短长分工见 `byte-short-long-memory`。

## 先分层，再谈存储

工作记忆是当前轨迹的 state：计划、工具句柄、未决槽位，生命周期等于本任务。情景记忆是跨会话事实与偏好，写入前抽取、确认、脱敏。程序记忆是 Skill / SOP，走版本库而不是聊天日志。条目应有 `user_id`、task_type、时间、权限、置信度、失效策略。全文对话只作原始附件，检索对象是结构化摘要。Memory 不是 RAG：RAG 取外部文档，Memory 是 Agent 自己沉淀且带 provenance 的状态，见 `meituan-memory-vs-rag`。

## 历史极大时怎么查

按时间分区 + 向量 / 倒排混合召回；先用意图或规则缩候选（本任务类型、近 $N$ 天、当前租户），再对 top-$k$  rerank。超长会话先滚动摘要，摘要失败则回源附件。不要把全文历史每次塞进 prompt。查询路由不能只靠向量：身份证号、订单号走倒排；「上次那个理财偏好」走语义加时间衰减。金融权限在召回前过滤，避免无权记忆进窗口。评测看正确记忆召回、错误记忆污染率和 p95 查询延迟。

写入要配额和冲突处理：用户更正优先于旧推断；过期制度随生效日期失效。污染修复见 `byte-memory-pollution`。大规模查询的工程细节：热层用会话 state 和最近摘要，温层按用户/任务倒排，冷层对象存储挂原始附件；p95 超时则降级为「只查热层 + 请用户确认」，而不是扫完全部历史。向量索引按时间分区，避免每次全库 ANN。分层存储、结构化条目、混合召回、权限先行；全文历史不是检索对象。

## 追问

- **为什么不每次塞全文？** 窗口被挤掉当前指令，过期事实被当成约束，成本随历史线性涨。分层检索是为了可控召回，不是为了「记得更多」。
- **摘要会不会丢关键约束？** 会。关键约束应结构化存储并在 compaction 后回归，见 `agent-memory-retrieval`。
- **向量检索不够吗？** 不够。ID / 错误码 / 精确偏好需要倒排；权限和时间必须当硬过滤。
- **谁有权读这条记忆？** 按用户与租户 ACL，tool 写入的内容默认不可升权。审计记写入者、来源和读取会话。

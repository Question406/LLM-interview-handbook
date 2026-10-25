---
id: p3a-openai-chatgpt-enterprise-rag
section: openai
order: 637
level: A
title: "OpenAI：企业 ChatGPT：内部数据接入与权限检索"
quick: "企业 RAG 要让权限贯穿接入、检索、缓存和引用展开，先过滤员工能看的证据，再生成带引用的答案。比如删除文档后先写 tombstone 立即隐藏，再异步清索引；更新与删除时限、ACL 泄漏和证据支持率要分别验证。"
companies:
  - openai
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · chatgpt-enterprise-rag"
    url: https://www.1point3acres.com/interview/problems/company/openai/chatgpt-enterprise-rag
    type: secondary
---

我会把文档权限和版本一路带到检索与引用展开，再让模型根据有权访问的证据回答。比如员工问「今年差旅报销标准是多少」，系统先确定租户和 ACL 组，召回有权限的片段，答案带引用，展开原文时再校验一次权限。

这道题按一千家企业、每家一百万篇文档设计，更新后一小时内可检索，删除后十分钟内不能出现在回答里。开始时要确认 ACL 来自哪个系统、变化多频繁。连接器先拉取文档，解析和切块时记录来源、版本和血缘，再写入带 ACL 的向量与关键词索引。查询时混合检索、精排，取前几段作为生成证据。租户边界在检索前和引用展开时分别检查。

数据里保留 document、version、chunk、`acl_group`，同步进度放在 `connector_cursor`，索引标记 `index_version`。答案绑定使用的 chunk 版本，ACL 变更带事件序号，缓存 key 也包含租户与权限版本，这样更新能沿着同一版本关系传播。

删除先写 tombstone 立即让文档不可见，再异步清理 blob 和向量，索引有延迟时也不能继续泄漏。检索文本始终当作数据，文档里的指令不能扩大工具权限。评测分别看 ACL 泄漏必须为 0、recall@k、证据支持率、拒答准确性、更新延迟和 P95 回答时延；每家企业都要有一份小而高质量的 gold set，避免平均分掩盖问题。

## 追问

**权限组特别多怎么办？**
按租户分区，检索时做文档过滤，返回前再做后置授权检查。热点 ACL 集合可缓存，但要按版本失效。若等生成后才屏蔽，模型已经看过无权限内容，隔离就太晚了。

**员工刚被移出某个组，十分钟内还能查到旧文档吗？**
不应该。ACL 事件序号推进权限版本，旧缓存随版本失效，检索读取最新组关系，引用展开的检查再补一层。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

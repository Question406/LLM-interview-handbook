---
id: ali-skill-memory-rag
section: agent
order: 21
level: S
title: 淘天面经：Skill、Memory、RAG 分别解决什么核心问题？
quick: >-
  Skill 存一类任务的操作方法，Memory 存跨会话状态和用户偏好，RAG
  检索当前问题需要的外部证据。三者的更新、权限和评测方式都不同，混进同一个向量库就分不清了。
tags:
  - Alibaba
  - Skill
  - Memory
  - RAG
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---

Skill 解决「这类任务怎么做」的程序化经验复用，Memory 解决跨会话的状态和个性化，检索增强生成（RAG）解决「此刻需要哪条外部证据」。淘天这题追问的重点是 division of responsibilities：把操作手册放进 RAG 不等于有了 Skill，把所有历史塞进窗口也不等于有了 Memory 治理。

| 组件 | 核心问题 | 典型实现 |
| --- | --- | --- |
| Skill | How to do this class of tasks? | 流程 + 模板 + 脚本 + 工具规范，按需加载 |
| Memory | What should persist across turns / sessions? | 短窗口、摘要、画像、带来源记录的事件 |
| RAG | What evidence do I need now? | 检索知识库 / 文档并引用 |

具体说，Skill 是可加载的操作步骤，比如退货需要哪些字段、先查询什么、什么时候转人工，它可以是一份 markdown 说明书加校验脚本，别把它当成又一段 embedding。Memory 是用户和会话的状态，地址、偏好、未完成订单，要有实体键和遗忘机制。RAG 是当前问题的证据，政策条款、商品规格，要能引用、能过期。

混成一个向量库，失败会很具体：用户上周的地址和今年的退货政策被同一套相似度捞出来，模型随机引用一个。三者的变更方式也不一样，Skill 变更是发版，流程改了要回归；Memory 变更涉及写入冲突和 GDPR 式删除；RAG 变更是索引更新。权限也不同，Skill 决定能调哪些工具，Memory 按用户隔离，RAG 按文档 ACL 过滤。让一个「全公司向量库」同时承担这三样，审计和回滚都会乱。

两种常见的偷懒也会出问题。把操作手册塞进 RAG，模型照样可能不按步骤执行，procedure 要靠 Skill 或工作流强制，见 `ali-modular-agent-plan`。把所有历史塞进窗口，没有实体键和旧记录作废机制，下一轮还是会用旧地址，冲突写入见 `ali-memory-conflict`。

验收时分别造用例：换流程只改 Skill，用户更正只改 Memory，政策更新只改索引，三项同时变时才看端到端。评测也拆开，Skill 看步骤合法率，Memory 看更正后是否用了新值，RAG 看引用忠实度（评估细节见 `ali-rag-eval`），别只报一个「答得对」。

## 追问

**手册检索算 Skill 吗？**
不算。Skill 要约束步骤和工具，检索只提供文本。

**长 context 能替代 Memory 吗？**
不能。没有实体键、冲突检测和遗忘，窗口只是缓存。

**三者的调用顺序是什么？**
先路由 Skill，再取相关的 Memory 槽位，再按需做 RAG，不要每轮把三个库全扫一遍。

**MCP 算哪一层？**
协议层，管能力怎么连，本身不是 Skill、Memory 或 RAG，见 `ali-mcp-vs-fc`。

---
id: ali-skill-memory-rag
section: agent
order: 21
level: S
title: 淘天面经：Skill、Memory、RAG 分别解决什么核心问题？
quick: "Skill 保存一类任务的操作方法；Memory 保存跨会话状态与用户偏好；RAG 检索当前问题需要的外部证据。它们的更新、权限和评测方式不同，不能只放进同一个向量库就认为已经实现。"
tags:
  - Alibaba
  - Skill
  - Memory
  - RAG
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---

常见误区是：把三者塞进同一个向量库，或把操作手册检索叫 Skill、把历史全文拼接叫 Memory。Skill 解决「这类任务怎么做」的程序化经验复用；Memory 解决跨会话状态与个性化；检索增强生成（RAG） 解决「此刻需要哪条外部证据」。淘天追问重点是边界：手册进 RAG ≠ 有 Skill；所有历史进窗口 ≠ 有 Memory 治理。冲突写入见 `ali-memory-conflict`，RAG 评估见 `ali-rag-eval`，工具连接见 `ali-mcp-vs-fc`。

## 三个组件解决三个问题

| 组件 | 核心问题 | 典型实现 |
| --- | --- | --- |
| Skill | How to do this class of tasks? | 流程 + 模板 + 脚本 + 工具规范，按需加载 |
| Memory | What should persist across turns / sessions? | 短窗口、摘要、画像、带来源记录的事件 |
| RAG | What evidence do I need now? | 检索知识库 / 文档并引用 |

Skill 是可加载的操作步骤：退货需要哪些字段、先查询什么、何时转人工。它可以是 markdown 说明书 + 校验脚本，别当成又一段 embedding。Memory 是用户与会话的状态：地址、偏好、未完成订单，要有实体键和遗忘。RAG 是当前问题的证据：政策条款、商品规格，要可引用、可过期。

## 不要混成一个向量库

混库的失败很具体：用户上周的地址和今年的退货政策被同一套相似度捞出来，模型随机引用。Skill 变更是发版（流程改了要回归）；Memory 变更是写入冲突与 GDPR 式删除；RAG 变更是索引更新。权限也不同：Skill 决定能调哪些工具，Memory 按用户隔离，RAG 按文档 ACL 过滤。用一个「全公司向量库」承担三职，审计和回滚都会乱。

把操作手册塞进 RAG，模型仍可能不按步骤执行。procedure 要 Skill 或工作流强制，见 `ali-modular-agent-plan`。把所有历史塞进窗口，没有实体键和旧记录作废机制，下一轮仍会用旧地址。

## 边界怎么验收

分别造用例：换流程只改 Skill、用户更正只改 Memory、政策更新只改索引。三项同时变时才看端到端。评测拆开：Skill 看步骤合法率，Memory 看更正后是否用新值，RAG 看引用忠实度。别只报一个「答得对」。

## 追问

- **手册检索算 Skill 吗？** 不算。Skill 要约束步骤与工具，检索只提供文本。
- **长 context 能替代 Memory 吗？** 不能。缺实体键、冲突检测和遗忘，窗口只是缓存。
- **三者调用顺序？** 先路由 Skill，再取相关 Memory 槽位，再按需 RAG；不要每轮三库全扫。
- **MCP 算哪一层？** 协议层，管能力怎么连，不是 Skill / Memory / RAG 本身。

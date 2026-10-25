---
id: p3a-microsoft-chatbot-personalization-memory-design
section: microsoft
order: 611
level: A
title: "Microsoft AI / Copilot：MAI Chatbot 记忆：存储、检索和冲突"
quick: "长期记忆区分用户明确事实、模型推断偏好和会话临时信息，每条保留来源、置信度、有效时间与版本。读取只在当前用户范围内召回，冲突先核对时间或确认，删除同步清理向量、摘要与缓存，避免旧信息再次出现。"
companies:
  - microsoft
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - Microsoft AI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Microsoft AI / Copilot · chatbot-personalization-memory-design"
    url: https://www.1point3acres.com/interview/problems/company/microsoft/chatbot-personalization-memory-design
    type: secondary
---

我会把长期记忆存成带来源、有效时间和版本的记录，检索时先按当前用户过滤，再选与本轮问题相关的记忆。用户明确说「我对花生过敏」与模型推断「似乎喜欢简短回答」，可信度和保留方式不同，临时会话内容也应单独处理。

题目是为个性化聊天助手设计记忆，让它不用每轮重读全部历史，也能记住偏好与经历，支持查看、纠正、删除和跨设备一致。练习规模是十万用户、每人最多一千条记忆。

> 来源：一亩三分地 Microsoft 题卡摘要（2026-10-18 读取），属于网站对候选人报告的二手整理，没有逐条核对原帖，网站收录也不代表公司官方确认；规模数字、SLO 和故障情景是手册补的练习约定。

## 从一次写入讲清记忆怎样更新

先澄清哪些敏感内容要用户同意、删除多久生效，以及候选记忆能否自动写入。对话事件先进入日志，提取器产生候选，校验置信度并查冲突后，才写版本化 memory store。用户明确声明优先于模型推断；新对话在用户范围内召回，再压缩成短上下文。

一条记录可记为 memory(id, user, type, value, source, confidence, `valid_from`, `valid_to`, version, deleted)。原始证据与提炼结论分开保存，便于追溯，短期上下文和长期事实采用不同保留期。

例如用户说「我下个月搬去西雅图」，候选记忆写明事件、来源对话 id、高置信度，以及 `valid_from` 为下个月。已有「住在纽约」时，保留历史并设对应 `valid_to`，新记录版本加一，用户 memory version 也增加。两周后另一设备问「周末去哪玩」，按当前日期核对生效时间：如果已到新记忆的 `valid_from`，才用西雅图；尚未生效则不能提前当成已经搬家。

## 冲突与删除都要更新派生数据

新记忆碰到高置信旧事实时，先确认语境或给两条记录明确时间范围，不能无依据覆盖。「我以前是 X」要保留原句与有效期，检索按问题时间选择，仅用 embedding 难以区分与「我现在是 X」的差异。

删除要传播到 memory store 的 deleted 状态、向量索引与派生摘要；摘要重新生成，旧缓存依据 user memory version 失效。这样用户删掉事实后，不会又从另一个缓存或设备读回来。

验证既看记忆精确率、更新及时性和错误纠正率，也看跨用户泄漏次数、多轮一致性与个性化收益。加入无需记忆即可完成的任务，防止助手过度个性化。

## 追问

**怎样确认删除真的生效？**
同时核对主存、向量条目和摘要，删除后立刻问一个仅凭该记忆才能回答的问题，检查输出不再包含它。

**新旧信息冲突一定覆盖吗？**
不一定。明确时间变化的记录按有效期并存，含糊冲突先向用户确认，来源与置信度作为判断依据。

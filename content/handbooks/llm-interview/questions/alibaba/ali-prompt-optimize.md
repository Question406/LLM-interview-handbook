---
id: ali-prompt-optimize
section: alibaba
order: 19
level: B
title: Prompt 自动推荐/压缩可用哪些策略？
quick: 模板分层、示例检索、embedding 聚类选示范、摘要压缩、关键槽位结构化；效果要用任务指标验证，不只看更短。
tags:
  - Alibaba
  - Prompt
  - Context
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

错法：原文越短越好。Prompt 自动推荐 / 压缩是按意图选模板、按相似度选示范、按预算压上下文。效果必须用任务指标验证（成功率、拒答率、引用正确率、槽位完整率），不能只看 token 变少。单意图短指令、模板已经稳定时，上自动压缩收益很小，还可能丢掉槽位。工具集裁剪与延迟的关系见 `ali-latency-3tools`，记忆分层见 `ali-skill-memory-rag`。

## 推荐是选模板，不是随机 few-shot

按意图路由到短模板：退货、物流、闲聊各用一份，别塞一份万能长 system。用 embedding 检索相似成功 case 作 few-shot；聚类选示范时要卡意图，避免把投诉话术示范塞进咨询单。示范要带正确工具轨迹，不要只贴最终回复。工具说明做裁剪，只暴露当前任务相关 tools。五十个 schema 全塞进去，既贵又诱导误调，见 `agent-tool-routing`。

推荐系统本身要版本化：模板、示范库、路由阈值变更都要可回滚。否则「自动」变成线上漂移，出了问题说不清是模型还是 prompt 库。

## 压缩要保住槽位

长历史走摘要 + 结构化 state，避免全文拼接。订单号、地址、售后条款、用户更正是不可压缩槽位，必须结构化留下，不能丢进摘要模型碰运气。近详远略：最近两轮保留原文，更早的只留事件。压缩把槽位摘要没了，后面轮次幻觉补订单号，比多花 200 token 更贵。Memory 的实体键与摘要分工见 `ali-memory-conflict`。

## 怎么验收

对照压缩前后的任务成功率、槽位完整率、错误工具率、p95 TTFT，别只报平均 prompt 长度。设金标槽位集，压缩后做 exact match。聚类选出的 few-shot 与当前意图不一致，模型会抄错口径。要在离线集上测「示范意图 = 当前意图」的命中。压缩比设上限：到预算再压，不要每轮都压到最短。

## 追问

- **摘要模型会不会再幻觉？** 会。所以槽位不走摘要，只压叙述性上下文，并抽检槽位完整率。
- **few-shot 越多越好吗？** 不是。过长会挤掉当前证据，且示范冲突时模型摇摆。按相似度取 2-4 条通常够。
- **和 RAG 是一回事吗？** 不是。RAG 取外部证据，prompt 压缩管的是对话与工具说明。见 `ali-rag-eval`。
- **如何证明更短且不掉点？** A/B 看成功率和槽位完整率，长度只作约束不是目标。

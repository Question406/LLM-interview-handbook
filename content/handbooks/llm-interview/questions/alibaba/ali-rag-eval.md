---
id: ali-rag-eval
section: alibaba
order: 14
level: S
title: RAG 如何提升生成质量？怎样评估一个 RAG 是否 work？
quick: 用检索证据约束生成，降低过时与幻觉。评估要拆开：检索（召回/精确/nDCG）、生成（忠实度/引用正确率）、端到端任务成功率，并做失败归因。
tags:
  - Alibaba
  - RAG
  - Eval
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

错法：只报端到端「答得像」，或把 RAG 说成换 embedding 就能消幻觉。RAG 用检索证据约束生成，降低过时与幻觉；生成器要在证据上综合，无证据则拒答。评估必须拆开检索、生成、端到端，并做失败归因。知识过期快、必须可引用时，RAG 比继续 SFT 更合适；常识闲聊上 RAG 只增加延迟。和微调怎么选见 `fund-rag-ft`，和 Skill / Memory 别混库见 `ali-skill-memory-rag`。

## RAG 约束的是证据

相对裸生成，外部知识以证据形式注入上下文。与传统检索 + 模板不同，生成器仍要综合多段、处理冲突、决定拒答。提升质量的杠杆在切分、混合检索、rerank、权限过滤，别只指望更大生成模型。切分过碎会拆散表格，过长会引入噪声。没有金标文档时，不要假装能算 Recall@$k$，改用人评忠实度和任务成功。

## 评估必须拆三层

1. 检索：Recall@$k$、Hit、nDCG、路由正确率；
2. 生成：faithfulness、引用可追溯、拒答率；
3. 业务：任务成功、满意度、延迟与成本。

用户问「这款耳机是否支持无线充电」。检索应命中规格说明书对应段；生成必须引用该段并忠实复述。检索到营销软文、生成写成「支持」，要分开标：检索错还是生成幻觉。淘天追问常落到切分、混合检索、rerank，以及这条归因。无证据必须拒答的用例要单独集，否则模型靠参数「蒙对」会把指标抬虚。

## 失败归因再改哪一层

只报端到端时，检索全错模型仍能编对，分数虚高。归因顺序：路由是否进对库 → 金标段是否进 top-$k$ → 生成是否引用且不添造 → 业务是否完成。坏在检索就改切分 / 召回 / rerank；坏在生成就改引用约束与拒答 SFT，别上来换更大的 embedding。文档更新后不重训仍应对，这是 RAG 相对微调的验收点。

## 追问

- **怎么证明 RAG work？** 给检索切片和忠实度，加上「无证据必须拒答」的用例，不要只看 BLEU。
- **检索对了仍幻觉？** 加强引用约束、把证据放前、对无引用输出惩罚；必要时 SFT「带证据回答」。
- **和 Memory 差在哪？** RAG 是当前问题的外部证据；Memory 是跨会话的用户状态。见 `ali-memory-conflict`。
- **没有金标怎么办？** 用人评忠实度、引用可点击率、任务成功，不要伪造 Recall。

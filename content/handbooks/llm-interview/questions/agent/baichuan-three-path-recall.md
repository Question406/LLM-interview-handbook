---
id: baichuan-three-path-recall
section: agent
order: 126
level: A
title: 百川智能：三路召回如何做？
quick: >-
  三路通常分别用关键词匹配、稠密向量和业务规则或结构化字段检索。各路先召回并检查权限，再合并候选、融合排序。用验证集调权重或训练轻量
  rerank，并根据 query 类型决定启用哪些检索方式。
tags:
  - Baichuan
  - Retrieval
  - Hybrid Search
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面 压力好大
    url: https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530
    type: candidate-first-hand
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“三路召回如何做的”**

常见误区是：背「BM25 + 向量 + 再加一路」就结束。三路互相补充，减少单一检索方式漏掉相关结果的情况；融合前要权限过滤，权重按 query 类型动，低置信才开满。两路混合见 `ant-bm25-hybrid`，改写见 `baichuan-query-rewrite-model-choice`，ES vs 向量见 `byte-es-to-vector`。

## 三路各自补什么

1. **稀疏路**（倒排 / BM25 / 学习稀疏）：稳专有名词、ID、错误码。
2. **稠密路**（embedding ANN）：抓同义改写和语义相近文档。
3. **结构化 / 规则路**：类目、时间、权限、表格主键或运营置顶。

案例库或检索增强生成（RAG）场景里，第三路也可以是高质量 few-shot 案例库的精确检索，与文档库分开索引，避免案例和知识互相污染。每路先独立取 top-$k$，做权限与过期过滤，再进入统一候选池。不要三路分数直接相加，量纲不同。

## 融合与动态开关

融合可以是 RRF、加权分或小模型 rerank。权重按 query 类型变：导航 / ID 偏稀疏，开放问句偏稠密，带明确过滤条件走结构化。不要每次开满：明确 ID 可以短路只走倒排；低置信或多跳再开齐。评估看分层 recall@$k$、下游任务成功和延迟。导入侧仍要切块、版本、ACL，否则三路只是把脏数据召得更全。

Query 改写是前段，不是第四路索引：改写后仍应保留原 query 走稀疏，防止 drift。

## 追问

- **第三路一定是规则吗？** 不一定。可以是知识图谱、案例库或运营置顶。它补的是稀疏/稠密都弱的信号。
- **RRF 和学权重怎么选？** 冷启动 RRF 稳；有标注后再学 query 分类器输出权重。固定 1:1:1 通常不是最优。
- **三路延迟怎么控？** 并行召回 + 短路。p95 超预算时先砍稠密 ANN 的 $k$，而不是砍权限过滤。
- **和 rerank 的关系？** 召回负责不漏，rerank 负责精排。精确 ID 没进池，rerank 救不回来。

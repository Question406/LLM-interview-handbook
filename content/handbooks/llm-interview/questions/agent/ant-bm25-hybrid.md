---
id: ant-bm25-hybrid
section: agent
order: 182
level: A
title: 蚂蚁：BM25 原理是什么，混合召回怎么接 RAG？
quick: >-
  BM25 是带文档长度归一的词项匹配分，稳专有名词和 ID。混合召回把 BM25 与稠密向量候选合并去重再
  rerank。金融知识库导入要切块、权限和版本，而不是只丢 embedding。
tags:
  - Ant Group
  - BM25
  - Hybrid Retrieval
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 蚂蚁大模型面经
    url: https://www.nowcoder.com/feed/main/detail/2b27dfe1f1ab4efa87eb0aea70ffdc20
    type: candidate-first-hand
  - title: 【面经】5月20日，蚂蚁智能体与大模型应用 一面
    url: https://www.nowcoder.com/discuss/888874988554448896
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型 / 智能体应用
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“讲一下BM25算法原理”**；**“讲讲RAG的混合召回”**

蚂蚁这题常连着问：先能写 BM25，再接到金融知识库的混合召回。别把 BM25 说成「就是 TF-IDF」，也别把混合说成「两个分数加起来」。专有名词、合同编号、错误码在金融场景比语义近邻更致命。三路召回见 `baichuan-three-path-recall`，权重动态化见 `jd-hybrid-retrieval-weight`。

## BM25 在算什么

对查询词 $q$，BM25 累加 IDF 与饱和的词频，并用文档长度相对平均长度做惩罚。直觉：稀有词权重大；同一词重复出现的收益递减（$k_1$ 控制饱和）；长文档不该只因为更长就更高分（$b$ 控制长度归一）。它不理解同义，所以「还款日 / 账单日」可能对不上，但「合同编号 / 错误码」比向量稳。面试若追公式，写清三项即可：IDF、饱和 TF、长度归一；不必默写所有变体。

## 混合召回怎么接 RAG

稀疏 top-$n$ + 稠密 top-$n$ → 统一候选池去重 → **权限与生效日期过滤** → 交叉编码器或 LLM rerank → 截断进上下文。权重按 query 类型动：短精确词、ID、错误码偏 BM25；长口语、同义改写偏稠密。融合可用 RRF，避免两路分数量纲不同硬加。导入知识库时记录来源、生效日期和 ACL，避免过期制度被召回当事实。从 ES 切到纯向量会丢的能力见 `byte-es-to-vector`。

金融 RAG 的失败往往在导入而不在模型：切块切断条款编号、没带租户权限、制度已废止仍在索引。混合召回救不了脏索引。评测按 query 类型切片报 Recall@$k$ 和下游答对，并单列「必须命中的关键词」集。蚂蚁场景里，混合召回还要能回答「这条制度现在是否有效、当前用户是否可读」——这不是 rerank 的事，是元数据。切块时保留条款号和标题路径，BM25 才有东西可打。面试收口：BM25 负责精确词与长度归一；向量负责同义；融合前进 ACL 与时效；权重随 query 类型动。

## 追问

- **为什么不固定 1:1 加权？** 导航型 query 会被语义近邻噪声挤掉精确命中。用验证集按类型扫，或先做 query 分类再加权。
- **BM25 对同义词没办法？** 可以在 query 侧改写或同义表扩召，但扩召要受控，否则召回噪声爆炸。改写模型选择见 `baichuan-query-rewrite-model-choice`。
- **只 rerank 不混合行不行？** rerank 只能在候选池里挑。精确 ID 若没进池，rerank 救不回来。
- **权限过滤放哪？** 融合前。先召后滤会把无权文档的分数泄漏进排序，也浪费配额。

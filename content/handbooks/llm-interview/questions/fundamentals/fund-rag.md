---
id: fund-rag
section: fundamentals
order: 13
level: A
title: BM25、Dense Retrieval、Cross-Encoder Reranker 如何组合？
quick: >-
  BM25 擅长 exact lexical match；dense retrieval 擅长语义 paraphrase；工业常做 hybrid
  recall，再用更昂贵 cross-encoder 同时编码 query+document 做精排。
tags:
  - RAG
  - Retrieval
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Dense Passage Retrieval for Open-Domain Question Answering
    url: https://arxiv.org/abs/2004.04906
    type: primary
  - title: Passage Re-ranking with BERT
    url: https://arxiv.org/abs/1901.04085
    type: secondary
---

错法：三选一站队，或让 cross-encoder 扫全库。工业默认是 hybrid 召回 + 贵模型精排：BM25 保专有名词 / ID / 原文片段，dense 保同义改写，cross-encoder 只看几十到几百候选。切块见 `fund-chunking`，ANN 索引见 `fund-ann`，融合权重见 `ant-bm25-hybrid`、`jd-hybrid-retrieval-weight`。最终质量要拆 retrieval recall 与 answer faithfulness；检索对了生成仍可胡编。要不要微调生成模型见 `fund-rag-ft`。

## 三路各自算什么

BM25 是词项匹配 + 文档长度归一，对稀有精确串强，对 paraphrase 弱。Dense / bi-encoder：query 与文档分开编码，文档向量可预计算，用内积 / 余弦 + ANN 从百万级取 top-$K$，擅长语义相近但字面不同。Cross-encoder：每个 query-doc 对联合进 Transformer，token 级 attention，准确但无法预计算文档侧，复杂度随候选数线性涨，所以只 rerank 召回集。DPR 把双塔检索做成可训练的召回器；BERT rerank 把交叉注意力放在精排。

## 为什么是级联而不是单一模型

第一阶段要从百万文档快速取 top-$K$，必须能预计算或倒排。第二阶段 $O(K)$ 次昂贵 forward 换精度。Hybrid 避免专有名词被 dense miss，也补上 BM25 对同义句的漏召。融合可以是分数加权、RRF 或学一个浅层学习器；权重随 query 类型变（ID 查询偏 BM25，口语偏 dense）。评测拆 Recall@$k$（召回是否含证据）与生成忠实度，不要用一个端到端分数掩盖上游。

失败模式：只用 dense 导致订单号 / 错误码检索失败；cross-encoder 直接打全库导致延迟爆炸；chunk 切坏使 BM25 和 dense 同时看不到完整证据（先修 `fund-chunking`）。

## 级联怎么评、权重怎么扫

评测必须拆开：召回用 Recall@$k$ / nDCG（金标是证据文档），精排用更小 $k$ 上的 nDCG，生成用忠实度与任务成功。端到端一个分数会把「检索挂了」和「生成胡编」混在一起。Hybrid 起步可用 RRF 或固定加权，再按 query 类型扫：含 ID / 错误码 / 专有名词的偏 BM25，口语改写偏 dense。学权重需要有标注的 query-doc，见 `ant-bm25-hybrid`、`jd-hybrid-retrieval-weight`。ANN 索引（`fund-ann`）只加速 dense 第一阶段，不改变「三路如何组合」的逻辑。

Rerank 的 $K$ 由延迟预算反推：cross-encoder 一次 forward 的成本乘 $K$ 必须落在 SLA 内，所以常见 $K\in[20,100]$ 而不是 $K=1000$。$K$ 太小，正确证据根本进不了精排；$K$ 太大，噪声文档和延迟一起涨。Chunk 边界错误时三路一起盲，先修切块重叠再谈融合。生成侧是否微调是另一题（`fund-rag-ft`）：检索没到证据，微调生成也补不回事实。

口令：lexical 保命、dense 保义、cross 保序、生成受证据约束。复杂度和准确度怎么换要说清楚，别站队「BERT 更强所以全程 BERT」。

## 追问

- **为什么不把 cross-encoder 当召回？** 无法为每个 query 扫全库；没有独立文档向量可索引。
- **Hybrid 一定要学权重吗？** 起步 RRF / 固定加权即可；有标注再按 query 类型扫，见 `ant-bm25-hybrid`。
- **召回高为什么答案仍错？** 生成未受证据约束，或 rerank 把对的证据挤出窗口。要拆指标。
- **BM25 对中文怎么用？** 先分词或用字 / n-gram 倒排；原则仍是稀疏词项匹配，和 dense 互补不变。
- **只做 dense 行不行？** 小语料、全是同义改写时可以试；线上有订单号、报错码、人名时几乎必须 hybrid。

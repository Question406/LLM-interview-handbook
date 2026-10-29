---
id: amazon-rerank-llm
section: amazon
order: 19
level: A
title: Amazon：LLM rerank 和 embedding 召回怎么叠？
quick: >-
  先用 embedding / BM25 召回，再用交叉编码器或 Bedrock Rerank 缩小候选；指令复杂时，才让 LLM 比较前十几条。每层分别测
  Recall、nDCG 和最终答案的证据支持，候选漏了先修召回。
tags:
  - Amazon
  - Rerank
  - RAG
  - Embeddings
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: >-
      Improve the relevance of query responses with a reranker model in Amazon
      Bedrock
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html'
    type: primary
  - title: Supported Regions and models for reranking in Amazon Bedrock
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-supported.html'
    type: primary
  - title: Amazon Titan Text Embeddings models
    url: >-
      https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html
    type: primary
  - title: Hybrid search with Amazon OpenSearch Service
    url: >-
      https://aws.amazon.com/blogs/big-data/hybrid-search-with-amazon-opensearch-service/
    type: secondary
---

## 可以这样回答

我会先用低成本检索保住召回，再逐层精排，LLM 只处理最后的一小组候选。比如条款在 embedding 第 12 名，直接取 top-5 生成就会漏；先扩大候选再精排才有机会找回来。

Bedrock 提供 Rerank API，以及 Knowledge Bases 的 rerankingConfiguration，公开模型包括 Amazon Rerank 1.0、Cohere Rerank 3.5 一类交叉编码器。LLM rerank 是可选的额外阶段，底层召回仍由 `amazon-titan-embed`、`amazon-kendra-hybrid` 中的模型负责。

## 技术备查

我会先用低成本检索保住召回，再逐层精排，LLM 只处理最后的一小组候选。比如条款在 embedding 第 12 名，直接取 top-5 生成就会漏；先扩大候选再精排才有机会找回来。

Bedrock 提供 Rerank API，以及 Knowledge Bases 的 rerankingConfiguration，公开模型包括 Amazon Rerank 1.0、Cohere Rerank 3.5 一类交叉编码器。LLM rerank 是可选的额外阶段，底层召回仍由 `amazon-titan-embed`、`amazon-kendra-hybrid` 中的模型负责。

## 候选逐层缩小

记 query 为 $q$，语料为 $\mathcal{D}$。先把 BM25 和 embedding ANN 候选合并，取 $k$，常见为 50 到 100。编号和条款号靠词法，同义表达靠向量。两路分数用 RRF 或分别归一再融合，见 `amazon-kendra-hybrid`。这一层允许混入不相关文档，主要避免漏召回。

接着，交叉编码器对 $(q, d_i)$ 逐对判断相关性，收缩到 $n$，例如 10 到 20。它同时看 query 和文档，与双塔点积不同。Bedrock 文档提到，rerank 可以减少送给生成模型的块，降低成本和延迟。索引仍用 Titan 或所选 embedding 建立，rerank 模型不用于建库。

如果指令特别细，或要辨别「不适用于危险品」这样的否定条件，再让 LLM 对这 $n$ 条做列表比较，挑出真正回答问题的三条。对 $k=1000$ 跑 Converse 会消耗大量 token 并拖高 p99，见 `amazon-p99-stream`。候选规模应满足：

$$
|\mathrm{LLM\ candidates}|\ll |\mathrm{rerank\ in}|\ll |\mathrm{recall}|.
$$

直接让 Nova 对每条打 1 到 10 分，相关性分数往往难 calibration，成本和稳定性也需要验证。交叉编码器本身就是为相关评分训练的，可先作为稳定基线。

## 接生成前，检查质量和预算

生成只读取精排后的 $n$ 个短块，引用指回块 id，见 `amazon-bedrock-rag`。图 / PDF 先定 OCR 或视觉检索，再进入漏斗，见 `amazon-mm-rag`；避免文字检索之后又把整页 PNG 加进 LLM rerank。

评测分别报召回 Recall@$k$、精排 nDCG@$n$ 和条款准确率，以及最终答案的证据支持、任务成功，见 `amazon-titan-eval`。标识符 query 单独切片。精排更准但生成仍胡编，应用还不满足上线条件。

预算可以先按召回 50 到 100ms、rerank 50 到 150ms，生成占更大部分；新增 LLM rerank 后要单独统计 p99。Knowledge Bases 开启 rerank 会覆盖默认排序，要区分默认 ranker 和所选 rerank 模型。

换 embedding 要全库重编，换 rerank 只需重放查询，因此精排迭代成本较低。权限过滤仍放召回层，Guardrails 继续检查生成，不能补救召回了无权查看的文档，见 `amazon-guardrails`。

## 追问

**能跳过交叉编码器直接用 LLM 吗？**
可以尝试，但要验证成本和稳定性。交叉编码器适合便宜地缩小候选，LLM 再处理复杂指令与否定条件。

**$k$ 太小怎么补？**
先扩大 $k$ 或合并词法候选。没进入候选的文档，精排无法找回来。

**商品双塔和政策精排是一回事吗？**
目标不同。商品双塔见 `amazon-two-tower`；政策 RAG 更常用 query 与条款的交叉相关评分，不能直接混用点击模型。

**Rerank 1.0 和 Cohere 怎么选？**
先确认区域和模型支持表，再用自己的政策集测 nDCG。

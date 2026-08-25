---
id: amazon-rerank-llm
section: amazon
order: 19
level: A
title: Amazon：LLM rerank 和 embedding 召回怎么叠？
quick: >-
  先宽召回再窄精排。embedding / BM25 取 $k$，交叉编码器或 Bedrock Rerank 收到 $n$，必要时再用 LLM 只看前十几条。别让
  LLM 给一千条打分。评的是 nDCG 加端到端接地，不是 rerank 模型自己的公开榜。
tags:
  - Amazon
  - Rerank
  - RAG
  - Embeddings
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Improve the relevance of query responses with a reranker model in Amazon Bedrock
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html
    type: primary
  - title: Supported Regions and models for reranking in Amazon Bedrock
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-supported.html
    type: primary
  - title: Amazon Titan Text Embeddings models
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html
    type: primary
  - title: Hybrid search with Amazon OpenSearch Service
    url: https://aws.amazon.com/blogs/big-data/hybrid-search-with-amazon-opensearch-service/
    type: secondary
---

Seller 政策和商品问答把检索问成「向量不够再上大模型」。公开层 Bedrock 有 Rerank API 和 Knowledge Bases 里的 rerankingConfiguration；模型卡上是 Amazon Rerank 1.0 和 Cohere Rerank 3.5 一类交叉编码器。LLM 当 reranker 是你自己的第三段，不是默认托管。底座召回见 `amazon-titan-embed`、`amazon-kendra-hybrid`。不是逐字真题。

## 三层，不要一层吃到饱

记 query $q$，语料 $\mathcal{D}$。我会画三段：

1. **召回。** BM25 并上 embedding ANN，取 $k$（常见 50–100）。标识符、条款号走词法；同义走向量。分数空间不同，用 RRF 或各自归一后再融，见 `amazon-kendra-hybrid`。这一层要高召回，允许脏。
2. **交叉精排。** Bedrock Rerank / Cohere 对 $(q, d_i)$ 打相关分，收到 $n$（10–20）。它看的是 query–文档对，不是双塔点积。公开文档写：用 reranker 可以少塞一些块给生成，降成本和延迟。索引仍用 Titan 或你选的 embedding，**不要用 rerank 模型去建库**。
3. **LLM rerank（可选）。** 只对 $n$ 条做列表wise：「哪三条真正回答 $q$，其余丢掉」。适合指令细、要否定句（「不适用于危险品」）的政策题。不要对 $k=1000$ 跑 Converse。Token 和 p99 会爆，见 `amazon-p99-stream`。

不等式：

$$
|\mathrm{LLM\ candidates}|\ll |\mathrm{rerank\ in}|\ll |\mathrm{recall}|.
$$

错法：embedding top-5 直接生成，条款编号在第 12 名；反过来 LLM 给全库打分。另一错：rerank 用和生成同一个 Nova 聊天模型、prompt 还写「请打 1–10 分」——校准差、贵、不稳定。交叉编码器是为相关分训的。

## 和生成、评测怎么接

生成只看 rerank 后的 $n$ 条短块，引用必须能指回块 id，见 `amazon-bedrock-rag`。图 / PDF 先决定 OCR 还是视觉检索，再进同一套漏斗，见 `amazon-mm-rag`。不要文本召回完又把整页 PNG 塞进 LLM rerank。

评测拆开：

- 召回：Recall@$k$，标识符切片单独报。
- 精排：nDCG@$n$、条款级准确。
- 端到端：接地、任务成功，见 `amazon-titan-eval`。精排变好但生成胡编，不算发版。

延迟预算：召回 50–100ms，rerank 50–150ms，生成才是大头。LLM rerank 若上了，要进 p99 分桶。Knowledge Bases 里打开 rerank 会覆盖默认排序；面试说清「默认 ranker 和你选的 rerank 模型不是同一个东西」。

换 embedding 要全库重编；换 rerank 模型不用重编，只要重放查询。这是为什么精排是便宜的迭代旋钮。Guardrails 仍挂生成，不替代「检索到了不该看的文档」—— ACL 在召回过滤，见 `amazon-guardrails`。

## 追问

- **为什么不跳过交叉编码器、直接 LLM？** 交叉编码器便宜、稳定、为相关分训。LLM 擅长指令和否定，但贵。叠，不替换。
- **$k$ 太小怎么办？** 精排救不了召回。先加词法并集或扩 $k$，再谈 rerank。
- **和两塔精排？** 商品侧两塔见 `amazon-two-tower`。政策 RAG 更常交叉编码器。别把商品点击模型和条款相关分焊成一个。
- **Rerank 1.0 和 Cohere 怎么选？** 以当时区域和模型表为准。用你的政策集标定 nDCG，不要背公开 demo 分。

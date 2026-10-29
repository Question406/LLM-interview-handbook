---
id: amazon-kendra-hybrid
section: amazon
order: 5
level: A
title: Amazon：关键词 + 向量混合检索，何时 BM25 赢 embedding？
quick: >-
  精确编号、罕见专名和条款原文通常更适合 BM25；同义改写、意图和拼写变体更适合向量检索。先合并两路候选，再做分数归一或 RRF，最后精排；ASIN
  这样的标识符保留词法检索。
tags:
  - Amazon
  - Kendra
  - Hybrid Search
  - BM25
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Amazon Kendra
    url: 'https://aws.amazon.com/kendra/'
    type: primary
  - title: What is Amazon Kendra?
    url: 'https://docs.aws.amazon.com/kendra/latest/dg/what-is-kendra.html'
    type: primary
  - title: Hybrid search with Amazon OpenSearch Service
    url: >-
      https://aws.amazon.com/blogs/big-data/hybrid-search-with-amazon-opensearch-service/
    type: primary
  - title: Semantic product search
    url: 'https://www.amazon.science/publications/semantic-product-search'
    type: primary
---

## 可以这样回答

精确标识符、罕见专名和条款原文，BM25 往往比 embedding 可靠；同义改写和自然语言意图则更适合向量。比如搜 `WH-1000XM5` 时，用户要的是这个型号，语义上相近的「耳机」不能替代它。

BM25 使用词面匹配和 IDF。ASIN、SKU、订单号、工单 ID、CVE 编号、错误码 `AccessDeniedException`，以及内部包名、`Section 4.2.1` 这样的条款，都需要精确命中。Embedding 会把编号压到向量空间，近邻可能变成另一个编号；罕见型号也可能被常见类目吸走。极短的品牌词和精确类目导航同样适合保留词法路径，双塔对这类 query 本来就不稳。

## 技术备查

精确标识符、罕见专名和条款原文，BM25 往往比 embedding 可靠；同义改写和自然语言意图则更适合向量。比如搜 `WH-1000XM5` 时，用户要的是这个型号，语义上相近的「耳机」不能替代它。

BM25 使用词面匹配和 IDF。ASIN、SKU、订单号、工单 ID、CVE 编号、错误码 `AccessDeniedException`，以及内部包名、`Section 4.2.1` 这样的条款，都需要精确命中。Embedding 会把编号压到向量空间，近邻可能变成另一个编号；罕见型号也可能被常见类目吸走。极短的品牌词和精确类目导航同样适合保留词法路径，双塔对这类 query 本来就不稳。

法律政策原文、日志字段也有这个要求。Seller Support 搜「危险品锂电池」，语义相近的「电池运输」可能漏掉关键限定，见 `amazon-bedrock-rag`。反过来，`laptop for college student` 对应「轻薄学生本」，以及同义、上下位、形态、轻度拼写和跨语言表达，词面很难覆盖。Amazon Science 的 Semantic Product Search 讨论了这些词法不足；商品标题堆重复属性时，BM25 还可能抬高劣质标题。

## 先合并候选，再融合和精排

两路分别召回，再取并集，可以补上 ANN 漏掉的精确 ASIN，见 `amazon-two-tower`。BM25 和余弦分数不在同一量纲，直接 `0.5 * bm25 + 0.5 * cos` 容易让长文档或长尾 IDF 主导排序。OpenSearch 的 hybrid search 先取各路 top，再用 min-max / L2 归一，以及算术或几何平均融合。

也可以使用 RRF，只比较名次，避开分数 calibration：

$$
\mathrm{RRF}(d)=\sum_{r\in R}\frac{1}{k+\mathrm{rank}_r(d)}
$$

这里 $k$ 常取 $60$，适合融合 BM25 和 ANN。并集决定哪些文档有机会进入候选，融合决定两路候选谁排前，后面的精排再考虑相关性、新鲜度、库存和权限。Kendra Intelligent Ranking 则是词法取候选后用语义模型重排的路径。

```python
def rrf(rank_lists, k=60):
    scores = {}
    for ranks in rank_lists:
        for doc, r in ranks.items():
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + r)
    return sorted(scores, key=scores.get, reverse=True)
```

代码中的 `ranks` 是 doc 到 1-based 名次的映射。某一路没有召回的文档，不要用名次 0 冒充已经排过。

## 按 query 类型检查效果

权限、marketplace、元数据和新鲜度过滤要在两路同时生效。向量路滤了 marketplace、词法路漏滤，仍可能返回别国政策。

评测把标识符、头部商品、长尾自然语言和拼写错误分开看，再报 nDCG。标识符切片上纯向量表现差，可能就是匹配方式不适合。线上点击和购买还受 position bias 影响：BM25 已占第一屏，历史行为会继续支持它，新语义模型可能离线赢、线上输。冷启动商品尤其要检查这种偏差，见 `amazon-cold-start`。

Kendra 提供关键词加语义的托管能力，OpenSearch 则方便自行控制 BM25、k-NN、融合与过滤。这里引用的资料注明 Kendra 已不对新客户开放，因此新项目需要先确认可用服务，再按约束选实现。

## 追问

**为什么不统一成一个大 embedding？**
编号和条款的精确匹配仍需要词法路径。双塔与倒排负责召回，交叉模型适合精排，也无法对全库逐对交叉编码。

**Kendra 和 OpenSearch 怎么选？**
先确认新客户可用性。托管语义重排可考虑 Intelligent Ranking 一类服务；需要自控融合与过滤时，看 OpenSearch / Bedrock Knowledge Bases。

**RAG 也要 BM25 吗？**
要。政策编号、API 名和内部术语与商品 ASIN 一样，纯向量漏掉时生成端仍可能自信作答。

**可以学习融合权重吗？**
可以。先用 RRF 建基线，有行为数据后按 query 类型训练和验证，避免头部 query 主导权重。release criteria 见 `amazon-lp-ml`。

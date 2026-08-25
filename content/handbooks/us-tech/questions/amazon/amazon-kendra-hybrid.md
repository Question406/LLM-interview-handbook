---
id: amazon-kendra-hybrid
section: amazon
order: 5
level: A
title: Amazon：关键词 + 向量混合检索，何时 BM25 赢 embedding？
quick: >-
  精确标识符、罕见专名、条款编号、报错码、型号，倒排 / BM25 赢。同义改写、意图、拼写变体，向量赢。混合不是加权凑热闹：先并集保召回，再用分数归一或
  RRF，最后用行为或交叉模型精排。别把 ASIN 赌在近邻上。
tags:
  - Amazon
  - Kendra
  - Hybrid Search
  - BM25
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Amazon Kendra
    url: https://aws.amazon.com/kendra/
    type: primary
  - title: What is Amazon Kendra?
    url: https://docs.aws.amazon.com/kendra/latest/dg/what-is-kendra.html
    type: primary
  - title: Hybrid search with Amazon OpenSearch Service
    url: https://aws.amazon.com/blogs/big-data/hybrid-search-with-amazon-opensearch-service/
    type: primary
  - title: Semantic product search
    url: https://www.amazon.science/publications/semantic-product-search
    type: primary
---

企业搜索和商品搜索岗都会问混合检索。Kendra 的卖点是关键词加语义，不必自己调 BM25；OpenSearch 则把 BM25 子句和 k-NN 子句在管内做分数归一。Kendra 现已不对新客户开放，现场提一句、落到「倒排 + 向量 + 融合」即可，不要背服务名当答案。Amazon Science 的 Semantic Product Search 写过纯词法的三个洞：同义 / 上下位、形态、拼写。反过来说，词法赢的场景论文没当缺点写，面试要自己补上。

## BM25 什么时候赢

BM25 吃的是词面和 IDF。下面这些 query，向量经常把真正要的那条挤出 top-$k$：

- **标识符。** ASIN、SKU、订单号、工单 ID、CVE 编号、错误码 `AccessDeniedException`。Embedding 把长 ID 压成一个点，近邻是「看起来像编号的别的编号」。
- **罕见专名和型号。** `WH-1000XM5`、内部包名、条款 `Section 4.2.1`。IDF 极高，倒排一击即中；向量空间里被更常见的「耳机」「退货政策」吸走。
- **用户就要字面。** 法律条款、政策原文、日志字段名。Seller Support 里搜「危险品锂电池」，漏掉带这个短语的条款就是事故，语义近邻「电池运输」不够，见 `amazon-bedrock-rag`。
- **极短、高精 query。** 品牌词、类目精确导航。双塔对短 query 本来就不稳。

向量赢的是：`laptop for college student` 对「轻薄学生本」、同义、轻度拼写、跨语言、标题从未出现过的说法。Amazon 商品标题充满属性堆砌，纯 BM25 会把堆了更多重复词的劣质标题刷上去，这才需要语义。

错法是「全部上向量，词法是遗留」。电商里标识符流量占比不低，ANN 掉点补救的第一刀就是词法并集，见 `amazon-two-tower`。

## 怎么融，别在分数空间上硬加

BM25 和余弦不在一个量纲。直接 `0.5 * bm25 + 0.5 * cos` 会让长文档或长尾 IDF 主宰。OpenSearch 的做法是子查询分别取 top，再 min-max / L2 归一，用算术或几何平均。RRF 更糙也更稳：

$$
\mathrm{RRF}(d)=\sum_{r\in R}\frac{1}{k+\mathrm{rank}_r(d)}
$$

$k$ 常取 $60$。不依赖分数校准，适合 BM25 和 ANN 两路。Kendra Intelligent Ranking 是另一路：词法先取候选，语义模型重排。面试说清你处在哪一段：**召回并集**还是 **分数融合**还是 **重排**。三段职责不同。并集解决「向量漏掉精确 ASIN」；融合解决「两路都召到了谁排前」；重排解决「相关性还要叠加新鲜度、库存、权限」。

权限和元数据过滤必须在两路都生效。只在向量路上滤 marketplace、词法路漏滤，会检出别国政策。新鲜度同理。

评测按 query 切片，不要一个 nDCG 打天下：标识符集、头部商品 query、长尾自然语言、拼写错误。标识符集上向量单独会很难看，这不是模型没训好，是任务不该交给它。线上用点击 / 购买时记住位置偏差：BM25 占了第一屏，行为数据会自我强化，新语义模型离线赢、线上输。冷启动商品更吃这个偏差，见 `amazon-cold-start`。

```python
def rrf(rank_lists, k=60):
    scores = {}
    for ranks in rank_lists:
        for doc, r in ranks.items():
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + r)
    return sorted(scores, key=scores.get, reverse=True)
```

`ranks` 是 doc 到 1-based 名次。两路没有的文档不要塞 0 分进去冒充排过。

## 追问

- **为什么不把 query 和文档都塞进一个大 embedding 就够了？** 标识符和条款编号的碰撞空间太差；延迟上也不能对全库做交叉编码。双塔加倒排是召回，交叉是精排。
- **Kendra 和 OpenSearch 怎么选？** 新项目别默认 Kendra（已不对新客户开放）。要托管语义重排可以用 Intelligent Ranking 一类服务；要自己控融合和过滤，OpenSearch / Bedrock Knowledge Bases 更常见。选的是约束，不是品牌。
- **BM25 在 RAG 里还要吗？** 要。政策编号、API 名、内部术语和商品 ASIN 是同一类。只向量的 Knowledge Base 会在这些 query 上静默失败，生成看起来很自信。
- **两路分数能不能学一个融合权重？** 能，但要按 query 类型切片训，否则会被头 query 带跑。上线前先用 RRF 做无参基线，有行为数据再学权重，门禁见 `amazon-lp-ml`。

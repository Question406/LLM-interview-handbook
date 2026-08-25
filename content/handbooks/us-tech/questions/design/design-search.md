---
id: design-search
section: design
order: 5
level: S
title: 设计：语义搜索 + 关键词，混合与拼写纠错
quick: >-
  关键词保精确匹配和专有名词，向量保改写和同义。融合用 RRF 或学出来的加权，不要口头宣布语义取代 BM25。拼写纠错是带代价的：纠错专有名词比不纠更糟。指标看 nDCG、零结果率和 p95。
tags:
  - Search
  - Google
  - Microsoft
  - Retrieval
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Dense Passage Retrieval for Open-Domain QA
    url: https://arxiv.org/abs/2004.04906
    type: primary
  - title: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
    url: https://arxiv.org/abs/2005.11401
    type: primary
  - title: System Design in a Hurry
    url: https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction
    type: secondary
---

Google 搜索质量、Microsoft Bing、Amazon 商品搜、Apple Spotlight 都会问混合检索。DPR / RAG 论文证明 dense 能补上词汇鸿沟；生产里专有名词、货号、错误拼写和新鲜度会把纯向量打死。不是某次现场逐字题。若结果还要生成答案，契约升级为 `design-prod-rag`；这里先把「找对文档」讲完。

## 查询理解和双路检索

我会先问：语料（网页 / 商品 / 内搜）、流量、是否要拼写、多语言、新鲜度、p95。然后按查询走一条短管道，而不是一上来 embedding。

1. **理解。** 语言、导航型 vs 信息型、是否像货号 / URL / 人名。导航型查询（精确品牌、SKU）应偏关键词；「怎么把手机连上车」才偏语义。
2. **拼写。** 噪声信道：$\arg\max_{c} P(q \mid c) P(c)$，或编辑距离 + 查询语言模型。展示纠错条，让用户一键回到原查询。专有名词、小语种、新品牌的先验弱，$P(c)$ 会把对的打成错的。策略：高置信才自动改写，否则只提示；永远保留原查询一路召回。
3. **关键词。** BM25 / 倒排，短语、字段加权（标题 > 正文）、过滤（语言、时间、权限）。货号、错误码、函数名靠这一路。
4. **语义。** 双塔或 DPR 式，ANN 取 top-$k$。文档塔离线，查询塔在线。文档更新频率决定索引 SLO，和 RAG 一样向量不会自己过期。

融合：倒数排名融合

$$
\mathrm{RRF}(d) = \sum_{\mathrm{rank}} \frac{1}{\kappa + r_{\mathrm{rank}}(d)}
$$

$\kappa$ 常用 60，用标注集扫。有点击日志再学一层轻量 LTR，特征包括两路分数、字段命中、新鲜度、权威度。不要把 BM25 分数和余弦直接加，尺度不同。

## 新鲜度、权限、延迟

内搜和商品搜几乎都有 ACL 和上下架。过滤在检索时做，不要取回再丢，否则 p95 和泄漏都坏。新鲜度：新闻 / 库存用时间衰减或独立新内容索引；纯语义会把去年的爆款永远排在新文档前面。

延迟预算示例：纠错 10–20 ms，倒排 30–80 ms，ANN 20–50 ms，LTR 10–20 ms。两路并行。p95 看尾部：超长查询、冷索引、纠错候选爆炸。纠错候选要封顶。

失败模式：语义把反义词当近邻（「取消订阅」召回「订阅」）；纠错把 `Sequel` 改成 `SQL` 或把人名改成常见词；零结果时乱做同义扩张，用户以为系统蠢而不是「库里没有」；embedding 升级后新旧混排。权限存在性泄漏同 `design-prod-rag`。

纠错候选要封顶，否则 p95 死在这一跳：

```python
def spell_candidates(q, max_n=8):
    raw = edit_neighbors(q, dist=2)[:max_n]
    return [c for c in raw if lm_score(c) > thresh] or [q]
```

原查询永远保留一路。货号 / UUID 检测为导航型就关掉自动改写，只提示。

## 指标

离线：nDCG@$k$、MRR、拼写纠正准确 vs 误伤率（不该改而改）。切分按时间，点击有位置偏差，要用点击模型或随机流量当金标，不要把「点了第一条」当绝对相关。线上：零结果率、改写撤销率（用户点回原查询说明纠错过了）、p95、权限事故。商品搜还要看成交，不只点击——点得动但买不到是排序学了标题党。

人工抽查按查询类型分层：专有名词、错拼、长尾问句、敏感查询。敏感查询要接 `design-moderation`，不是检索分数越高越好。

零结果是产品信号：库里没有就说没有，并记 zero-result rate。用同义乱扩把无关文档填满，nDCG 可能还好看，用户会觉得搜索在撒谎。标题党商品用成交 / 退货护栏，不要只优化点击。

## 追问

- **为什么不关掉 BM25？** 货号、错误码、精确专名在子词 embedding 里会被打散。混合是约束，不是过渡方案。
- **纠错置信度怎么定？** 用日志里「展示纠错后用户是否撤销」当监督；阈值按误伤率护栏定，不要只追求纠错覆盖。
- **多语言一个索引？** 嵌入空间和分词都可能不齐。按语言分索引或带语言过滤更稳；混排要有评测证明。
- **和 RAG 的边界？** 搜索返回文档；RAG 多了生成和引用。检索层可以共用。

---
id: drustz-f889b0c6f4ca7d336e
section: mlsd
order: 35
level: A
title: >-
  06 · Search / Retrieval Post-training：Exa 类 AI Web Search ·
  十、Freshness、Serving 与成本
quick: >-
  作者文档章节 · 06 · Search / Retrieval Post-training：Exa 类 AI Web Search ·
  十、Freshness、Serving 与成本
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md
    type: primary
---
## 十、Freshness、Serving 与成本

### 10.1 Freshness 是一条独立数据链

```text
discovery (crawl/feed/sitemap)
  → fetch scheduling
  → parse + canonicalize
  → incremental lexical/vector indexing
  → cache invalidation
  → query-time temporal ranking
```



要定义：

- `discovery lag`：页面发布到发现。
- `fetch lag`：发现到成功抓取。
- `index lag`：抓取到可检索。
- `answer staleness`：用户查询时用了多久前的内容。

按 domain change rate 动态 recrawl；新闻、职位、金融页面比静态论文更频繁。支持删除/takedown 和 canonical version 替换。query classifier 判断 freshness intent，并把 `as_of` 传入 ranking/answer。

### 10.2 Cost-efficient serving cascade

```text
query cache / normalized query
  → cheap intent + lexical/dense ANN (top 1K)
  → lightweight reranker (top 100)
  → expensive cross-encoder (top 10–30)
  → fetch/extract only selected pages
  → answer model tier based on difficulty/confidence
```



优化旋钮：

- **ANN**：HNSW/IVF/PQ、binary quantization、Matryoshka/nested embeddings；报告 recall–latency–memory Pareto。
- **Precompute**：document embeddings 离线；增量 index 分 segment，后台 merge。
- **Dynamic top-k**：容易 navigational query 少取，multi-hop/low-confidence 扩展。
- **Early exit**：reranker confidence 足够就不调用大 cross-encoder。
- **Cache**：query/result/excerpt cache 带 index version 与 TTL；fresh query 不盲目复用。
- **Token budget**：返回 dense, query-specific excerpts，而不是整个页面。
- **Model routing**：rewrite/extract 用小模型，复杂 synthesis 才上 frontier model。
- **Parallelism**：独立 subqueries/fetch 并发，但设 per-host limit、deadline 和 global budget。

不要只给“量化、缓存、batching”三个词。面试里要说清它们影响的是哪段 latency、是否损失 recall、如何用 canary 验证。

### 10.3 Capacity 粗估模板

假设峰值 `Q` queries/s，每 query：

- candidate retrieval `K_0`；
- light rerank `K_1`；
- cross-encode `K_2` pairs；
- 平均 `S` 次 agent searches。

那么 cross-encoder pair throughput 约：

\[
TPS_{pair}=Q\cdot S\cdot K_2
\]

如果 `Q=1000`, `S=3`, `K_2=20`，就是 60K pairs/s；这会迫使你做 batching、small reranker、early exit 或降低 `K_2`，而不是简单部署一个最大模型。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/06_search_post_training.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md)。作者整理资料；许可和第三方来源范围见阅读指南。

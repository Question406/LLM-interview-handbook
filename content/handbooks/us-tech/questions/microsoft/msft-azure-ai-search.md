---
id: msft-azure-ai-search
section: microsoft
order: 15
level: A
title: Microsoft：Azure AI Search + 生成，混合检索、权限、引用
quick: >-
  LLM 产品岗别把 Azure AI Search 答成「一个向量库」。混合检索是 BM25 和向量并行，RRF 融合，可选语义排序器做 L2。过滤必须在证据进模型之前按用户身份裁。引用要绑可点击的文档键和跨度，不能事后编一个文件名。
tags:
  - Microsoft
  - Azure AI Search
  - Hybrid Retrieval
  - RAG
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Hybrid search overview in Azure AI Search
    url: https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview
    type: primary
  - title: Semantic ranking overview
    url: https://learn.microsoft.com/en-us/azure/search/semantic-search-overview
    type: primary
  - title: Document-level access control
    url: https://learn.microsoft.com/en-us/azure/search/search-document-level-access-overview
    type: primary
  - title: Retrieval-augmented generation in Azure AI Search
    url: https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview
    type: primary
---

## 题怎么来的

Azure / Copilot 产品岗问「搜索 + 生成」，要的是检索栈怎么给 LLM 供证据，不是 Lucene trivia。公开文档把混合查询写成：同一请求里关键词和向量并行，用 Reciprocal Rank Fusion（RRF）合并；语义排序器是可选 L2，模型来自 Bing 那路阅读理解，只重排 L1 的前约 50 条。权限有原生 Entra 授权令牌裁剪，也有自定义安全过滤字段。引用是生成契约，和 `msft-copilot-ground` 同一句：没进证据集的命题不能写。`realInterview: false`。

## 混合检索：L1 融合，L2 可选

纯向量会漏货号、人名、错误码；纯 BM25 会漏改写。Azure AI Search 的默认产品答案是 **两个都跑**。倒排和 ANN 各出一份有序列表，RRF 按名次调和，不把 BM25 分数和余弦相似度强行对齐：量纲不同，对齐是在骗人。

白板三层：

1. **L1 检索。** `search` 文本 + `vectorQueries`。过滤器（租户、时间、路径、ACL 字段）是全局的，必须进这次请求，不要检索后再在应用层丢文档。
2. **RRF 融合。** 多路（多向量字段、关键词、语义 cap）都走名次。文档自己的 `hybrid-search-ranking` 页写的就是这套。
3. **L2 语义排序。** 可选、计费。只看文本，把 L1 的前 50 条按问题意图重打 `@search.rerankerScore`（大约 0 到 4）。顺带出 caption / highlight，有时能抽短答案。它不是 L1：拿它扫全库又贵又慢。

生成侧只塞 top-k 短块，带 `id`、标题、caption。k 开到 40「显得召回好」会把 TPM 和 lost-in-the-middle 一起打爆，见 `msft-azure-tpm`、`msft-long-context`。很多仓库 / SharePoint 问题，8k 的混合检索短上下文，赢过 128k 全塞。

常见误区是：只 embed 不建倒排；用向量分数和 BM25 加权平均当融合；把语义排序器当「我们有 rerank 所以可以不滤 ACL」。

## 权限：进模型之前裁，不是生成后再检查

文档级访问控制两条公开路：

- **原生 token。** 索引里同步 ACL / RBAC / Purview 标签 / SharePoint 权限。查询带调用者的 Entra token（`x-ms-query-source-authorization`），服务在引擎内拼安全过滤。应用不用自己展开嵌套组。
- **安全过滤字段。** 自定义身份模型：索引里存 `group_ids`，查询时 `filter=group_ids/any(...)`。灵活，但组变更要重索引或可接受短暂脏读。

和 Copilot 同一条红线： **先滤再生成**。若先向量搜全库、模型已经看见不该看见的 token，再丢结果，日志和思维链都可能泄漏。索引可以按租户全量建，查询必须带身份；「搜完再滤」既慢又会在日志里留下越权命中。权限变更（移出频道、标签升级）要在检索路径生效；embedding 缓存可以留，**按用户缓存的命中列表不能跨用户复用**。

混合查询里，安全过滤是全局谓词。若对向量子查询写了 `filterOverride`，必须把 ACL 谓词再写进去，否则关键词路滤了、向量路没滤。这是产品事故，不是召回调参。

## 引用：可点击、可定位、与 ACL 一致

引用失败两种，分开放：

- **幻觉引用。** 句子在 $E$ 里没有，或绑到无关文档。生成 / 对齐问题。缓解：提示里只给检索块；每个断言绑 `document_key` + 段落 id；对不上就删句或改口「索引里没写」。
- **越权引用。** 内容对，但当前用户打不开。安全事故。UI 点击必须落到同一身份下的原文，不能用应用身份开一份「预览」。

语义 caption 适合做摘要高亮，**不能代替引用主键**。caption 是模型抽的句子，文档键和 chunk id 才是主键。行号当装饰，文本跨度才可核验。生成用约束解码把 doc id 限制在本次检索集合里，能压住乱写文件名，见 `msft-constrained-decode`。约束不管权限，权限仍在 L1。

评测拆开报：recall@k（用户可见的金标）、越权率（必须是 0）、引用可点击率、生成在证据外的命题率。只报「答案好看」会把编造引用算成正例。A/B 时多召回一篇用户可见的无关 wiki，不如少召回；多召回一篇用户不可见的设计文档，直接是事故。

## 追问

- **为什么不把全租户 embed 进一个大索引再在应用层滤？** 索引可以全量建，查询必须带身份。应用层滤意味着引擎已经打分、日志已经记下命中，模型侧若误塞一块就是泄漏窗口。
- **混合一定赢纯向量？** 公开基准和文档都说多数 检索增强生成（RAG） 场景混合加语义排序更稳。专名、错误码、SKU 靠关键词；改写、多语言靠向量。要按切片报，不要一个「检索分」。
- **引用了过期文档？** 按 item id 删旧块再写新块，回答带时间戳。向量不会自己过期，过期是元数据，不是 embedding 漂移。
- **和 M365 语义索引的差别？** Copilot 走 Graph + 语义索引，ACL 跟 M365 对象走。Azure AI Search 是你自己的索引和切片策略，ACL 要自己同步。产品故事能复用，索引实现不能画成同一个方块。

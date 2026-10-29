---
id: msft-azure-ai-search
section: microsoft
order: 15
level: A
title: Microsoft：Azure AI Search + 生成，混合检索、权限、引用
quick: >-
  Azure AI Search 让 BM25 与向量并行召回，用 RRF 融合，再可选语义排序器。查询按当前用户权限过滤，证据通过权限检查后才进
  LLM；生成论断绑定 document_key 和文本跨度，用户也必须能用同一身份打开引用。
tags:
  - Microsoft
  - Azure AI Search
  - Hybrid Retrieval
  - RAG
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Hybrid search overview in Azure AI Search
    url: 'https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview'
    type: primary
  - title: Semantic ranking overview
    url: 'https://learn.microsoft.com/en-us/azure/search/semantic-search-overview'
    type: primary
  - title: Document-level access control
    url: >-
      https://learn.microsoft.com/en-us/azure/search/search-document-level-access-overview
    type: primary
  - title: Retrieval-augmented generation in Azure AI Search
    url: >-
      https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview
    type: primary
---

本卡讨论公开方案，`realInterview: false`。Azure AI Search 可以先用 BM25 和向量并行召回，再用 RRF 融合，必要时做语义重排。接生成模型时，最关键的 checks 是 user permissions 和 citation locations。比如答案内容正确却引到用户打不开的设计文档，仍是越权事故。

## 先检索授权证据，再生成

关键词擅长货号、人名和错误码，向量擅长改写。`search` 与 `vectorQueries` 在同次请求中运行，租户、时间、路径和 ACL 过滤也进入请求。RRF 按名次合并多向量字段和关键词等结果，避免直接加权不同量纲的 BM25 与余弦分数，文档的 `hybrid-search-ranking` 页说明了这一路径。

可选 L2 语义排序器来自 Bing 阅读理解模型，只重排 L1 前约 50 条文本，返回约 0 到 4 的 `@search.rerankerScore`，还能提供 caption / highlight 或短答案。它需要额外计费，不适合扫描全库，也不会代替 ACL。

生成只读取 top-k 短块，附 `id`、标题、caption。把 k 加到 40 会增加 TPM 和 lost-in-the-middle，见 `msft-azure-tpm`、`msft-long-context`。例如许多仓库 / SharePoint 问题的 8k 混合短上下文可胜过 128k 全量输入。

文档权限可走两条路。原生方案在索引同步 ACL / RBAC / Purview 标签 / SharePoint 权限，请求带 Entra token（`x-ms-query-source-authorization`），由引擎裁剪，无需应用自己展开嵌套组。自定义身份则索引 `group_ids`，查询加 `filter=group_ids/any(...)`，组变化时同步重索引或明确允许的短暂脏读。

索引可全租户建立，查询必须带身份。模型看到越权 token 后再删结果，日志或 chain of thought 仍可能泄漏。移出频道或标签升级要及时影响检索，embedding 缓存可保留，但按用户得到的命中列表不能跨用户复用。向量子查询用了 `filterOverride` 时还要重写 ACL 谓词，避免关键词路过滤而向量路绕过。

## 引用检查内容支持与访问权限

每个断言绑定 `document_key`、段落 id 和文本跨度，不能在证据 $E$ 中找到支持就删句或说「索引里没写」，契约见 `msft-copilot-ground`。语义 caption 是摘要高亮，文档键和 chunk id 才用于定位主键；装饰性的行号无法代替可核验跨度。

引用点击也要使用当前用户身份，不能让应用身份提供越权预览。约束 decoding 可以把 doc id 限制在此次检索集合内，减少乱写文件名，见 `msft-constrained-decode`；它不负责权限，权限在 L1 检查。

评测分别报用户可见金标的 recall@k、越权率（要求 0）、引用可点击率和证据外命题率。多召回无关 wiki 不一定更好，召回用户不可见文档则直接违反权限。过期文档按 item id 删除旧块重写，回答带时间戳，时效由元数据管理。

## 追问

**为什么不能全量搜索后应用过滤？**
那时引擎已打分并可能记录越权命中，应用一旦误传给模型就会泄漏。身份过滤应进入查询。

**混合一定比纯向量好吗？**
多数 RAG 场景可从混合加语义排序受益，仍要分别测试专名、错误码、SKU、改写和多语言切片。

**与 M365 语义索引相同吗？**
不相同。Copilot 通过 Graph 和 M365 对象权限工作；Azure AI Search 的索引、切片与 ACL 同步由自己的应用管理。

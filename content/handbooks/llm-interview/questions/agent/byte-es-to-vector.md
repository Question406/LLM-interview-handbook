---
id: byte-es-to-vector
section: agent
order: 202
level: A
title: 字节 Agent 一面：从 ES 切到向量检索，哪些能力升、哪些会降？
quick: >-
  向量检索更容易找到同义、口语和改写的表达，但精确 ID、错误码、指定关键词的命中和可解释的过滤会变差。生产上一般混合，让 ES
  处理过滤与专有名词，向量检索查找语义相近的内容，最后重排候选结果。
tags:
  - ByteDance
  - Elasticsearch
  - Vector Search
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 字节跳动-Agent开发实习生 一面（45分钟）
    url: 'https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604'
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：Agent 开发实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“为什么选择用 ElasticSearch”**；**“如果从 ES 切换向向量检索，哪些能力会下降，哪些能力会提升？”**

切到向量检索，同义、口语和改写类的 query 会变好，精确 ID、错误码、必须命中的关键词和可解释的结构化过滤会变差。所以生产上一般混合：过滤和专有名词留在 ES，语义近邻走向量，统一候选池后再 rerank，再用 Recall@$K$ 和精确命中率分别验收。字节 Agent 实习一面连着问「为什么用 ES」和「切过去升什么降什么」，把切换讲成全面升级是最常见的错。

先说为什么当初用 ES。日志、配置、工单号、权限过滤在倒排上很成熟，布尔过滤、租户字段、时效、可解释的命中高亮和调权都是现成能力，运维和相关性调权也可控。Agent 场景里大量 query 是「这个 error_code」「这个配置键」「这个工单」，精确命中比语义近邻重要。选 ES 的理由是过滤和专有名词是刚需，跟它传不传统没关系。

切过去之后，升的一面，比如「那个超时的接口」这种口语说法，向量能召到相关文档。降的一面，比如「error_code=5001」，可能被一堆近义噪声挤掉；ANN 是近似检索，还会偶发漏召，调试起来也比看 inverted index 难。所以过滤和专有名词留在 ES，语义近邻走向量，统一候选池后再 rerank，权限过滤仍然放在融合前。

同一面要是追问项目里报过的 Recall@$K$，要讲清评测集怎么更新、怎么做时间切分、有没有精确命中子集，避免只在一个被记熟的测试集上刷分。也别用单一的 Recall 宣布向量全面更好。混合的细节见 `ant-bm25-hybrid`、`baichuan-three-path-recall`，ES 的用法可以对照 `jd-es-vector-usage`。

## 追问

**过滤为什么不能事后做？**
先召回再过滤，会泄漏无权文档的存在和分数，也浪费 $k$ 的配额。租户条件应该直接写成检索谓词。

**向量检索能加 metadata filter 吗？**
能，但那已经算混合了。纯向量切换一般指丢掉倒排和布尔查询。

**怎么验收「没变差」？**
同时报语义集的 Recall 和 ID / 关键词的必须命中率，后者掉了就不能切。

**Agent 为什么更怕漏精确符号？**
工具参数和排障都依赖精确的键。漏掉一个 error_code，后面的规划就建在错的文档上了。

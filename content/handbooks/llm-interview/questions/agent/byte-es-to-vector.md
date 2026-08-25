---
id: byte-es-to-vector
section: agent
order: 202
level: A
title: 字节 Agent 一面：从 ES 切到向量检索，哪些能力升、哪些会降？
quick: >-
  升的是同义、口语、改写召回；降的是精确 ID、错误码、必须命中的关键词和可解释过滤。生产应混合：过滤与专有名词留
  ES，语义近邻走向量，再用 rerank。别把切换讲成全面升级。
tags:
  - ByteDance
  - Elasticsearch
  - Vector Search
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节跳动-Agent开发实习生 一面（45分钟）
    url: https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：Agent 开发实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“为什么选择用ElasticSearch”**；**“如果从ES切换向向量检索，哪些能力会下降，哪些能力会提升？”**

字节 Agent 实习一面连问「为什么用 ES」和「切到向量升什么降什么」。这块容易直接答成把切换讲成全面升级。正确结构：升 / 降各举一例 → 混合检索 → 用 Recall@$K$ 与精确命中率分别验收。混合细节见 `ant-bm25-hybrid`、`baichuan-three-path-recall`，ES 用法也可对照 `jd-es-vector-usage`。

## 为什么先用 ES

日志、配置、工单号、权限过滤在倒排里成熟：布尔过滤、租户字段、时效、可解释的命中高亮和调权都是现成能力。运维和相关性调权可控。Agent 场景大量 query 是「这个 error_code / 这个配置键 / 这个工单」，精确命中比语义近邻更重要。选 ES 不是因为「传统」，是因为过滤和专有名词是刚需。

## 切到纯向量：升什么、降什么

升：同义、口语、改写。「那个超时的接口」能召到相关文档。降：精确 ID、错误码、必须命中的关键词、可解释的结构化过滤；「error_code=5001」可能被近义噪声挤掉。ANN 近似还会引入偶发漏召，调试比看 inverted index 难。生产应混合：过滤与专有名词留 ES，语义近邻走向量，统一候选池后再 rerank。权限过滤仍在融合前。

同面若追到项目里报过的 Recall@$K$，要讲评测集更新、时间切分和精确命中子集，避免只刷一个被记熟的测试集。不要用单一 Recall 宣布向量全面更好。

## 追问

- **过滤为什么不能事后做？** 先召后滤会泄漏无权文档的存在与分数，也浪费 $k$ 配额。租户条件应是检索谓词。
- **向量能否加 metadata filter？** 能，那已经是混合。纯向量切换通常指丢掉倒排与布尔查询。
- **如何验收「没变差」？** 同时报语义集 Recall 和 ID/关键词必须命中率；后者掉了就不能切。
- **Agent 为什么更怕漏精确符号？** 工具参数和排障依赖精确键。漏一个 error_code，后续规划会建在错文档上。

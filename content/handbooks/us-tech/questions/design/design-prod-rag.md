---
id: design-prod-rag
section: design
order: 1
level: S
title: 设计：生产 RAG（切片、新鲜度、权限、引用、p95）
quick: >-
  我会先定文档权限、有效期、引用要求和 p95，再按标题、条款、表格结构切块。检索前用元数据过滤 ACL
  和作废内容，生成后逐句核对证据，引用对不上就删句或拒答；向量本身不会自动过期。
tags:
  - RAG
  - Amazon
  - Google
  - Latency
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
    url: 'https://arxiv.org/abs/2005.11401'
    type: primary
  - title: Amazon Bedrock
    url: 'https://aws.amazon.com/bedrock/'
    type: primary
  - title: System Design in a Hurry
    url: 'https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction'
    type: secondary
---

## 题目描述

本题是手册归纳的系统设计练习。流量、数据量和具体 SLO 未给定时，请先列出可调整的假设，不把假设当成已披露事实。

### 场景与目标

设计企业知识库问答服务。文档带租户、访问权限、版本和有效期，并会持续新增、修改或作废；用户希望得到可以定位到证据的回答。

### 需要满足的功能

- 接收用户身份、会话与问题，从用户有权访问的有效材料中回答。
- 管理资料更新和删除，使回答能够标明所依据的文档版本与位置。
- 无相关材料、证据互相冲突或服务失败时，返回明确的无答案或降级结果。

### 约束与交付物

不能泄漏其他租户或无权限文档的内容与存在性，也不能引用作废政策。需要澄清规模、更新时效、引用粒度、p95 和成本预算，并提供相应评测与监控目标。

请说明 scope 和 constraints、对外接口及返回语义、核心数据对象、主要请求的完整生命周期、故障与恢复行为，以及能验证设计是否达标的指标。题目不预先指定数据库、模型或调度算法；需要解释自己作出的选择与代价。

### 请求与结果示例

某政策在 00:00 生效、旧版同时作废，用户在 00:05 提问时，回答应遵守事先约定的新鲜度目标；任何引用都能回到该用户可读的有效版本。

## 可以这样回答

生产 RAG 我会先保证三件事：只检索当前用户有权看的有效文档，回答能回到具体证据块，检索和生成都在 p95 预算内。比如新政策 0 点生效，0:05 仍引用昨日条款，首先要查索引新鲜度，换更大的模型也解决不了。Lewis 的 RAG 论文提供检索加生成的骨架，实际设计还要把切片、新鲜度、ACL 和引用接好。

Google Assistant / 内搜、Meta 工作问答、Amazon Bedrock 企业知识库和 Microsoft Copilot grounding 都涉及这些约束，Hello Interview 式白板题也会逐项追问。公司专项见 `amazon-bedrock-rag` 和 `apple-siri-grounded`。

## 技术备查

## 解题思路与参考答案

生产 RAG 我会先保证三件事：只检索当前用户有权看的有效文档，回答能回到具体证据块，检索和生成都在 p95 预算内。比如新政策 0 点生效，0:05 仍引用昨日条款，首先要查索引新鲜度，换更大的模型也解决不了。Lewis 的 RAG 论文提供检索加生成的骨架，实际设计还要把切片、新鲜度、ACL 和引用接好。

Google Assistant / 内搜、Meta 工作问答、Amazon Bedrock 企业知识库和 Microsoft Copilot grounding 都涉及这些约束，Hello Interview 式白板题也会逐项追问。公司专项见 `amazon-bedrock-rag` 和 `apple-siri-grounded`。

## 切片和权限先于 embedding

我会先问语料规模、更新频率、是否有租户 / ACL、要不要句级引用、p95 数字。这些约束确定后，才能选择索引和服务架构。

切片按标题、条款、table boundaries 切，重叠只为了不把句子从中间切断。固定 512 token 会把「仅适用于危险品」切丢，后面生成再准也是错的。表格尽量整表进一块，太大再按行加表头副本。元数据绑在块上：`doc_id`、版本、生效/作废时间、租户、权限组、语言、源 URI。

索引到千万块时，过滤必须在 ANN 之前或走支持预过滤的引擎。路径是：ACL ∩ 未作废 ∩ 语言/市场，再向量或混合检索（BM25 + dense）。只靠余弦、把权限写进 prompt「请不要引用无权限文档」，模型会漏：检索层已经把不该看的块打进上下文了。存在性泄漏也算事故：无权限用户不该靠「检索为空 vs 有结果但生成拒绝」来探测文档在不在。

embedding 模型升级要双写、按 `doc_id` 切流，不能假设新旧向量可混排。混合检索的融合用倒数排名（RRF）即可，权重现场用标注集扫，不要口头保证「语义一定赢关键词」。

白板把过滤写成调用，避免只画箭头：

```python
def retrieve(q, user):
    hits = hybrid_search(
        q,
        filters={"acl": acl_groups(user), "expired": False},
        k=50,
    )
    return rrf(hits.bm25, hits.dense, k=8)
```

ACL 在引擎里做，不在应用层先取 200 再丢。租户隔离用独立索引或强制 filter；共享索引必须测跨租户召回率为 0。引用可以很土：生成带 `c12` 标记，后处理对不上的句子直接删。

## 新鲜度、引用、失败模式

向量不会过期。新条款生效靠：解析 → 按 `doc_id` 删旧块 → 写新块 → 索引 SLO（例如 15 分钟内可检索）。回答里带文档时间戳。当天作废的条款若还能被引用，是事故，不是「相关性还行」。

引用：每个断言对齐到 `chunk_id`。对不上就删句或改口「材料里没写」。评测拆开：检索 recall@$k$、引用精确率、证据支持准确率、过期引用率（目标 0）、ACL 泄漏（目标 0）。hallucination 通常比慢更贵。

失败模式：热更新读写到一半，用户看到新旧条款拼接；切块过碎，cross-encoder 重排救不回缺失的限定句；生成把两块拼成一条从未出现的政策；查询 embedding 超时后静默降级只走 BM25，语义问句全崩却没打日志。

不要报一个平均延迟。例：总预算 2 秒。查询编码 30–50 ms，检索 200–400 ms，重排 50–100 ms，生成 1.0–1.3 s，余量给队列、安全过滤、重试。p95 看尾部：冷索引、GC、生成打满 token。提示只塞 top-$k$ 短块，不要塞整份 PDF。检索质量不够时加一块重排，而不是加上下文长度。

流式可以早出第一个 token，但引用校验要在 sentence boundaries 做，不能先把没引用的事实吐完再改。离线用 (问题, 金标条款) 算检索和有实际证据支持；线上看改写率、升级工单、过期引用告警。A/B 的护栏是事故率，不是 BLEU。和客服工具链的 permissions 与 failure handling 见 `design-chat-tools`，评测污染见 `design-eval-platform`。

一个数字例子：索引 10 分钟滞后、政策 0 点生效。0:05 的问答如果仍引用昨日条款，就是 freshness SLO 破了，跟模型无关。降级顺序也要写死：embedding 超时走 BM25；检索全空就拒答并给人工入口，禁止用参数记忆补政策。

## 追问

**为什么不只托管 Knowledge Base 默认切块？**
默认切块和同步节奏保不住表格和分钟级生效。托管是底座，条款结构和 ACL 是你的责任。
**权限在生成后再滤？**
晚了。上下文里已经有秘密，prompt 挡不住，日志也可能落盘。
**embedding 换了旧索引怎么办？**
双写、按文档切流、检索侧带模型版本；混排等于随机召回。
**和纯语义搜索的差别？**
搜索可以只返回链接；生产 RAG 多了生成 hallucination 和引用契约。检索底座同构，见 `design-search`。

---
id: design-prod-rag
section: design
order: 1
level: S
title: 设计：生产 RAG（切片、新鲜度、权限、引用、p95）
quick: "先钉契约：谁能看哪些文档、答案必须能指回块、p95 拆到检索和生成。切片按结构不是按固定 token 数。权限和作废走元数据过滤，不要指望向量自己过期。引用对不上就删句或拒答。"
tags:
  - RAG
  - Amazon
  - Google
  - Latency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
    url: https://arxiv.org/abs/2005.11401
    type: primary
  - title: Amazon Bedrock
    url: https://aws.amazon.com/bedrock/
    type: primary
  - title: System Design in a Hurry
    url: https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction
    type: secondary
---

Google Assistant / 内搜、Meta 工作问答、Amazon Bedrock 企业知识库、Microsoft Copilot grounding 都会把「上个向量库」拆开问。Lewis 的 检索增强生成（RAG） 论文给的是检索加生成骨架；Hello Interview 式白板要的是约束：切片、新鲜度、ACL、引用、p95。公司专项见 `amazon-bedrock-rag` 和 `apple-siri-grounded`。

## 切片和权限先于 embedding

我会先问语料规模、更新频率、是否有租户 / ACL、要不要句级引用、p95 数字。缺这些就画架构，等于还没开始。

切片按标题、条款、表格边界切，重叠只为了不把句子从中间切断。固定 512 token 会把「仅适用于危险品」切丢，后面生成再准也是错的。表格尽量整表进一块，太大再按行加表头副本。元数据绑在块上：`doc_id`、版本、生效/作废时间、租户、权限组、语言、源 URI。

索引到千万块时，过滤必须在 ANN 之前或走支持预过滤的引擎。路径是：ACL ∩ 未作废 ∩ 语言/市场，再向量或混合检索（BM25 + dense）。只靠余弦、把权限写进 输入提示（prompt）「请不要引用无权限文档」，模型会漏：检索层已经把不该看的块打进上下文了。存在性泄漏也算事故：无权限用户不该靠「检索为空 vs 有结果但生成拒绝」来探测文档在不在。

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

引用：每个断言对齐到 `chunk_id`。对不上就删句或改口「材料里没写」。评测拆开：检索 recall@$k$、引用精确率、证据支持准确率、过期引用率（目标 0）、ACL 泄漏（目标 0）。幻觉通常比慢更贵。

失败模式：热更新读写到一半，用户看到新旧条款拼接；切块过碎，cross-encoder 重排救不回缺失的限定句；生成把两块拼成一条从未出现的政策；查询 embedding 超时后静默降级只走 BM25，语义问句全崩却没打日志。

## p95 预算

不要报一个平均延迟。例：总预算 2 秒。查询编码 30–50 ms，检索 200–400 ms，重排 50–100 ms，生成 1.0–1.3 s，余量给队列、安全过滤、重试。p95 看尾部：冷索引、GC、生成打满 token。提示只塞 top-$k$ 短块，不要塞整份 PDF。检索质量不够时加一块重排，而不是加上下文长度。

流式可以早出第一个 token，但引用校验要在句子边界做，不能先把没引用的事实吐完再改。离线用 (问题, 金标条款) 算检索和有实际证据支持；线上看改写率、升级工单、过期引用告警。A/B 的护栏是事故率，不是 BLEU。和客服工具链的边界见 `design-chat-tools`，评测污染见 `design-eval-platform`。

一个数字例子：索引 10 分钟滞后、政策 0 点生效。0:05 的问答如果仍引用昨日条款，就是 freshness SLO 破了，跟模型无关。降级顺序也要写死：embedding 超时走 BM25；检索全空就拒答并给人工入口，禁止用参数记忆补政策。

## 追问

- **为什么不只托管 Knowledge Base 默认切块？** 默认切块和同步节奏保不住表格和分钟级生效。托管是底座，条款结构和 ACL 是你的责任。
- **权限在生成后再滤？** 晚了。上下文里已经有秘密，prompt 挡不住，日志也可能落盘。
- **embedding 换了旧索引怎么办？** 双写、按文档切流、检索侧带模型版本；混排等于随机召回。
- **和纯语义搜索的差别？** 搜索可以只返回链接；生产 RAG 多了生成幻觉和引用契约。检索底座同构，见 `design-search`。

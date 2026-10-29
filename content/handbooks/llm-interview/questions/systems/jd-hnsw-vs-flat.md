---
id: jd-hnsw-vs-flat
section: systems
order: 141
level: A
title: 京东：向量检索里 IVF / HNSW 和暴力有何差异？
quick: >-
  FLAT 扫全库，结果精确；IVF 先选 cluster 再扫描其中的向量，可以用 nprobe 调整召回和延迟；HNSW
  沿分层图找近邻，查询快但更占内存。选择时要看数据量、目标 p95、可接受的召回损失，以及过滤条件怎样参与检索。
tags:
  - JD
  - Vector Search
  - HNSW
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 京东大模型应用开发 实习面经
    url: 'https://www.nowcoder.com/feed/main/detail/904555611d13461da9288d4147b7550b'
    type: candidate-first-hand
  - title: 27暑期实习-京东Agent开发二面分享
    url: 'https://www.nowcoder.com/feed/main/detail/6af1c8611e434bbe8ba9cfa2bd0eaf18'
    type: candidate-first-hand
  - title: Redis 向量索引
    url: >-
      https://redis.io/docs/latest/develop/interact/search-and-query/advanced-concepts/vectors/
    type: primary
---

## 真题记录

- 公司：京东
- 团队 / 岗位：大模型应用开发 / Agent
- 届别 / 流程：实习；一面或二面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“IVF 和 HNSW 的差异？”**；二面追问 Redis 向量检索内部算法

FLAT、IVF 和 HNSW 主要是在精确度、查询速度、建库成本和内存之间做取舍。FLAT 给出精确检索的参考结果；IVF 只搜索部 clustering；HNSW 用分层图缩小搜索范围。选哪一种，要拿 $N$、目标 p95 和可接受的召回损失来判断。

比如电商检索增强生成（RAG）除了找语义相近的商品，还要过滤租户、类目和库存。近邻找得快，过滤后却没有足够候选，也达不到业务目标。因此我会测带过滤的 Recall@k 与延迟曲线。Redis 常见的是 FLAT 与 HNSW；缓存是否该加，则是另一道问题。

## 从精确检索到近似检索

FLAT，也就是暴力检索，会对每个 query 扫全库，对向量条数是 $O(N)$，复杂度 $O(N\cdot d)$，召回是参考上限。百万级以上延迟不可接受，适合金标评测、小租户、或过滤后候选已经很少。Agent 里用它当评测基线，不要当线上主路径。

IVF 先把库聚成 $nlist$ 个 cluster，query 只探 `nprobe` 个 cluster 再扫倒排。建索引相对便宜、内存小于图索引，但 cluster boundaries 会漏召：真实近邻若落在未探 cluster 里就丢了。`nprobe` 越大召回越好、延迟越差，这是一条可调曲线，不是简单的开关。过滤条件和 cluster 结构冲突时更明显：先按类目 TAG 砍掉 90% 再 IVF，和「先 IVF 再过滤」召回差一截。我会问清过滤是 pre-filter 还是 post-filter。



HNSW 用多层导航图做 ANN：上层稀疏跳、下层精细搜。查询延迟低、召回靠 `efSearch` / `M` 调。代价是图占内存大（每点要存邻居），增删不如 IVF 灵活，重建成本高。热点 SKU 更新频繁时，图的局部修复和全量重建要有策略，不能假设「插入就是 $O(1)$」。

如果更在意建库速度、内存和过滤，可以优先评估 IVF；如果库相对稳定、查询延迟要求很低，可以优先评估 HNSW。两者都是近似，都要拿 FLAT 在抽样集上画 Recall-Latency。距离函数必须和 embedding 训练时一致（IP / L2 / cosine），normalization 没做却用 IP，排序可能出错而没有明显报错。

## 把过滤和服务成本一起测

电商场景通常需要把向量 ANN 和类目 / 租户 / 库存规则结合起来。串店、过季、无货要用元数据过滤，不能指望 embedding 自己学会。多路召回（文本倒排 + 向量）再交融合，比单路把 `efSearch` 开到最大更稳。量化（PQ / SQ）再换一档内存，但会叠加近似误差，评测要单独报。服务侧：HNSW 常驻内存，要按分片 / 副本算 RSS，不要只报 QPS。

## 追问

**为什么不用 FLAT？**
百万级 $O(N\cdot d)$ 延迟不可接受。FLAT 当金标评测和过滤后小候选集的基线，线上用 ANN，并报告相对 FLAT 的 Recall@k 损失。小租户可以一直 FLAT。
**`nprobe` 和 `efSearch` 是什么？**
IVF 探几个 cluster；HNSW 搜索时动态候选集大小。都是召回-延迟旋钮，面试报曲线和目标 p95，不要报库默认值。加大这两个数都能买召回、付延迟。
**过滤放哪？**
pre-filter 可能让 IVF 探到 empty cluster、HNSW 图走偏；post-filter 可能滤完不足 $k$。电商常用硬条件进索引属性、软条件后处理。串店问题必须靠租户 TAG，不能指望 embedding。
**Redis 里有哪些？**
RediSearch 一类提供 FLAT 与 HNSW。选 HNSW 要能说出图内存和增删代价，选 FLAT 要能说出 $N$ 上限。大规模 IVF/PQ 往往拆到专用引擎，Redis 缓存热点。
**和倒排怎么配合？**
向量负责语义近邻，倒排负责精确词和类目。融合后再给 Agent 当短名单，不要把全库 top-1000 塞进 prompt，那会变成长上下文成本问题。

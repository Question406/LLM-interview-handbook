---
id: jd-hnsw-vs-flat
section: systems
order: 141
level: A
title: 京东：向量检索里 IVF / HNSW 和暴力有何差异？
quick: >-
  FLAT 精确但 $O(N)$；IVF 先探簇再扫倒排，建库快、召回受 nprobe 限制；HNSW 用分层图做 ANN，查询快、吃内存。选型看
  N、延迟和可接受的召回损失，并和过滤条件是否兼容。
tags:
  - JD
  - Vector Search
  - HNSW
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 京东大模型应用开发 实习面经
    url: https://www.nowcoder.com/feed/main/detail/904555611d13461da9288d4147b7550b
    type: candidate-first-hand
  - title: 27暑期实习-京东Agent开发二面分享
    url: https://www.nowcoder.com/feed/main/detail/6af1c8611e434bbe8ba9cfa2bd0eaf18
    type: candidate-first-hand
  - title: Redis 向量索引
    url: https://redis.io/docs/latest/develop/interact/search-and-query/advanced-concepts/vectors/
    type: primary
---

## 真题记录

- 公司：京东
- 团队 / 岗位：大模型应用开发 / Agent
- 届别 / 流程：实习；一面或二面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“IVF和HNSW的差异？”**；二面追问 Redis 向量检索内部算法

错法：把三种索引说成「HNSW 一定更好」。它们换的东西不同：FLAT 换精确，IVF 换建库便宜，HNSW 换查询延迟。选型看 $N$、p95、可接受的召回损失，以及过滤条件能不能和索引结构共存。电商 RAG 几乎总是「ANN + 倒排 / TAG 过滤」，不是纯向量。报告 Recall@k 对延迟曲线，不要只说「我们用了 HNSW」。Redis 向量常见 FLAT 与 HNSW 两种，同面缓存卡讲何时用 Redis，本题讲索引差异。

## FLAT 与 IVF：精确上限和探簇

FLAT / 暴力：每个 query 扫全库，复杂度 $O(N\cdot d)$，召回是参考上限。百万级以上延迟不可接受，适合金标评测、小租户、或过滤后候选已经很少。Agent 里用它当评测基线，不要当线上主路径。

IVF：先把库聚成 $nlist$ 个簇，query 只探 `nprobe` 个簇再扫倒排。建索引相对便宜、内存小于图索引，但簇边界会漏召：真实近邻若落在未探簇里就丢了。`nprobe` 越大召回越好、延迟越差，这是一条可调曲线，不是布尔。过滤条件和簇结构冲突时更明显：先按类目 TAG 砍掉 90% 再 IVF，和「先 IVF 再过滤」召回差一截。我会问清过滤是 pre-filter 还是 post-filter。

## HNSW：分层图换查询延迟

HNSW 用多层导航图做 ANN：上层稀疏跳、下层精细搜。查询延迟低、召回靠 `efSearch` / `M` 调。代价是图占内存大（每点要存邻居），增删不如 IVF 灵活，重建成本高。热点 SKU 更新频繁时，图的局部修复和全量重建要有策略，不能假设「插入就是 $O(1)$」。

和 IVF 对比口诀：建库快、内存省、过滤友好 → 偏 IVF；查询要极低延迟、库相对稳 → 偏 HNSW。两者都是近似，都要拿 FLAT 在抽样集上画 Recall-Latency。距离函数必须和 embedding 训练时一致（IP / L2 / cosine），归一化没做却用 IP，排序会 silently 错。

## 落地：ANN 不是检索的全部

京东场景几乎总是向量 ANN + 类目 / 租户 / 库存规则。串店、过季、无货要用元数据过滤，不能指望 embedding 自己学会。多路召回（文本倒排 + 向量）再交融合，比单路把 `efSearch` 开到最大更稳。量化（PQ / SQ）再换一档内存，但会叠加近似误差，评测要单独报。服务侧：HNSW 常驻内存，要按分片 / 副本算 RSS，不要只报 QPS。

## 追问

- **为什么不用 FLAT？** 百万级 $O(N\cdot d)$ 延迟不可接受。FLAT 当金标评测和过滤后小候选集的基线，线上用 ANN，并报告相对 FLAT 的 Recall@k 损失。小租户可以一直 FLAT。
- **`nprobe` 和 `efSearch` 是什么？** IVF 探几个簇；HNSW 搜索时动态候选集大小。都是召回-延迟旋钮，面试报曲线和目标 p95，不要报库默认值。加大这两个数都能买召回、付延迟。
- **过滤放哪？** pre-filter 可能让 IVF 探到空簇、HNSW 图走偏；post-filter 可能滤完不足 $k$。电商常用硬条件进索引属性、软条件后处理。串店问题必须靠租户 TAG，不能指望 embedding。
- **Redis 里有哪些？** RediSearch 一类提供 FLAT 与 HNSW。选 HNSW 要能说出图内存和增删代价，选 FLAT 要能说出 $N$ 上限。大规模 IVF/PQ 往往拆到专用引擎，Redis 缓存热点。
- **和倒排怎么配合？** 向量负责语义近邻，倒排负责精确词和类目。融合后再给 Agent 当短名单，不要把全库 top-1000 塞进 prompt，那会变成长上下文成本问题。

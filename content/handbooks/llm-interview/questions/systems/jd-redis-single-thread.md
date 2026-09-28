---
id: jd-redis-single-thread
section: systems
order: 190
level: A
title: 京东 Agent 二面：Redis 单线程为什么还能高并发？向量检索内部用什么算法？
quick: >-
  命令执行单线程是为了避免锁；吞吐来自内存 + I/O 多路复用。大 key、慢 Lua、全量扫描会堵住事件循环。向量侧常见
  FLAT 暴力和 HNSW 近似，要按召回与延迟选型，并带租户元数据过滤。
tags:
  - JD
  - Redis
  - HNSW
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 27暑期实习-京东Agent开发二面分享
    url: https://www.nowcoder.com/feed/main/detail/6af1c8611e434bbe8ba9cfa2bd0eaf18
    type: candidate-first-hand
  - title: Redis 单线程与 I/O 多路复用
    url: https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/
    type: primary
  - title: Redis 向量索引
    url: https://redis.io/docs/latest/develop/interact/search-and-query/advanced-concepts/vectors/
    type: primary
---

## 真题记录

- 公司：京东
- 团队 / 岗位：Agent 开发
- 届别 / 流程：27 暑期实习；二面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“Redis 是单线程的，为什么它还能支持高并发？”**；**“Redis 做语义向量的相似度检索，内部用的是什么算法？”**

错法：把「单线程」理解成整个进程只有一个线程，或反过来以为多线程 Redis 就一定更快。核心命令执行串行是为了 避免锁、保证每个命令原子；吞吐来自内存随机访问 + I/O 多路复用（epoll），不是来自并行算指令。堵点是大 value、`KEYS`、慢 Lua、全量聚合，它们会占住事件循环，后面所有连接一起排队。同面「何时加缓存」讲场景，本题讲为什么快、向量怎么建。

## 单线程快在哪，堵在哪

网络收发、AOF rewrite、RDB fork、过期清理可以在旁路线程；命令执行仍是一条事件循环。好处：没有细粒度锁、没有命令交叉导致的中间态，pipeline 和多路复用能把微秒级 GET 堆到十万 QPS 量级（纯内存、小 key）。这和 LLM serving 的 continuous batching 不是一回事：Redis 是串行很快的短命令，serving 是 GPU 上交错长请求。

会堵的操作：大 key（一次返回 MB 级）、`KEYS *`、跨 slot 的复杂 Lua、RediSearch 上一次扫太多文档。Agent 会话 state 若把整段对话塞进一个 string，读写都会卡循环。拆 key、用 SCAN、把重计算下沉到应用，比「开多线程 Redis」更对症。Redis 6+ I/O threads 只加速读写 socket，不把 `HNSW` 搜索并行化；别说成「现在已经是多线程数据库」。

持久化和复制在旁路，但 fork 瞬时 RSS 翻倍、主从积压会反过来拖命令。面试提一句：高并发假设的是命令短、value 小、不阻塞循环。

## 向量：FLAT 与 HNSW

RediSearch / RedisVL 一类索引提供 FLAT（精确、线性扫）和 HNSW（分层图 ANN）。电商 RAG 选型同 `jd-hnsw-vs-flat`：小库或金标用 FLAT；线上低延迟用 HNSW，调 `EF_RUNTIME` / `M`，接受召回损失。距离度量（COSINE / IP / L2）必须和 embedding 训练一致。

几乎总会加类目 / 租户 TAG 过滤，否则召回串店。过滤是索引属性还是后过滤，决定召回和延迟。向量检索比 GET 重得多：一次 kNN 可能毫秒到几十毫秒，会占住同一条命令循环。这就是「单线程高并发」和「向量检索」被同场问的原因。热 key 和大 top-k 会把 QPS 打穿。分片、只把热点 SKU 放 Redis、冷数据走专用向量库，是常见拆法。不要把 Redis 向量说成「免费的 FAISS 集群」。

## 和缓存题怎么分

何时用 Redis 见 `jd-when-to-cache`：高频读、可短暂不一致。本题我会收成：单线程 = 命令原子 + 无锁；快 = 内存 + 多路复用；慢命令会堵所有人。向量 = FLAT 精确 / HNSW 近似，必须带租户过滤。Serving 侧 LLM 的并发模型完全不同，不要用 Redis 线程模型去类比 vLLM。

## 和向量题怎么收

单线程高并发的前提是命令短、value 小。向量 kNN 一旦变成毫秒到几十毫秒的重查询，同一条循环上的 GET 会被拖死，所以要限 top-k、拆实例、热点走 GET 缓存。HNSW 吃 RSS，fork 持久化会翻倍内存，缓存和搜索不要混在一个进程里硬扛。同面「何时缓存」决定放不放，本题决定放进去会不会堵。LLM serving 的连续 batch 是另一套并发模型，不要类比。

## 追问

- **整个 Redis 只有一个线程吗？** 不是。核心命令执行单线程，为的是无锁和命令原子；网络 I/O、AOF rewrite、RDB fork、过期清理可以在旁路。我会主动拆开「进程」和「命令循环」。
- **为什么大 key 危险？** 一次返回或一次 HNSW 搜索占满事件循环，后面所有连接的 GET 一起排队。会话不要整段对话一个 string，向量不要一次扫过大候选集。拆 key、SCAN、把重计算下沉。
- **I/O threads 能加速 HNSW 吗？** 不能。Redis 6 的 I/O 线程加速的是 socket 读写，不把查询算法并行化。向量搜索仍在命令线程里跑。把「已经多线程」说成 HNSW 能并行会被拆穿。
- **内部算法是什么？** 常见 FLAT 暴力精确和 HNSW 分层图 ANN。按 $N$、p95、可接受召回损失选型，距离函数对齐 embedding，加上类目/租户 TAG 防串店。详见配套向量卡。
- **能当主向量库吗？** 小规模、要和会话缓存同机可以。百万级、要 IVF/PQ/GPU 检索，应拆到专用引擎，Redis 只缓存热点向量和短名单。否则单线程循环和 RSS 都会先爆。

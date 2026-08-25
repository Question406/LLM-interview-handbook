---
id: fund-ann
section: fundamentals
order: 14
level: A
title: HNSW / IVF / PQ 各自是什么？
quick: >-
  HNSW 是多层小世界图近邻搜索；IVF 先聚类到倒排 coarse cells 再搜少量 cells；PQ 把向量子空间量化成
  code，主要省内存并加速距离估计。选型看 recall、延迟、内存和能否增量更新，而不是背定义。
tags:
  - RAG
  - ANN
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs
    url: https://arxiv.org/abs/1603.09320
    type: primary
  - title: Faiss indexes
    url: https://github.com/facebookresearch/faiss/wiki/Faiss-indexes
    type: primary
---

三者经常被当成「三种索引名词」来背。我会答召回、延迟、内存、更新怎么换，而不是默写数据结构。HNSW 用图换高召回和高内存；IVF 用探查的 cell 数换延迟和召回；PQ 用码本近似距离换内存和速度，并通常给召回打折。实践几乎总是组合（IVF-PQ、HNSW 存 PQ code），很少三选一。不要编具体毫秒或百分数，把曲线形状讲清楚即可。

## 三条轴：召回、延迟、内存

近似最近邻没有免费午餐：

- **HNSW：** 查询从稀疏高层图走到密集底层。高召回、低延迟在中等规模上很常见，但图的邻居指针按点存储，内存随 $N\times M$（每点边数）涨，比一份向量副本更大一截。构建也重，动态插入可以做，大规模重建仍贵。适合「内存够、要高 recall@k、更新不是每秒百万级」的 RAG。
- **IVF：** 先把空间分成 coarse centroids，查询只搜 `nprobe` 个倒排列表。`nprobe` 是显式旋钮：小则快、易漏邻近列表里的真邻居；大则接近扫全库。内存主要是原向量（或再量化后的向量）加很小的质心表。适合十亿级、必须控制扫描量的场景；对聚类边界附近的点不友好。
- **PQ：** 把向量切成 $m$ 段，每段用码本代替，距离用查表近似。内存可以从每向量数百维浮点压到几十字节，SIMD 扫库变快；近似误差直接吃掉召回。它是压缩与距离估计，不是单独的「一种搜法」，常挂在 IVF 列表或 HNSW 节点上。

HNSW 的瓶颈往往是 **RAM**；IVF 的瓶颈是 **nprobe 与质心是否过时**；PQ 的瓶颈是 **量化误差 vs 你要的 recall@k**。延迟还取决于是否需要精确重排：用 PQ 短列表召回、再用原向量 rerank，是常见的「先省内存再补召回」。不要背「HNSW 一定最快」。图遍历的随机内存访问在超大图上会变慢；IVF 扫连续倒排列表更缓存友好，`nprobe` 小时可以更低延迟。PQ 的查表距离极快，但若召回不够还要精确 rerank，总延迟包含「近似检索 + 精确重排」，不一定赢。三条轴上移动一个，另外两条通常变差。我会画这张三角，不默写论文标题。

## 组合与更新，比单名词更常考

大规模 RAG 常见配方：

- **IVF-PQ：** 倒排缩小扫描，PQ 缩小每条距离的内存。召回靠 `nprobe`、码本大小和是否对短列表做精确 rerank。内存最好，召回通常低于同内存预算下的未压缩 HNSW。
- **HNSW + 量化向量：** 图还在，边上的向量换成 PQ / scalar quantizer。延迟和好召回仍在，内存下来一截，但图结构本身仍占空间。
- **Flat / 精确：** 小库或必须几乎满分召回时，别上 ANN。我会先估计 $N$ 和延迟预算，再决定要不要上 HNSW。

更新频率是第四轴。IVF 在分布漂移后质心变差，需要重建或增量加列表；HNSW 可插点，删除与图修复更麻烦；PQ 码本一旦过时，全库距离都偏。文档热更新的 RAG，要问「能否接受周期性重建」，不能只报离线 recall。Embedding 模型一换，三种索引全部作废，这比调 `nprobe` 更致命。增量插入时 HNSW 通常最省事，IVF 要决定新点进哪个 list、是否定期重训质心。删除在图索引上是已知痛点，常标记墓碑后批量重建。选型时把「日更新量 / 全库重建窗口」问清楚，否则会上线后才发现每周都要停机建图。

## 怎么选，而不是背百科

给一个具体约束再选：内存紧、十亿级、可接受 rerank → IVF-PQ；内存松、千万级、要高召回低延迟 → HNSW；已经 IVF 但 RAM 爆 → 先 PQ 再决定要不要加短列表精确重排。验收必须用 **同一 query 集上的 recall@k vs 延迟 vs 常驻内存**，不要用训练时的召回代替线上。Embedding 一换，所有指数都要重建，ANN 选型不能独立于向量模型。

参数不要背死数：HNSW 的 `M` / `efSearch`、IVF 的 `nlist` / `nprobe`、PQ 的 $m$ 与码本大小，都是沿曲线滑动的旋钮。现场画一条「横轴延迟、纵轴召回」的示意，把三种方法放在不同区域。`efSearch` 加大，HNSW 召回升、延迟升；`nprobe` 加大，IVF 同理；PQ 的 $m$ 加大，近似更细、内存和距离计算变贵。这些旋钮让你在同一族索引里走曲线，不能把 IVF 调成 HNSW 的内存形态。验收必须用线上 query、同一 embedding，报告 recall@k 与 p95 延迟与常驻内存。用训练语料自检索的召回会虚高。不要编造「HNSW 召回 99%、IVF 95%」这类假数，把权衡方向讲对即可。

## 追问

- **PQ 能单独当索引吗？** 能做压缩暴力扫描，但大库仍要 IVF / HNSW 缩小候选。PQ 主业是内存和近似距离。短列表精确 rerank 是补召回的常用后处理。
- **为什么 IVF 会漏掉近邻？** 真邻居落在未探查的 cell。加大 `nprobe` 或更好的质心能缓解，代价是延迟。分布一漂，质心过时会让泄漏更严重。
- **HNSW 一定比 IVF 准吗？** 在内存充裕、图建好的中小库上常常更高召回；内存不够时你根本建不起同样质量的图，比较无意义。超大库上 IVF-PQ 往往是唯一能放进 RAM 的方案。
- **要满分召回怎么办？** ANN 不保证。小库用精确搜索；大库用短列表 + 原向量 rerank 逼近，并报告实测 recall，而不是承诺满分。不要编造具体百分数。

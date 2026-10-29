---
id: ml101-approx-neighbors
section: classical-models
order: 8
level: A
title: 近似最近邻为什么更快？怎么评价召回和速度？
quick: >-
  近似最近邻用索引缩小搜索范围或近似计算距离，少比较候选，因此更快，但可能漏掉真实最近邻。评价时用精确搜索作参照，同时报告
  recall@k、延迟分位数、throughput 与索引内存。调搜索预算得到召回和速度的曲线，再按业务 threshold 选点。
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'Faiss: Faiss indexes'
    url: 'https://github.com/facebookresearch/faiss/wiki/Faiss-indexes'
    type: primary
  - title: 'Faiss: Index IO, cloning and hyper parameter tuning'
    url: >-
      https://github.com/facebookresearch/faiss/wiki/Index-IO,-cloning-and-hyper-parameter-tuning
    type: primary
---

近似最近邻（ANN）快，是因为它不再对所有向量都做完整比较，而是用索引挑有希望的候选。代价是某些查询会漏掉精确最近邻，所以速度和召回要一起看。

例如倒排文件索引 IVF 先把向量分到若干区域，查询只访问少量相近区域；真实邻居如果落在没访问的区域就会漏掉。分层可导航小世界图（HNSW）则沿邻接关系探索候选。压缩向量还可减少存储和距离计算成本，但会增加近似误差。机制见 [Faiss 索引说明](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)。

设精确搜索前 k 个结果为集合 G，近似结果为 A，可用 $|A\cap G|/k$ 衡量这一条查询的 recall@k，再在代表性查询集上汇总。例如 k=10 时命中八个精确邻居，重合召回为 0.8。要固定距离定义、过滤条件、硬件和 batch，测 P50/P95/P99 延迟、每秒查询数（QPS）、内存及建索引成本。IVF 的 nprobe 或 HNSW 的搜索范围增大通常更准也更慢，参见 [Faiss 参数取舍](https://github.com/facebookresearch/faiss/wiki/Index-IO,-cloning-and-hyper-parameter-tuning)。

## 追问

**ANN recall 高，业务检索就一定好吗？**
不一定。它只说明接近精确向量搜索，向量本身是否表达业务相关性，还要用业务标注评价。

**为什么要看 P99？**
难查询或热点可能搜索更久，平均值会掩盖尾延迟，线上时限常受这部分影响。

---
id: amazon-two-tower
section: amazon
order: 2
level: S
title: Amazon：双塔召回，训练对齐和 serving 近似，ANN 掉点怎么补？
quick: >-
  训练用精确内积和难负例把 query / item 塔对齐；线上用预计算 item 向量加 ANN。掉点几乎都来自「训练时见过的邻居」和「HNSW /
  PQ 真正返回的邻居」不是同一集合。先测 ANN recall，再用 ANN 难负例、词法并集和重排把漏召回补回来。
tags:
  - Amazon
  - Two-Tower
  - Retrieval
  - ANN
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Semantic product search
    url: https://www.amazon.science/publications/semantic-product-search
    type: primary
  - title: Web-scale semantic product search with large language models
    url: https://www.amazon.science/publications/web-scale-semantic-product-search-with-large-language-models
    type: primary
---

Search / Recs / Bedrock 检索岗爱问这题。Amazon Science 的 Semantic Product Search 把商品召回做成双塔：query 塔实时、item 塔离线。后面 BERT 双塔要蒸馏才能扛住电商实时延迟。公开论文和「十亿级目录、毫秒召回」是同一张图。按 Leadership Principles 收：先指标和失败模式，不要只画两个 MLP。

## 训练对齐的是什么

两座塔不共享计算图。query $q$ 出 `[B, D]`，item $i$ 出 `[B, D]`，分打 $s(q,i)=f(q)^\top g(i)$ 或余弦。购买 / 点击是正例。InfoNCE：

$$
L=-\log\frac{\exp(s(q,i^+)/\tau)}{\sum_{i\in\mathcal{N}}\exp(s(q,i)/\tau)}
$$

$\mathcal{N}$ 是正例加负例。现场错法是把 in-batch 负例当成线上分布。Batch 里的随机商品太容易，模型学的是「和随机货分开」，不是「在近邻里排对」。Amazon 那篇还会把 impressed-not-purchased 和随机负例分开，不要一套 triplet 糊过去。

item 塔输入是标题、品牌、类目路径，不是用户历史。用户历史进 query 塔或后面的精排。把点击序列塞进 item 塔，新商品立刻冷启动失败，见 `amazon-cold-start`。

训练必须和 serving 用同一套预处理：同样截断、同样 lower / 分词、serving 关掉 dropout。两塔可以不对称（query 浅、item 深），但 $D$ 和度量必须一致。余弦训练、欧氏检索，掉点你会怪 ANN。

## serving 近似掉在哪

线上不能对亿级 ASIN 做精确 MIPS。item 向量预先算好，丢进 HNSW / IVF-PQ。query 只跑一次塔，再 ANN。训练看到的是精确内积下的 $\mathcal{N}$；线上看到的是量化加图搜索后的 $\hat{\mathcal{N}}$。两集合一散，离线 Recall@100 很好、线上少召回。

掉点拆开量，不要口头「ANN 有损失」：

1. **编码漂移。** 模型周更、目录日更，索引里仍是旧向量。
2. **量化。** PQ / OPQ 把 $D$ 维压成码本，近邻被挤出 top-$k$。
3. **图搜索预算。** HNSW 的 `efSearch`、IVF 的 `nprobe` 太小，recall 先崩，延迟看起来很漂亮。
4. **负例不匹配。** 没在 ANN 邻居上训过，模型不会在「看起来都像」的 200 个里把正例顶上去。

补法按成本排。先在固定 query 集上算「精确 top-$k$ 被 ANN 覆盖的比例」，目标先放到 $0.95$ 以上再谈模型。覆盖不够就加 `efSearch` / `nprobe`，或先别上太狠的 PQ。覆盖够了还掉，从 ANN 索引里挖难负例再训，让训练邻居逼近 serving 邻居。再不够：词法召回并集，见 `amazon-kendra-hybrid`；top 200 用交叉编码器或精排重排。电商里 ASIN、型号、错误码不能靠近邻碰运气，必须有倒排保底。

蒸馏也是对齐。大 cross-encoder 或大双塔当教师，小双塔当学生，论文里约 75M 学生相对 20 倍教师只掉约 3% 相关性，才能进实时预算。不要把教师直接挂到 p99 链路上。

索引新鲜度要有 SLO：新 ASIN 多久可召回、改标题多久重嵌。向量不会自己过期，和 `amazon-bedrock-rag` 里政策条款一个道理。特征版本和索引别名绑在一起发，见 `amazon-feature-store`。

```python
import torch
import torch.nn.functional as F

def infonce(q, p, t=0.05):
    # q, p: [B, D], in-batch negatives
    q = F.normalize(q, dim=-1)
    p = F.normalize(p, dim=-1)
    logits = q @ p.T / t
    return F.cross_entropy(logits, torch.arange(q.size(0), device=q.device))
```

这只是 in-batch。生产要把 ANN 挖到的 ASIN 拼进负例，否则你在优化一个线上不存在的 softmax。

## 追问

- **为什么不把 query、item 塞进同一个 Transformer？** 交叉注意力更准，但 item 不能预计算，延迟从毫秒变成对全库做 Transformer。召回用双塔，精排再用交叉。别把召回和精排合成一段。
- **ANN recall 已经 0.99 为什么还掉转化？** 召回集对了，排序目标可能仍是点击不是购买；或词法精确匹配被语义近邻挤掉。看失败 query：漏 ASIN 是召回，排错是 ranker。
- **item 塔要不要每天全量重嵌？** 改标题、类目、合规状态的走增量；embedding 模型一换必须全量。增量更新和模型版本打在同一索引别名上，否则训练/服务再偏一次。

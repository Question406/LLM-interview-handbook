---
id: amazon-two-tower
section: amazon
order: 2
level: S
title: Amazon：双塔召回，训练对齐和 serving 近似，ANN 掉点怎么补？
quick: >-
  双塔训练用正例和难负例对齐 query / item 向量，线上预计算 item 后用 ANN 召回。掉点先测 ANN
  对精确近邻的覆盖，再查编码版本、量化和搜索预算；覆盖足够后，用 ANN 难负例、词法并集和精排改进相关性。
tags:
  - Amazon
  - Two-Tower
  - Retrieval
  - ANN
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Semantic product search
    url: 'https://www.amazon.science/publications/semantic-product-search'
    type: primary
  - title: Web-scale semantic product search with large language models
    url: >-
      https://www.amazon.science/publications/web-scale-semantic-product-search-with-large-language-models
    type: primary
---

## 可以这样回答

ANN 掉点先拆成两件事：索引有没有找回精确向量搜索的邻居，以及这些邻居是否真能满足用户意图。前者查编码、量化和搜索预算，后者查训练负例与排序目标。比如精确 Recall@100 很好，HNSW / PQ 实际返回的却是另一组商品，继续优化原来的训练 loss 未必能补上。

Amazon Science 的 Semantic Product Search 用 query 塔实时编码、item 塔离线编码来做商品召回；后续 BERT 双塔通过 distillation 适应实时延迟。十亿级目录、毫秒召回需要这种预计算，Search、Recs 和 Bedrock 检索都可以按同样的失败路径分析。

## 技术备查

ANN 掉点先拆成两件事：索引有没有找回精确向量搜索的邻居，以及这些邻居是否真能满足用户意图。前者查编码、量化和搜索预算，后者查训练负例与排序目标。比如精确 Recall@100 很好，HNSW / PQ 实际返回的却是另一组商品，继续优化原来的训练 loss 未必能补上。

Amazon Science 的 Semantic Product Search 用 query 塔实时编码、item 塔离线编码来做商品召回；后续 BERT 双塔通过 distillation 适应实时延迟。十亿级目录、毫秒召回需要这种预计算，Search、Recs 和 Bedrock 检索都可以按同样的失败路径分析。

## 训练先把空间和难负例对齐

query $q$ 和 item $i$ 分别输出 `[B, D]`，用 $s(q,i)=f(q)^\top g(i)$ 或余弦打分。两塔各自计算，购买 / 点击可作正例，InfoNCE 用正例与负例比较：

$$
L=-\log\frac{\exp(s(q,i^+)/\tau)}{\sum_{i\in\mathcal{N}}\exp(s(q,i)/\tau)}
$$

$\mathcal{N}$ 包含正例和负例。随机 in-batch 商品太容易区分，线上却要在相似商品里找对目标。Amazon 论文还区分 impressed-not-purchased 与随机负例，训练时应保留这种差异。

item 塔输入标题、品牌和类目路径，用户历史进入 query 塔或后面的精排。若 item 必须依赖点击序列，新商品就缺输入，见 `amazon-cold-start`。query 塔可以浅、item 塔可以深，但维数 $D$ 与距离度量要一致。截断、lower / 分词也要与 serving 相同，线上关闭 dropout；余弦训练却用欧氏检索会引入额外偏移。

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

这只是 in-batch 基线。生产训练还要加入 ANN 挖出的 ASIN 难负例，让模型学会区分线上真正相近的商品。

## 在线近似逐项测，再按成本修

亿级 ASIN 无法逐个算精确 MIPS。线上把预计算 item 向量放进 HNSW / IVF-PQ，query 塔运行一次再搜索。精确内积的 $\mathcal{N}$ 与量化、图搜索后的 $\hat{\mathcal{N}}$ 会有差异。

先查编码漂移：模型周更、目录日更，索引可能还是旧向量。再查 PQ / OPQ 将 $D$ 维压成码本后损失多少近邻，以及 HNSW 的 `efSearch`、IVF 的 `nprobe` 是否太小。预算小会让延迟好看，同时降低 recall。最后看训练是否缺少 ANN 邻居，让模型在 200 个相似候选中也能区分正例。

固定 query 集，先测精确 top-$k$ 被 ANN 覆盖的比例，可先把目标放到 $0.95$ 以上。覆盖不足时调大 `efSearch` / `nprobe` 或减轻 PQ；覆盖够了再挖 ANN 难负例重训。仍有缺口时合并词法候选，见 `amazon-kendra-hybrid`，再对 top 200 交叉编码或精排。ASIN、型号和错误码要保留倒排精确路径。

distillation 可用大 cross-encoder 或大双塔指导小双塔。公开论文约 75M 学生相对 20 倍教师只损失约 3% 相关性，使它能进入实时预算；教师本身不适合直接塞进 p99 链路。

索引也要有新鲜度 SLO：新 ASIN 多久可召回，标题变更后多久重嵌。向量不会自动过期，与 `amazon-bedrock-rag` 的政策版本同理；特征版本和索引别名一起发布，见 `amazon-feature-store`。

## 追问

**为什么不让 query 和 item 进同一个 Transformer？**
cross-attention 可以更准，但 item 不能独立预计算，无法对全库逐对运行。召回双塔，候选精排再交叉。

**ANN recall 到 0.99，转化还下降呢？**
继续看任务相关性。可能点击目标与购买不一致，或精确商品被语义近邻挤走。失败 query 中先区分漏 ASIN 与 ranker 排错。

**item 每天都要全量重嵌吗？**
标题、类目和合规状态变化可增量更新；embedding 模型变化必须全量重嵌。更新与模型版本绑定同一索引别名。

---
id: meta-dlrm
section: meta
order: 5
level: A
title: Meta：DLRM 推荐，稀疏 embedding 和 MLP 怎么切并行
quick: "DLRM 让稠密特征走 bottom MLP、类别 id 查 embedding，做两两点积交互后由 top MLP 预测 CTR。巨型表按表或行分片，较小 MLP 用数据并行，再用 all-to-all 为每张卡拼齐其样本的 embedding，反向沿相反方向送回梯度。"
tags:
  - Meta
  - DLRM
  - RecSys
  - Embedding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Deep Learning Recommendation Model for Personalization and Recommendation Systems
    url: https://arxiv.org/abs/1906.00091
    type: primary
  - title: facebookresearch/dlrm
    url: https://github.com/facebookresearch/dlrm
    type: primary
  - title: News Feed ranking, powered by machine learning
    url: https://engineering.fb.com/2021/01/26/ml-applications/news-feed-ranking/
    type: secondary
---

DLRM 的并行通常分成两部分：巨型 embedding 表做模型分片，较小 MLP 做数据并行，中间用 all-to-all 对齐样本的特征向量。原因是推荐模型的瓶颈常在稀疏 lookup 与通信，不能直接套 dense Transformer 的切法。

一条样本有连续特征 $x_{\mathrm{dense}}$ 和用户、广告、页面、hash 桶等类别 id。Bottom MLP 先把连续特征投到与 embedding 一样宽；每个类别特征查表 $E_f \in \mathbb{R}^{V_f \times d}$，其中 $V_f$ 可到千万、亿，所有表可达 TB 级。Lookup 输入为 `[B]` int64，输出 `[B, d]`；多值兴趣 id 要 sum / mean pooling，访问更不规则。

论文默认将这些向量和 dense 投影两两点积，得到约 $O(F^2)$ 个交互标量，再送 top MLP、CTR / CVR 头，用 logloss 训练，见 `meta-ranking-logloss`。这是 2019 DLRM 的公开基线，线上还会叠级联、延迟预算与新鲜特征，Feed 多目标见 `meta-newsfeed-rank`。

## 表和样本怎样分摊

MLP 较小，每卡复制一份、各算 $B/N$ 样本很合适；TB 级 embedding 不能每卡复制。Table-wise 将整张表放一张卡，实现简单，但 uid、广告 id 热表可能打满一张卡，冷表却空闲。Row-wise 按 id 段分散大表，负载更均衡，lookup 可能跨卡。按列切 $d$ 也可做，但 interaction 与 pooling 更复杂，较少采用。

每张卡查自己负责的表，再 all-to-all，使第 $i$ 张卡收齐其样本的全部 embedding，才能执行 interaction 与 top MLP。反向再把稀疏梯度 all-to-all 发给持有那些行的卡，更新本地表。只有命中的行有梯度，优化器和通信按 nnz 处理，避免整表 dense all-reduce。

FSDP 切的是同一组 dense 状态，DLRM 切的是特征表与行，见 `meta-fsdp2`。大 MLP 也可叠 FSDP，但不能用 ZeRO-3 代替这里的 embedding 并行。

热 id 频繁读写，Adam fp32 状态也随表行占空间。可以按频率分表，热小表放 GPU、冷表放 CPU 或多卡，或用 hash 碰撞换容量、AdaGrad / Row-wise 优化器减少状态。通信量约为 $B \cdot F \cdot d \cdot \mathrm{bytes}$，反向再来一次，$F$、$d$ 增大时网络可能先于 GEMM 饱和，要关注 RDMA 与拓扑，FlashAttention 解决不了。动态下标与集体通信也容易让 `torch.compile` graph break，见 `meta-pytorch-compile`。

广告还需校准概率，AUC 之外看 predicted vs observed，见 `meta-ads-calibration`。

## 追问

**推理沿用训练分片吗？**
可以沿用，但 batch 与 QPS 不同，热表可能复制多份换低延迟，不能原样照搬拓扑。

**embedding 为什么不直接 DDP？**
每卡复制 TB 级表不现实，DDP 更适合小 MLP。

**交互能换 Transformer 吗？**
可以，但算力和 serving 延迟会明显增加，需要级联或蒸馏支持。先把 lookup、浅 MLP、点积交互的基线讲清。

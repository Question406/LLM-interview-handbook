---
id: meta-dlrm
section: meta
order: 5
level: A
title: Meta：DLRM 推荐，稀疏 embedding 和 MLP 怎么切并行
quick: >-
  稠密特征走 bottom MLP，类别 id 走巨型 embedding 表，交互（两两点积）后再进 top MLP 出 CTR。表太大，embedding
  用模型并行；MLP 小，用数据并行。两段之间用 all-to-all 把各卡查出的向量对齐到样本维。
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

广告 / 推荐 / RecSys MLE 在 Meta 几乎都会碰到「稀疏表 + 小 MLP」。DLRM 是 2019 年的公开骨架，不是今天线上的全部，但面试要用它把并行切分讲清楚。Feed 排序的级联和多目标见 `meta-newsfeed-rank`，本题只收模型怎么切。

## 模型四段，别画成纯 Transformer

一条样本大约是：连续特征 $x_{\mathrm{dense}}$，再加上很多类别 id（用户、广告、页面、hash 桶）。前向：

1. **Bottom MLP：** $x_{\mathrm{dense}}$ 映射到和 embedding 同宽的向量。
2. **Embedding：** 每个稀疏特征一张表 $E_f \in \mathbb{R}^{V_f \times d}$，lookup 得到向量。$V_f$ 可以到千万、亿，表合计 TB 级，这是推荐和 LLM 最大的差别。
3. **Interaction：** 论文默认是 embedding 向量（含 dense 投影）两两点积，拼成交互特征。复杂度大约 $O(F^2)$ 个标量，不是大 GEMM。
4. **Top MLP：** 接到 CTR / CVR 头，训练常用 logloss，见 `meta-ranking-logloss`。

现场别一上来改成「把 id 当 token 做 Transformer」。可以提，但要先承认 DLRM 的工业假设：lookup 是瓶颈、MLP 很浅、特征交叉用点积就够当基线。

Lookup 的 shape：batch 里每个特征是 `[B]` 的 int64 下标，输出 `[B, d]`。多值特征（一个用户一堆兴趣 id）是变长，需要 pooling（sum / mean），这会让 embedding 核更不规则。

## 并行：表切模型，MLP 切数据

MLP 参数相对小，**数据并行**（每卡一份 MLP，样本切 $B/N$）很合适。Embedding 表放不下、也没必要每卡复制：

- **Table-wise（按表切）：** 整张表放在一张卡上。实现简单，但热表（uid、广告 id）会把某张卡打满，冷表空转。
- **Row-wise（按行切）：** 一张大表按 id 段切到多卡。负载更匀，一次 lookup 可能要跨卡。
- 列切 / 把 $d$ 切开比较少见，交互和 pooling 会变烦。

训练一步的通信是 **all-to-all**，不是 Transformer 那种层内 all-reduce。直觉：我这张卡负责若干部表，但 mini-batch 里每条样本的 id 落在所有表上。各卡先按自己管的表做 lookup，再 all-to-all，让第 $i$ 张卡凑齐它那份样本的全部 embedding，才能做 interaction + top MLP。反向把梯度 all-to-all 回去，更新本地表。

和 FSDP 的对比（`meta-fsdp2`）：FSDP 切的是**同一套 dense 权重的副本**；DLRM 切的是**不同特征的表**。两套可以叠（大 MLP 再 FSDP），但面试先把 all-to-all 说完，不要用 ZeRO-3 替代 embedding 并行。

## 面试要能点的坑

Embedding 是 **随机写入 + 极不均衡**。Hot id 的行被所有 batch 碰到，Adam 的 fp32 状态也随行走，热行又慢又费。常见工程：频率分表（热表小、驻 GPU；冷表 CPU / 多卡）、hash 碰撞换容量、AdaGrad / Row-wise 优化器减少状态。

All-to-all 的字节数大约是 $B \cdot F \cdot d \cdot \mathrm{bytes}$ 量级（再乘一次反向）。$d$ 和 $F$ 变大，网络先于 GEMM 饱和。这就是为什么推荐训练常谈 RDMA / 拓扑，而不是 FlashAttention。`torch.compile` 在这种动态下标 + 集合通信上很容易 graph break，见 `meta-pytorch-compile`。

评估不要只报 AUC。广告出价吃的是校准过的概率，见 `meta-ads-calibration`。DLRM 论文本身是系统+模型基线，线上还有级联、延迟预算、特征新鲜度。

## 追问

- **推理和训练切分一样吗？** 可以同一套表分片。推理 batch 和 QPS 不同，有时会把热表复制多份换延迟。不要假设训练拓扑原样上线。
- **为什么不把 embedding 也 DDP？** 复制 TB 级表不现实。DDP 适合 MLP。
- **Interaction 换成 Transformer？** 能，算力和 serving 延迟会跳一个量级，要有级联或蒸馏。先把 baseline 并行讲对再升级。
- **稀疏梯度怎么做？** 只有被 lookup 到的行有梯度。优化器和通信都要按nnz 走，不要对整张表做 dense all-reduce。

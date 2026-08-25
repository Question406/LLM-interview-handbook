---
id: apple-kmeans
section: apple
order: 8
level: A
title: Apple coding：k-means / 近邻，作为电面算法题怎么答到 ML 岗标准？
quick: >-
  向量化算 $[n,k]$ 距离，迭代赋值和更新均值，处理空簇，报 $O(n k d I)$。ML 岗还要接到初始化、k-means++、和端上
  palettization（16 中心 $\approx$ 4-bit）或检索。嵌三层循环只能当草稿，不能当答完。
tags:
  - Apple
  - K-means
  - Coding
  - Nearest Neighbor
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Apple Intelligence Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-intelligence-foundation-language-models
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

公开的 Siri MLE 电面讨论里，k-means 和 attention、sampling 并列成 ML coding 基本功，见 `apple-mha-code`。Exponent 也说 Apple 有的组是应用型 ML 题，有的是常规编码。把它答成双循环刷题，过不了 MLE 标准；答成「调库」又没代码。目标是 15–20 行向量化，外加三个 ML 追问接得住。

## 先写对迭代，再谈技巧

输入 $X\in\mathbb{R}^{n\times d}$，簇数 $k$。目标是

$$
\min_{c,\mu}\sum_{i=1}^{n}\lVert x_i-\mu_{c_i}\rVert_2^2.
$$

这是 NP-hard，Lloyd 迭代只保证单调不增到局部最优。面试先承认这句，避免被问「为什么换种子分数乱跳」。

```python
import numpy as np

def kmeans(x, k, n_iter=20, seed=0):
    n, d = x.shape
    rng = np.random.default_rng(seed)
    mu = x[rng.choice(n, size=k, replace=False)]
    for _ in range(n_iter):
        dist = ((x[:, None, :] - mu[None, :, :]) ** 2).sum(-1)  # [n, k]
        c = dist.argmin(axis=1)
        new = mu.copy()
        for j in range(k):
            m = c == j
            if m.any():
                new[j] = x[m].mean(axis=0)
            else:
                new[j] = x[rng.integers(n)]  # 空簇：随机重启
        if np.allclose(new, mu):
            break
        mu = new
    return mu, c
```

复杂度 $O(n k d I)$，内存 $O(n k)$ 的距离矩阵。$n$ 到百万、$d$ 到几百时这张表会爆，改成分块或 mini-batch：每次用 $b$ 条样本做一次赋值和均值的增量更新。电面 $n$ 小，写全量即可，但要把内存上限说出来。

空簇必须处理，否则 `mean` 出 `NaN`，下一轮全盘崩。k-means++：第一个中心均匀抽，之后第 $j$ 个以正比于 $\min_{t<j}\lVert x-\mu_t\rVert^2$ 的概率抽，期望把初始代价压下来。不要把 ++ 写成「每个簇抽最远的那一个」——那是 greedy 的另一变种，最坏会被离群点带跑。

距离：欧氏和 k-means 的均值更新匹配。若数据是单位化 embedding，用 $2-2\cos$ 等价于欧氏；不要一边 cosine 赋值一边算术均值更新，均值会离开球面，这时该用 spherical k-means（均值再归一化）或换算法。

## 近邻：同一套距离，不同的题

「最近邻」有时是 k-means 的赋值（每个点找最近中心，其实是 $k$ 个原型上的 1-NN），有时是真的 $k$NN 分类 / 检索。

- **原型：** 推理只存 $k$ 个中心，$O(k d)$。这就是向量量化。Apple 端上 palettization：投影权按块做 k-means，$k=16$ 个中心对应 4-bit 码本，见 `apple-ondevice-quant`。面试把这句接上，coding 题就变成了公司题。
- **检索：** 私有消息 / 照片 embedding 的 top-k 邻居。精确 $O(n d)$；端上 $n$ 是用户自己的库，暴力扫往往够。需要更快再上 IVF（先 k-means 粗量化，再只扫近的几个倒排表）或图索引。不要一上来画分布式集群——和数据不出设备冲突，见 `apple-personalize`。
- **kNN vs k-means：** 分类题若 $n$ 小、决策边界不规则，kNN 更直接；要压缩模型或做码本，才是 k-means。说清任务，不要把两个 $k$ 混用。

评测：inertia（上式）只测紧致，不测下游。Palettization 要看恢复 adapter 之后的任务分；检索要看 recall@$k$ 和延迟。聚类没有唯一标签时，不要硬报 accuracy。

## ML 岗标准的口头清单

写完代码我会按这个顺序补，面试官通常会打断到其中一条：

1. 复杂度与何时改 mini-batch。
2. 初始化 / 空簇 / 局部最优，多 seed。
3. 和量化码本或端上检索的关系。
4. $k$ 怎么选：下游任务曲线，不是只看肘部。肘部在高维 embedding 上很钝。

时间不够就保 1 和 3。纯嵌套三层循环只在解释广播时当伪代码，最终要留下向量化版。采样题同一套「能跑 + 能接到产品」的标准，见 `apple-topk-sample`。

## 追问

- **和 GMM？** k-means 是等方、硬赋值的极限；要协方差或软赋值再上 EM。端上码本很少上满 GMM，贵。
- **Mini-batch 会不会不收敛？** 有噪声，用衰减学习率或最后几轮全量 polish。生产 palettization 往往离线多跑几次取恢复误差最低的码本。
- **高维距离失效？** 维数灾难让两两距离集中。先降维或用余弦加归一化；这也是为什么检索常用 trained embedding 而不是原始像素。
- **为什么电面爱出这题？** 短、可测数值、又能拐到量化。准备 20 行比再刷一道 hard 图更划算。

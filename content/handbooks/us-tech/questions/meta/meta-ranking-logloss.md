---
id: meta-ranking-logloss
section: meta
order: 14
level: A
title: Meta：为什么排序常盯 logloss / 校准而不只是 AUC
quick: >-
  AUC 只看正负样本谁排前，对分数做任意单调变换不变。Feed 的 $V=\sum w_k p_k$ 和广告的
  $bid\times pCTR$ 用的是概率的绝对大小。Logloss 是 proper scoring rule，校准差会直接改加权和与出价，AUC 可以纹丝不动。
tags:
  - Meta
  - Ranking
  - Logloss
  - Calibration
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: News Feed ranking, powered by machine learning
    url: https://engineering.fb.com/2021/01/26/ml-applications/news-feed-ranking/
    type: primary
  - title: Practical Lessons from Predicting Clicks on Ads at Facebook
    url: https://dl.acm.org/doi/10.1145/2648584.2648589
    type: primary
  - title: On Calibration of Modern Neural Networks
    url: https://arxiv.org/abs/1706.04599
    type: secondary
---

这题和 `meta-ads-calibration`、`meta-newsfeed-rank` 是同一类问题，但问法更「原则」：为什么排序组的看板不止 AUC。广告、Feed、推荐都会问。公开博客已经把 Feed 写成多头概率加权；广告论文把 logloss / NE 当核心离线指标。不要编造内部仪表盘名。

## AUC 看不见的东西

AUC 是随机一正一负，正样本分更高的概率。它只依赖**序**。任意严格单调变换 $g$，$g(s)$ 和 $s$ 的 AUC 相同。所以：

- 把所有 CTR 预测从 $[0.02, 0.08]$ 拉到 $[0.2, 0.8]$，AUC 可以不变，拍卖已经按十倍概率出价；
- 两个头 $p_{\mathrm{like}}$、$p_{\mathrm{hide}}$ 量纲漂了，加权 $V=\sum w_k p_k$ 的相对权重被静默改写，AUC 仍可能每头都在涨。

Feed 博客的合成是线性加权概率。权重 $w_k$ 是产品旋钮，假设 $\hat{p}_k$ 是校准过的。头 A 过度自信、头 B 保守，调 $w$ 就是在跟校准误差打架。完整性头如果只报 AUC「能分开违规」，但概率全挤在 $0.01$，你设的阈值 $0.2$ 永远不会触发。

广告更硬：期望价值用 $p$ 的绝对值。见 `meta-ads-calibration`。推荐 DLRM（`meta-dlrm`）同样用 logloss 训 CTR 头。

## Logloss 在罚什么

二元 logloss $\ell=-y\log p-(1-y)\log(1-p)$ 是 proper scoring rule：期望损失的最小值在 $p=\Pr(y=1\mid x)$。它同时讨厌：

- 排反（正样本给很低的 $p$）；
- 校准差（该给 $0.1$ 给 $0.5$）。

广告里常报 **normalized entropy**：logloss 除以用全局 CTR 当常数预测的 logloss。这样跨天、跨流量可以比。AUC 跨天也可以比，但 AUC 涨 + NE 恶化，是典型的「分更开了但更不像概率」。

校准图是 logloss 的可视化朋友：分组统计 $pred$ vs $obs$。ECE 是摘要，切片（新广告、新用户、位置）比全局 ECE 重要。Guo et al. 2017 说现代网容易过度自信，和深度 CTR 模型的现象一致，但面试用 Feed/广告的加权公式就够，不必把论文背完。

## 什么时候 AUC 仍要看

AUC 对**候选集里谁该排前**仍然有用，尤其是负样本抽样变了、绝对 $p$ 不可比的时候。检索阶段（Pass 0）有时更关心召回和序，不把分当概率用。精排和混排一旦进 $V$ 或进竞价，就必须盯 logloss / 校准。

位置偏差：用展示位置当特征，模型会把「靠前」写成高 $p$。AUC 在同一位置内仍可能很好，换到新槽位校准崩。要 IPS / 位置头 / 随机探索槽，这和 `meta-ab-peeking` 的实验纪律是一套：没有随机化，离线 AUC 和 logloss 都会撒谎，只是谎的方式不同。

错误答法：「logloss 对不平衡更稳。」不平衡时两个指标都要小心抽样。差别在 **概率绝对值进不进决策**。错误答法二：「校准了 AUC 自然会好。」常数预测校准完美，AUC $=0.5$。

## 怎么在面试里收口

我会说：离线主看 NE / logloss + 校准图，辅看 AUC；线上用 A/B 看时长、花费、完整度，不拿离线 AUC 决策全量。多头时每个头单独校准，再谈 $w_k$，否则权重实验在拟合校准漂移。

## 追问

- **多分类 / 多标签用什么？** 各头二元 logloss 或 softmax 交叉熵损失（CE），仍然是 proper。用 AUC 一对多只能看序。
- **校准会伤 AUC 吗？** 保序校准（isotonic 若严格单调）AUC 不变；分段乱校准可能伤序。先保序，再查切片。
- **为什么不直接优化 $V$ 的在线指标？** 在线指标方差大、延迟高。Logloss 是便宜的代理，但代理有效的前提是 $p$ 校准且标签定义和线上一致。
- **和完整度违规头？** 更要校准。阈值过滤吃的是绝对 $p$，不是 AUC。漏放成本不对称，阈值按代价定，不是 $0.5$。

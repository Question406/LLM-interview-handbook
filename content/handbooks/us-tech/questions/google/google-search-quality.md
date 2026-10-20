---
id: google-search-quality
section: google
order: 12
level: S
title: Google：搜索质量离线指标（NDCG）和线上行为怎么对不上
quick: >-
  NDCG 量的是「有标注的相关性是不是排在前面」；线上量的是点击、停留、任务完成。对不上通常是位置偏差、标注 ≠ 效用、按查询或按会话统计的差别，以及过度优化代理指标的 Goodhart 问题。别用「再训一个更大的 ranker」当第一句话。
tags:
  - Google
  - Search
  - NDCG
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Cumulated gain-based evaluation of IR techniques
    url: https://dl.acm.org/doi/10.1145/582415.582418
    type: primary
  - title: Rules of Machine Learning (Google Developers)
    url: https://developers.google.com/machine-learning/guides/rules-of-ml
    type: secondary
  - title: Unbiased Learning-to-Rank with Biased Feedback
    url: https://arxiv.org/abs/1608.04468
    type: primary
---

搜索 / 排序质量岗几乎必问：离线 NDCG 涨了，线上 CTR 或任务完成不动甚至掉。广告侧的校准故事见 `google-ads-auction`；推荐漏斗见 `google-youtube-rank`。

## NDCG 到底在积分什么

有一组查询，每个查询有人工 graded 相关性 $rel_i$（0–4 常见）。折损累计增益

$$
\mathrm{DCG}@k=\sum_{i=1}^{k}\frac{2^{rel_i}-1}{\log_2(i+1)},\qquad
\mathrm{NDCG}@k=\mathrm{DCG}@k/\mathrm{IDCG}@k
$$

IDCG 是同一组文档的理想排列。它对标注相关且排得靠前给高分。指数增益让「高度相关」远重于「勉强相关」。这是离线、可复现、可用于训练的代理指标。

它 不是：用户会不会点、点完会不会满足、第二条广告会不会挡住、会话里会不会改写查询。代理和产品目标之间有缝，缝就是对不上的来源。

## 为什么涨 NDCG、线上不涨

位置偏差。 用户从上往下看。第一条即使稍差也更常被点。标注员看的是独立 query-doc，或在固定 SERP 里打分；模型若用点击当标签，会把「排在上面」学成「相关」。离线 NDCG 用人工级，线上 CTR 被位置污染，两者可以反向。纠偏：随机化 / 插页、IPS、位置作为特征但训练时对齐。Joachims 那条线：有偏反馈不能当无偏相关。

标注 ≠ 效用。 评级定义是「这个页满足查询吗」。用户要的可能是新鲜、本地、多样性、一条就能完成任务。把三篇同质高相关全排前面，NDCG 很高，用户却只看到同质的重复内容。多样性、新鲜度、权威性经常在重排，不在 NDCG 的标注协议里。

查询级 vs 会话级。 NDCG 按单次查询平均。线上要看：有没有二次搜索、有没有长停留、任务是否结束。一个改写查询在离线是两条独立 query，线上是同一次失败。

切片和漂移。 评测集是旧查询、旧文档、旧意图（疫情、选举、新 app）。线上是今天的分布。整体 NDCG +0.2% 可能来自头部导航查询，尾部信息查询在掉。应按头部、中部、尾部查询，以及国家和设备分组分析，再看线上。

Goodhart。 模型直接对着 NDCG 或点击优化久了，开始刷标注协议和点击诱饵。离线更好、用户更烦。Rules of ML 反复说：不要把代理指标当成目标本身。

呈现。 标题、摘要、视频大卡改变点击，不改变静态相关性分。NDCG 的文档集合若不含「这条结果长什么样」，线上必然分叉。

## 面试怎么收

先承认 NDCG 仍要用：没标注就没法离线迭代，A/B 太贵。然后说 决策规则：上线门槛是线上实验（或交错评估），NDCG 是门禁和调试器。两者冲突时，查偏差和切片，而不是加模型宽度。

交错（interleaving）把两个 ranker 混在同一页，比 NDCG 更接近线上、比全量 A/B 便宜。校准点击模型、用停留 / 长点击当效用，比再堆一层 Transformer 先做。

常见误区是：说「NDCG 没用了」；说「线上 CTR 就是质量」；把搜索质量答成推荐 CTR。搜索有明确查询意图，会话成功比点击更接近产品。

## 追问

- **NDCG 用 $2^{\mathrm{rel}}$ 还是线性增益？** 指数把满分文档和「还行」拉开。导航查询往往只要那一个满分 URL，线性增益会低估排错的代价。
- **没有标注怎么办？** 行为当弱监督必须纠偏；主动学习抽冲突 query 给人工。不要用原始 CTR 当 graded label。
- **和广告质量同分吗？** 搜索 NDCG 是相关性；广告还要 pCTR 校准和拍卖。混在一个分里会让商业结果挤掉信息结果。广告见 `google-ads-auction`。
- **离线涨 1% 该不该全量？** 先看切片、延迟、多样性、人工抽查，再小流量。上线门槛不能只看一个 NDCG 数字。

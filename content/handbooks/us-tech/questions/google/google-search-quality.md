---
id: google-search-quality
section: google
order: 12
level: S
title: Google：搜索质量离线指标（NDCG）和线上行为怎么对不上
quick: >-
  NDCG 衡量有人工相关性标注的文档是否排在前面，线上还受点击位置、呈现和会话体验影响。两者对不上时，我会先按查询和用户群切片，检查 position
  bias、标注是否覆盖效用，以及评测分布是否过时，再用小流量实验判断上线。
tags:
  - Google
  - Search
  - NDCG
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Cumulated gain-based evaluation of IR techniques
    url: 'https://dl.acm.org/doi/10.1145/582415.582418'
    type: primary
  - title: Rules of Machine Learning (Google Developers)
    url: 'https://developers.google.com/machine-learning/guides/rules-of-ml'
    type: secondary
  - title: Unbiased Learning-to-Rank with Biased Feedback
    url: 'https://arxiv.org/abs/1608.04468'
    type: primary
---

离线 NDCG 涨、线上表现不涨时，我会先检查两者到底在衡量什么，再查 position bias 和分布切片。比如把三篇高度相关但内容重复的页面排在前面，NDCG 可以很高，用户却没有更快完成任务。广告侧的 calibration 见 `google-ads-auction`，推荐漏斗见 `google-youtube-rank`。

有一组查询，每个查询有人工 graded 相关性 $rel_i$（0–4 常见）。折损累计增益

$$
\mathrm{DCG}@k=\sum_{i=1}^{k}\frac{2^{rel_i}-1}{\log_2(i+1)},\qquad
\mathrm{NDCG}@k=\mathrm{DCG}@k/\mathrm{IDCG}@k
$$

IDCG 是同一组文档的理想排列。它对标注相关且排得靠前给高分。指数增益让「高度相关」远重于「勉强相关」。这是离线、可复现、可用于训练的代理指标。

这个分数没有直接测用户会不会点、点完是否满足、页面广告是否遮挡，以及会话里是否改写查询。这些差别都可能让离线分数和线上表现分开变化。

先看 position bias。用户从上往下看。第一条即使稍差也更常被点。标注员看的是独立 query-doc，或在固定 SERP 里打分；模型若用点击当标签，会把「排在上面」学成「相关」。离线 NDCG 用人工级，线上 CTR 被位置污染，两者可以反向。纠偏：随机化 / 插页、IPS、位置作为特征但训练时对齐。Joachims 那条线：有偏反馈不能当无偏相关。

再看标注与实际效用是否一致。评级定义是「这个页满足查询吗」。用户要的可能是新鲜、本地、多样性、一条就能完成任务。把三篇同质高相关全排前面，NDCG 很高，用户却只看到同质的重复内容。多样性、新鲜度、权威性经常在重排，不在 NDCG 的标注协议里。

统计单位也要对齐。NDCG 按单次查询平均。线上要看：有没有二次搜索、有没有长停留、任务是否结束。一个改写查询在离线是两条独立 query，线上是同一次失败。

还要检查切片和分布漂移。评测集是旧查询、旧文档、旧意图（疫情、选举、新 app）。线上是今天的分布。整体 NDCG +0.2% 可能来自头部导航查询，尾部信息查询在掉。应按头部、中部、尾部查询，以及国家和设备分组分析，再看线上。

长期直接对着 NDCG 或点击优化时，可能出现 Goodhart 问题：开始刷标注协议和点击诱饵。离线更好、用户更烦。Rules of ML 反复说：不要把代理指标当成目标本身。

页面呈现也会影响结果。标题、摘要、视频大卡改变点击，不改变静态相关性分。NDCG 的文档集合若不含「这条结果长什么样」，线上必然分叉。

先承认 NDCG 仍要用：没标注就没法离线迭代，A/B 太贵。我的决策规则是：release criteria 是线上实验（或交错评估），NDCG 是 acceptance checks 和调试器。两者冲突时，查偏差和切片，而不是加模型宽度。

交错（interleaving）把两个 ranker 混在同一页，比 NDCG 更接近线上、比全量 A/B 便宜。calibration 点击模型、用停留 / 长点击当效用，比再堆一层 Transformer 先做。

常见误区是：说「NDCG 没用了」；说「线上 CTR 就是质量」；把搜索质量答成推荐 CTR。搜索有明确查询意图，会话成功比点击更接近产品。

## 追问

**NDCG 用 $2^{\mathrm{rel}}$ 还是线性增益？**
指数把满分文档和「还行」拉开。导航查询往往只要那一个满分 URL，线性增益会低估排错的代价。

**没有标注怎么办？**
行为当弱监督必须纠偏；主动学习抽冲突 query 给人工。不要用原始 CTR 当 graded label。

**和广告质量同分吗？**
搜索 NDCG 是相关性；广告还要 pCTR calibration 和拍卖。混在一个分里会让商业结果挤掉信息结果。广告见 `google-ads-auction`。

**离线涨 1% 该不该全量？**
先看切片、延迟、多样性、人工抽查，再小流量。release criteria 不能只看一个 NDCG 数字。

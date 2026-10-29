---
id: ml101-ranking-metrics
section: metrics
order: 8
level: A
title: Precision@K、Recall@K、MAP 和 NDCG 怎么选？
quick: >-
  只关心前 K 个里有多少可用结果，看 Precision@K；关心找全多少相关结果，看 Recall@K。MAP 用二元相关性奖励相关结果靠前，NDCG
  可处理多级相关性并折扣靠后位置；所有指标都要说明候选集、截断和无相关结果时的规则。
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'TensorFlow Ranking: MeanAveragePrecisionMetric'
    url: >-
      https://www.tensorflow.org/ranking/api_docs/python/tfr/keras/metrics/MeanAveragePrecisionMetric
    type: primary
  - title: 'scikit-learn: ndcg_score'
    url: >-
      https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html
    type: primary
---

先按用户怎样消费结果选指标。前 K 个位置是否够准，用 Precision@K；检索阶段有没有把需要的结果找回来，用 Recall@K；二元相关性下想综合奖励靠前命中，可以用 MAP；相关程度有高低、位置价值也不同，则用 NDCG。TensorFlow Ranking 给出 MAP 的定义，scikit-learn 的 NDCG 则明确用位置折扣和理想排序 normalization。[TensorFlow Ranking: MeanAveragePrecisionMetric](https://www.tensorflow.org/ranking/api_docs/python/tfr/keras/metrics/MeanAveragePrecisionMetric)、[scikit-learn: ndcg_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html)。

设前 K 个结果中有 $h$ 个相关，全部相关结果共有 $R$ 个，那么 Precision@K 是 $h/K$，Recall@K 是 $h/R$。同一个命中数，前者问展示位置浪费了多少，后者问应该找的结果漏了多少。例如相关文档共 10 篇，前 5 个找到 3 篇，Precision@5 为 0.6，Recall@5 为 0.3。

对一个查询，AP 会在每个相关结果出现的位置取当时的 precision，再除以全部相关结果数；MAP 再对查询的 AP 平均。因此相关结果越早出现通常越好。计算截断版本时，需要写清只累加到 K 还是还改了分母，避免名字相同、实现不同。

NDCG 给各位置的非负相关收益打折，再除以同一候选集的理想排序得分。例如采用线性收益 $g_i$ 时：

$$
\mathrm{DCG}@K=\sum_{i=1}^{K}\frac{g_i}{\log_2(i+1)},\qquad
\mathrm{NDCG}@K=\frac{\mathrm{DCG}@K}{\mathrm{IDCG}@K}.
$$

这样「非常相关」排在第一位与第五位会有不同贡献。收益也可另作变换，报告中要注明；候选集或相关性标注改变后，分数不能直接横比。

## 追问

**没有任何相关结果的查询怎么算？**
分母可能为零，应提前规定记零、单独统计或排除的规则，并报告此类查询比例。不能在看到模型结果后再选择有利定义。

**只标过曝光结果，Recall@K 可靠吗？**
不一定。未曝光结果的相关性未知，真实分母可能缺失。要说明标注覆盖与候选池，必要时补充 pooling 评审或其他验证。

**前 K 个命中数相同，排序就一样好吗？**
不是。Precision@K 不区分 K 个位置内部的顺序，AP 和 NDCG 会奖励更早的相关命中，因此还要看用户对位置是否敏感。

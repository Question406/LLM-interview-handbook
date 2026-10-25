---
id: ml101-fairness-slices
section: metrics
order: 11
level: A
title: "为什么总体指标提高，某个人群表现却变差？"
quick: "总体指标把人群按样本权重混在一起，多数人群的收益可能盖住少数人群的退化。先按有业务意义的人群及交叉切片看样本数、错误类型和不确定性，再检查数据覆盖、标签与阈值；公平性目标需要结合具体任务定义。"
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Google ML Crash Course: Evaluating for bias"
    url: https://developers.google.com/machine-learning/crash-course/fairness/evaluating-for-bias
    type: primary
  - title: "Fairlearn: MetricFrame"
    url: https://fairlearn.org/main/api_reference/generated/fairlearn.metrics.MetricFrame.html
    type: primary
---

总体平均值会把不同人群混在一起，所以总分上涨并不保证每组都变好。多数群体的改善足够大，就可能掩盖少数群体的明显退化。Google 的公平性课程提醒，汇总 precision、recall 或 accuracy 不足以暴露少数子集的问题。[Google ML Crash Course: Evaluating for bias](https://developers.google.com/machine-learning/crash-course/fairness/evaluating-for-bias)。

例如一个示意测试集有 900 个多数群体样本和 100 个少数群体样本。旧模型两组准确率分别为 90% 和 80%，总体是 89%；新模型变成 95% 和 60%，总体却提高到 91.5%。少数群体少对了 20 个，多数群体多对了 45 个，平均值只显示净增。

我会保留总体结果，再按地区、语言、设备或相关人口属性检查各组样本数、漏报与误报；必要时看交叉切片，例如某地区中的某种语言。Fairlearn 的 MetricFrame 就提供整体和分组指标的并列结果，方便比较差异。[Fairlearn: MetricFrame](https://fairlearn.org/main/api_reference/generated/fairlearn.metrics.MetricFrame.html)。小切片的比例很容易波动，要同时看计数和不确定性。

接着查训练数据是否覆盖不足、标签规则是否对不同组不一致、输入质量是否不同，以及同一个决策阈值造成了怎样的错误分配。明确需要保护的结果之后，再评估补数据、改善特征、调整目标或决策流程，不能只把总分优化得更高。

## 追问

**各组 accuracy 一样，就公平了吗？**
不能据此下结论。组内正例比例不同，accuracy 相同仍可能伴随不同的漏报、误报或获益机会，必须结合实际伤害选择评估维度。

**把敏感属性从特征中删除，就能消除差异吗？**
不保证。其他变量可能与它相关，标签和数据覆盖也可能有偏差。即使模型不读取该属性，评估时仍要在有权限、合适的条件下检查群体差异。

**小群体样本太少怎么办？**
优先补充有代表性的评估样本，同时报告计数和较大的不确定性。不要把一次偶然高分当成已解决，也不要因样本少就完全不检查。

**所有公平性指标都能同时最优吗？**
通常不能保证。不同指标表达不同的价值与统计要求，可能发生冲突；需要先说明任务中的错误代价和希望保障的机会，再透明地报告取舍。

---
id: ml101-robust-regression
section: linear-models
order: 10
level: A
title: "Huber 回归和分位数回归适合什么问题？"
quick: "Huber 适合少量大残差会扭曲平方损失的回归，在小残差处用平方、大残差处改成线性增长。分位数回归则直接预测给定特征下的中位数或其他分位数，用不对称 pinball loss 表达高估、低估的不同代价。两者要按目标选择，不能因为都较稳健就互相替代。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: HuberRegressor"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html
    type: primary
  - title: "scikit-learn: QuantileRegressor"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.QuantileRegressor.html
    type: primary
---

Huber 主要减轻大残差的影响，分位数回归主要改变要预测的统计量。先问业务要一个稳健的中心趋势，还是想知道高分位的等待时间，再选损失。

Huber 在残差较小时像平方误差，较大时只线性增长，大错误仍影响拟合，却不会随残差平方迅速放大。它适合标签里偶尔出现极端偏离的情形，但不保证处理好所有高杠杆特征异常。[HuberRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html) 的实现还会估计残差尺度。

分位数回归对残差 $r=y-\hat y$ 使用 $\rho_\tau(r)=\max(\tau r,(\tau-1)r)$。取 $\tau=0.9$ 时，低估的单位代价更大，拟合条件 90% 分位数；取 0.5 则是条件中位数。比如配送时间多数很短、偶尔很长，承诺时限可以预测高分位，而平均耗时是另一个目标。定义见 [QuantileRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.QuantileRegressor.html)。

## 追问

**预测 90% 分位数能保证每个订单都覆盖吗？**
不能。分位数描述条件分布的位置，模型错误或分布变化也会影响覆盖，需要在留出数据和关键分组上检验。

**Huber 会自动删除离群点吗？**
不会。大残差仍有影响，只是增长更慢；还应先查离群值是数据错误还是有效的罕见事件。

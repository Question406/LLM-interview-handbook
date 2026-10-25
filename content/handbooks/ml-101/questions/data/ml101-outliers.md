---
id: ml101-outliers
section: data
order: 8
level: A
title: "异常值怎么识别和处理？"
quick: "先判断异常值是采集错误、真实极端事件，还是分布变化，再决定修正、保留或限制其影响。单变量可看分位数和稳健尺度，多变量可用异常检测辅助排查；阈值在训练数据上确定，不能为了提高测试分数删掉难样本。"
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Novelty and Outlier Detection"
    url: https://scikit-learn.org/stable/modules/outlier_detection.html
    type: primary
  - title: "scikit-learn: Preprocessing data"
    url: https://scikit-learn.org/stable/modules/preprocessing.html
    type: primary
---

异常值先当成待调查记录，再决定怎么处理。极端取值可能是单位错误，也可能是真实的大客户或新出现的行为；它们需要不同动作。异常检测方法通常寻找偏离主要数据区域的点，并不直接证明这些点是错误数据。scikit-learn 也区分了训练集中寻找离群点，和在相对干净的训练数据之外检测新颖样本。[scikit-learn: Novelty and Outlier Detection](https://scikit-learn.org/stable/modules/outlier_detection.html)。

我会先检查字段含义、合法范围、缺失编码和数据来源，再按群组画分布。单变量可以用分位数、箱线图或中位数附近的稳健尺度定位候选；多变量可以结合距离、Isolation Forest 等方法找出单列不显眼但组合异常的记录。检测分数只用于安排检查优先级。

比如订单金额突然很大，要先看是否把「分」当成「元」、是否重复入账。如果确认是正常的大额订单，删除它会改变目标人群；可以保留原值，考虑变换、分组建模或对极端误差较稳健的损失。用中位数和分位距做缩放能降低少量极端值对尺度的影响，预处理指南介绍了这种稳健缩放。[scikit-learn: Preprocessing data](https://scikit-learn.org/stable/modules/preprocessing.html)。

真正的错误能修就按源记录修，无法确认时保留标记。截尾或分位数阈值要只在训练集确定，并把同一规则用于验证和上线，同时单独检查尾部样本的表现。

## 追问

**超过三个标准差就删除，可以吗？**
不能直接这样做。阈值是否合理取决于分布，重尾数据本来就有极端值，而且均值、标准差自身也可能受异常影响。

**异常值就是异常标签吗？**
不是。特征极端和标签错误是两个问题；真实欺诈可能特征异常，正常大额交易也可能特征异常，需要结合任务和源数据判断。

**测试集中出现训练时没见过的极端值呢？**
先用预先确定的规则处理并记录，不根据测试标签临时删样本。随后调查是合法尾部还是漂移，必要时补充有代表性的训练与评测数据。

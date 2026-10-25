---
id: ml101-imbalance
section: metrics
order: 3
level: S
title: "类别极不均衡时怎么训练和评价？"
quick: "先保留符合线上比例的独立评估集，用 PR、正类召回和误报成本评价，再考虑类别加权、训练集重采样或调整阈值。重采样必须限制在训练折内，并检查它是否改变概率校准；正例少时也要先确认标签质量和覆盖范围。"
tags:
  - Machine Learning
  - metrics
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Google ML Crash Course: Accuracy, recall, precision"
    url: https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall
    type: primary
  - title: "scikit-learn: Probability calibration"
    url: https://scikit-learn.org/stable/modules/calibration.html
    type: primary
---

类别不均衡时，我会先明确真正想找的少数类以及误报和漏报的成本。全预测多数类就可能得到很高准确率，因此先建立符合真实比例的评估集和简单基线。

例如一万笔交易只有十笔风险交易，我会看能找回几笔、需要审核多少笔，以及置信区间有多宽。十笔正例太少，一笔变化就会明显改变召回，收集可信标签可能比反复调参数更有价值。

训练阶段可以给少数类更高权重，或对多数类下采样，减少它们在目标中的支配；再在验证集上选择阈值。复制少数类不会增加独立信息。若使用合成或重采样，必须在每个训练折内部做，防止原样本与衍生样本同时出现在训练和验证两侧。

加权和采样会改变模型学习的分布或损失偏好。预测分数要当作真实概率使用时，应在保留真实比例的数据上核验并按需校准。

## 面试追问

**只调整阈值就够了吗？**
排序已经很好时，阈值调整可能足够；模型根本没有区分少数类的能力时，改变阈值无法创造信息，需要改数据、特征或训练目标。

**测试集要不要也采样成一比一？**
通常保留实际分布。人为平衡会改变精确率和实际成本的估计；若因采集成本使用抽样测试，应记录采样概率并采用相应加权。

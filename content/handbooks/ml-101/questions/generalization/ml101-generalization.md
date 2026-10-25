---
id: ml101-generalization
section: generalization
order: 7
level: S
title: "什么是泛化？训练误差低为什么还不够？"
quick: "泛化是模型在没见过、且与实际使用条件相符的数据上仍能预测准确。训练误差低只说明模型拟合了手里的样本；要用独立留出的数据估计新样本误差，并确认切分方式接近上线场景。"
tags:
  - Machine Learning
  - generalization
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Cross-validation"
    url: https://scikit-learn.org/stable/modules/cross_validation.html
    type: primary
  - title: "scikit-learn: Common pitfalls and recommended practices"
    url: https://scikit-learn.org/stable/common_pitfalls.html
    type: primary
---

泛化就是模型换一批新样本后还好用。训练时已经用标签调整过参数，训练分数会偏乐观，因此我会在没有参与拟合和选择模型的数据上评价它。

比如用过去三个月订单预测下月取消率。模型记住某几笔订单的编号，也能把训练误差做到很低，但新订单的编号没有对应规律。用下个月数据验证，才更接近要解决的问题。

独立测试还依赖评估对象。随机切分估计的是相近分布的新样本效果；用户重复出现、时间变化或采集渠道变化时，应该按用户、时间或渠道设计切分。最后报告具体指标和样本范围，让人知道这个结论适用于哪一批数据。

## 面试追问

**训练误差为零就说明过拟合了吗？**
不一定。任务简单、标签规律明确时，零训练误差也可能泛化良好。要结合独立数据上的误差以及数据是否泄漏判断。

**测试集很小会有什么问题？**
结果会有较大抽样波动。可以增加独立测试样本，或在开发阶段用适当交叉验证估计波动；反复查看同一小测试集再改模型会进一步使估计偏乐观。

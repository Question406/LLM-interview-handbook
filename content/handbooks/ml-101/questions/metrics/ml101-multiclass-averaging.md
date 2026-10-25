---
id: ml101-multiclass-averaging
section: metrics
order: 6
level: A
title: "多分类的 macro、micro 和 weighted 指标有什么区别？"
quick: "Macro 先按类别算指标再等权平均，micro 汇总所有类别的 TP、FP、FN 后计算，weighted 按各类真实样本数加权平均。类别不均衡时它们回答的问题不同，报告平均分时也要保留每类结果和样本数。"
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: precision_recall_fscore_support"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html
    type: primary
---

Macro 给每个类别相同权重，micro 给所有预测决策一起记账，weighted 则让真实样本多的类别占更大权重。选哪种取决于想保护每个类别，还是想概括当前流量下的总体表现。scikit-learn 对这些平均方式的定义以逐类指标和真实支持数为基础。[scikit-learn: precision_recall_fscore_support](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html)。

先把每一类当作「本类对其他类」，分别计算 TP、FP、FN。Macro 再对各类 precision、recall 或 F1 等权平均；weighted 用该类真实样本占比作权重。Micro 先把 TP、FP、FN 跨类相加，再代入指标公式，所以并不是逐类 F1 的平均。

比如 900 个常见类样本、100 个少数类样本，模型全部预测成常见类。两类 recall 分别是 1 和 0，macro recall 是 0.5，weighted recall 是 0.9；单标签且统计全部类别时，micro precision、recall 和 F1 也都等于 accuracy，也就是 0.9。只看后面的数，会掩盖少数类完全没召回。

我会先按实际任务选择主要指标，再同时展示类别支持数和错误类型。Macro 更容易暴露少数类问题，但小类别的估计也更不稳定；weighted 的高分则不能替代对重要少数类的单独验收。

## 追问

**Macro F1 等于 macro precision 和 macro recall 的调和平均吗？**
通常不等于。Macro F1 是先算每类 F1 再平均，非线性运算的顺序不同，结果也可能不同。

**Weighted F1 一定在加权 precision 与 recall 之间吗？**
不一定。它是各类 F1 的加权平均，不是从两个已加权的均值再算 F1，scikit-learn 也特别提醒了这一点。

**某类没有预测样本，precision 怎么算？**
分母为零，需要事先规定处理方式，例如记零或标为未定义，同时报告支持数。不要让不同实现的默认值悄悄改变平均分。

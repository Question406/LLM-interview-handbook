---
id: ml101-threshold
section: metrics
order: 4
level: S
title: "分类阈值为什么不一定是 0.5？"
quick: "0.5 适合把校准概率用于误报、漏报代价对称的简单二分类。实际阈值要按业务成本、审核容量或召回约束，在独立验证数据上选择；改变阈值会改变分类结果，但不改变原始分数的排序。"
tags:
  - Machine Learning
  - metrics
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Tuning the decision threshold"
    url: https://scikit-learn.org/stable/modules/classification_threshold.html
    type: primary
---

阈值把预测分数变成行动，应该由行动成本决定。比如同样是 20% 风险概率，人工复核一次很便宜时可能值得检查，直接拒绝一位正常用户很贵时就需要更谨慎。

设模型给出的真实正类概率为 $p$，误报成本为 $C_{FP}$，漏报成本为 $C_{FN}$，正确判断成本取零。判正的期望成本是 $C_{FP}(1-p)$，判负的期望成本是 $C_{FN}p$。比较两者，最优规则是：

$$p>\frac{C_{FP}}{C_{FP}+C_{FN}}.$$

例如漏报成本为 9、误报成本为 1，阈值是 0.1。这个推导要求概率适合当前人群，成本也能由这两个常数描述。若每天只能复核一百笔，就还要把容量约束加入选择，可能按当天分数选前一百笔。

实际会在验证数据上画出阈值与收益、误报、召回的关系，再冻结规则到测试集评价。

## 面试追问

**调阈值会提高 ROC-AUC 吗？**
不会。原始连续分数的 AUC 不变。把分数先变成零一标签再计算 AUC，会丢失排序信息，不能用来比较原始排序能力。

**阈值能长期固定吗？**
要监测。人群、正类比例、成本和容量变化都可能使旧阈值不再合适；更新阈值也需要新的验证数据，不能根据当日测试结果反复试。

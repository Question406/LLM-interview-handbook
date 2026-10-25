---
id: ml101-roc-pr
section: metrics
order: 2
level: S
title: "ROC-AUC 和 PR 曲线分别衡量什么？"
quick: "ROC 曲线比较不同阈值下的真正率与假正率，AUC 描述整体排序能力；PR 曲线比较精确率与召回率，更容易看出少数正类被大量误报淹没的情况。正类比例很低时，我会重点看 PR、具体阈值的误报量和召回。"
tags:
  - Machine Learning
  - metrics
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Google ML Crash Course: ROC and AUC"
    url: https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc
    type: primary
  - title: "scikit-learn: Metrics and scoring"
    url: https://scikit-learn.org/stable/modules/model_evaluation.html
    type: primary
---

ROC-AUC 适合观察分数能否把正样本排在负样本前面，PR 更直接反映找回正类时需要接受多少误报。两者回答的问题不同，实际还要回到可用阈值。

假设有 100 个正例、99,900 个负例。某阈值召回 80 个正例，同时误报 999 个负例，真正率是 80%，假正率是 1%，但精确率只有 $80/(80+999)\approx7.4\%$。这个例子说明，低假正率在巨大负类基数下仍会产生很多误报。

对随机抽取的一对正负样本，ROC-AUC 可以解释为正例分数更高的概率，平分按一半计。它不要求分数是概率，也不能保证高分区域恰好满足业务要求。PR 的汇总要注明计算方式：Average Precision 按召回增量加权精确率，与梯形积分得到的 PR 面积可能不同。

## 面试追问

**正类比例变化会影响指标吗？**
PR 对正类比例敏感。若只改变正负混合比例、类内分数分布保持不变，ROC 可以不变，但精确率会变化；现实中类内分布也可能一起变化。

**AUC 高就代表上线效果好吗？**
不代表。业务可能只允许极少误报，整体 AUC 没有专门优化这个区间。应比较固定误报预算下的召回，或固定审核容量下的精确率。

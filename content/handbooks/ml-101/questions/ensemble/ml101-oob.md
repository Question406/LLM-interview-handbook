---
id: ml101-oob
section: ensemble
order: 6
level: A
title: "袋外 OOB 估计是怎么来的？能替代所有验证吗？"
quick: "袋外估计（OOB）利用每棵树 bootstrap 时没抽到的样本做预测，再为每个样本汇总所有没见过它的树，估计泛化误差。它节省一次单独划分，但不是时间外推、分组泛化或反复调参后的独立测试。预处理若已经看过全体数据，也可能让 OOB 过于乐观。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: RandomForestClassifier, OOB estimates"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
    type: primary
---

袋外估计（OOB）是有放回抽样 bootstrap 自带的一种验证机会：一棵树训练时没有见到的样本，可以交给它预测。对每个训练样本，只汇总把它留在袋外的树，再把这些预测与真实标签比较。

从 n 个样本中有放回抽 n 次，某样本一次都没抽到的概率是 $(1-1/n)^n$，样本多时约为 $e^{-1}$。不同树遗漏不同样本，所以一个样本通常有多棵可用树。例如样本 A 出现在树 1 的训练集中、没出现在树 2 和 3 中，A 的 OOB 预测只能用后两棵。

它适合快速监测带 bootstrap 的森林，但仍遵守任务的数据独立性。若同一用户的其他记录进了树，OOB 并不等于从未见过这个用户；时间任务也需要向未来验证。调参反复选择最好的 OOB 后，还应留独立测试集。实现和样本过少时的限制见 [RandomForestClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)。

## 追问

**为什么不能用所有树预测训练样本再评估？**
其中很多树见过该样本，尤其深树可能已经记住它，会让误差过小。

**树很少时 OOB 靠谱吗？**
可能不稳定，甚至某个样本一次都没被留出。先检查有效 OOB 预测覆盖，再增加树数观察估计是否稳定。

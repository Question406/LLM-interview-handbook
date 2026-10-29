---
id: ml101-group-time-split
section: data
order: 4
level: S
title: 什么情况下不能随机切分数据？
quick: >-
  样本有时间顺序或共享实体时，随机切分可能高估效果。预测未来就按时间回测，预测新用户或新患者就按实体分组切分；切分方式要回答实际部署的泛化问题，必要时在
  time boundaries 留出间隔。
tags:
  - Machine Learning
  - data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'scikit-learn: Cross-validation'
    url: 'https://scikit-learn.org/stable/modules/cross_validation.html'
    type: primary
---

当样本之间存在联系，或预测必须面对未来时，我会按联系和时间切分。随机切分适合相对独立、同分布的新样本，无法自动模拟所有上线场景。

例如一个患者有十次检查记录，随机分到两侧后，模型可能识别患者特征。如果部署对象是新患者，就应该按患者分组。若部署对象包含老患者，但要预测他们未来的情况，则更适合使用 time-based split，同时限制历史特征只使用当时已知记录。

时间回测可以逐步向前滚动：早期数据训练，后面的窗口验证。标签需要观察未来七天才形成时，要检查训练标签的观察窗口是否跨入验证时期；按任务设置间隔，避免未来结果进入训练。不同窗口都报告指标，可以看出模型是否只在某一时期有效。

## 面试追问

**分层抽样能解决用户泄漏吗？**
不能。分层只维持类别比例，分组才控制同一实体不跨集合。必要时选同时考虑类别比例与分组的方案。

**时间验证里类别比例变了怎么办？**
保留这种变化并单独解释，因为它可能正是上线要面对的情形。可以报告各时间段表现和样本数，避免人为均衡后掩盖真实困难。

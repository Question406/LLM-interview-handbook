---
id: ml101-model-choice
section: diagnosis
order: 3
level: S
title: "面对一个新的表格预测任务，怎么建立基线和选择模型？"
quick: "先定义预测对象、预测时点、标签和业务成本，再建立合理切分与简单基线。通常比较常数预测、正则线性模型和树模型，用同一验证流程检查效果、延迟与稳定性；错误分析决定下一步补数据、做特征还是加模型复杂度。"
tags:
  - Machine Learning
  - diagnosis
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Cross-validation"
    url: https://scikit-learn.org/stable/modules/cross_validation.html
    type: primary
  - title: "scikit-learn: Ensembles"
    url: https://scikit-learn.org/stable/modules/ensemble.html
    type: primary
---

我会先把任务和可用信息定清楚，再选模型。明确在什么时候为谁预测什么，才能知道哪些特征可以用、怎样切分，以及用什么指标评价。

例如预测新订单七天内取消，先固定七天的标签观察窗口，特征只使用下单预测时点已经可得的字段，七天观察窗只用于形成标签，并按时间留出后续订单。先跑总报平均取消率的常数概率基线，再做带正则的逻辑回归和一类树模型，所有预处理都放进同一验证流程。

比较时除了主指标，也看概率质量、重要分群和服务成本。线性模型训练和解释简单；树模型能自动学习一些非线性和交互，但也要控制复杂度。选择验证表现可靠、满足实际约束的方案，无需预先认定某类模型必胜。

然后抽看错误样本。若主要是标签错或关键字段缺失，换更复杂的模型帮助有限；若明显存在当前特征无法表达的交互，可以改特征或模型。方案确定后冻结参数和阈值，在最终测试集评价。

## 面试追问

**什么时候值得引入复杂模型？**
简单基线已经可靠、验证中的错误确实与表达能力有关，并且额外效果能覆盖训练、推理与维护成本时。最好用同一切分做增量比较。

**怎么避免试了很多模型之后挑到偶然赢家？**
保留最终独立测试数据，开发阶段记录试验并关注差异的不确定性。搜索很多方案时，可以用嵌套验证评价完整选择流程。

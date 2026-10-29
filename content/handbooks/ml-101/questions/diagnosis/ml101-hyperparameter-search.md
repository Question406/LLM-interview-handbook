---
id: "ml101-hyperparameter-search"
section: "diagnosis"
order: 5
level: "A"
title: "网格搜索、随机搜索和贝叶斯优化怎么选？"
quick: "参数少且候选明确时用网格搜索；空间较大、预算固定时先随机搜索；单次训练昂贵且能利用历史结果时考虑贝叶斯优化。三者都只在训练与验证部分选参数，测试集留到最终评估。"
tags: ["ML101", "diagnosis"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "scikit-learn: Tuning hyperparameters"
    url: https://scikit-learn.org/stable/modules/grid_search.html
    type: primary
  - title: "Practical Bayesian Optimization of Machine Learning Algorithms"
    url: https://arxiv.org/abs/1206.2944
    type: primary
---

我会按搜索空间和单次训练成本选择方法。网格搜索枚举指定组合，适合少数有明确候选的参数；随机搜索从给定分布抽样，预算可直接控制，也能避免对每个不重要维度都铺满网格。 [scikit-learn: Tuning hyperparameters](https://scikit-learn.org/stable/modules/grid_search.html)

贝叶斯优化用已经评估的参数与分数拟合代理模型，再用采集规则决定下一次试哪里，在探索不确定区域与利用好区域之间取舍。训练昂贵时它可能省试验，但代理模型和调度也有成本，不能保证每个任务都优于随机搜索。 [Practical Bayesian Optimization of Machine Learning Algorithms](https://arxiv.org/abs/1206.2944)

例如先调学习率和正则强度，可以在对数尺度随机取值；发现有效范围后再细化。若每次训练很久，就让贝叶斯优化利用这些历史结果。所有候选使用同一评价协议，交叉验证中的预处理也只在训练折拟合，并记录耗时、随机种子和试验配置。

## 追问

**为什么学习率常在对数尺度搜索？**
因为重要差别常是数量级。在线性区间均匀抽样，容易把预算都花在较大数值附近。

**找到验证最优后直接报分吗？**
频繁搜索会对验证集 overfitting，需要独立测试集；数据紧张时可以用嵌套交叉验证估计选择过程的表现。

**并行越多越适合贝叶斯优化吗？**
不一定。大量试验同时发出时，后来的决策暂时用不到还未结束的结果，需要专门的批量或异步策略。

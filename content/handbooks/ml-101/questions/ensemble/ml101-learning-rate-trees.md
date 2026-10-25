---
id: ml101-learning-rate-trees
section: ensemble
order: 8
level: A
title: "提升树的学习率、树数和树深怎样配合？"
quick: "学习率决定每棵树对总预测贡献多大，树数决定加多少步，树深决定每步能拟合多复杂的交互。降低学习率通常要增加树数，深树则更容易贴近复杂结构也更容易过拟合。用验证曲线与早停一起选择，训练时间和推理成本也要纳入取舍。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: GradientBoostingRegressor"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingRegressor.html
    type: primary
  - title: "scikit-learn: Early stopping in Gradient Boosting"
    url: https://scikit-learn.org/stable/auto_examples/ensemble/plot_gradient_boosting_early_stopping.html
    type: primary
---

提升树的学习率、树数和深度要一起调：一个控制步长，一个控制走几步，一个控制每步模型有多复杂。单独降低学习率、树数却不变，可能只是让模型没学够。

模型逐轮更新为 $F_t(x)=F_{t-1}(x)+\eta h_t(x)$。这里 $F_t$ 是前 t 轮的总预测，$h_t$ 是本轮新树，x 是输入，学习率 $\eta$ 缩小每棵树的贡献，通常需要更多轮才能达到类似训练误差，但轮数翻倍并不等于学习率减半的完全等价模型，因为后续树的拟合目标已经变化。树深会影响一次能表达的交互和局部细节。[GradientBoostingRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingRegressor.html) 明确说明了学习率与树数的取舍。

例如浅树拟合后训练和验证误差都高，可以考虑增加容量；如果训练误差持续下降、验证误差已上升，就该限制深度、叶节点样本数或早停，而不是继续加树。实践中固定可靠的验证切分，比较若干学习率与深度组合，让早停选择有效轮数，再核算模型大小与推理时延。

## 追问

**学习率越小越好吗？**
不一定。太小可能在训练预算内欠拟合；需要更多树也会增加模型和推理成本。

**早停看到哪条曲线？**
看独立验证指标，不能只看训练误差。若据验证集选择了轮数，最终效果仍用未参与选择的测试集评估。

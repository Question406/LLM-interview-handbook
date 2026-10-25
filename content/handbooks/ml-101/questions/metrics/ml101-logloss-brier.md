---
id: ml101-logloss-brier
section: metrics
order: 7
level: A
title: "Log loss 和 Brier score 分别惩罚什么？"
quick: "Log loss 惩罚给真实类别分配过低概率，对自信但错误的预测尤其敏感；Brier score 是概率与真实标签的平方差，惩罚有界。两者都评估概率质量，不能仅凭分类准确率代替，也不能把分数下降直接解释成校准一定变好。"
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: log_loss"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.log_loss.html
    type: primary
  - title: "scikit-learn: brier_score_loss"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html
    type: primary
---

两者都检查预测概率是否可靠，但惩罚形状不同：log loss 对真实类别概率接近零的错误惩罚很重；Brier score 用平方差，二分类常用口径下每条损失最多为 1。对应实现分别见 [scikit-learn: log_loss](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.log_loss.html) 和 [scikit-learn: brier_score_loss](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html)。

设真实标签 $y\in\{0,1\}$，模型给正类的概率为 $p$。二分类的单样本损失是：

$$
L_{\log}=-y\log p-(1-y)\log(1-p),\qquad L_{\mathrm{Brier}}=(p-y)^2.
$$

例如真实是正类，模型却只给 0.01，log loss 约为 4.605，Brier 为 0.9801；给 0.1 时分别约为 2.303 和 0.81。两次都按 0.5 阈值判错，但前一次更自信地错了，因此概率损失能揭示 accuracy 看不到的差别。上面 log 使用自然对数。

Log loss 与 Brier 都是严格适当的概率评分规则：在理想期望下，如实预测真实条件概率最优。有限数据上的分数还受到区分能力和样本不确定性的影响，所以我会同时看概率校准曲线、类别切片和业务决策阈值，避免把它们当作只测校准的仪表。

## 追问

**真实类别概率为零，log loss 会怎样？**
理论损失趋于无穷。库通常按浮点精度裁剪概率以便计算，仍应检查是否存在自信错误或数值下溢，不能只靠裁剪掩盖问题。

**多分类 Brier 的范围还是 0 到 1 吗？**
要看约定。对所有类别的独热标签平方差求和，常见范围是 0 到 2；二分类常除以 2，得到 0 到 1。比较结果必须注明是否缩放。

**准确率相同，log loss 更低的模型一定更适合业务吗？**
不一定。还要把概率转成动作，检查错误成本、阈值、流量分布和推理开销；概率分数是评估输入，业务收益还需要单独验证。

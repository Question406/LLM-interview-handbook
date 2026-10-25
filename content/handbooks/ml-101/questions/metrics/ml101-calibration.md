---
id: ml101-calibration
section: metrics
order: 5
level: S
title: "概率校准是什么？AUC 高还需要校准吗？"
quick: "校准要求预测为某个概率的一批样本，实际正类比例也接近这个概率。AUC 衡量排序，无法保证 0.8 真的对应约 80% 的发生率；要做风险估计或成本决策时，可以用独立数据校准，并同时检查可靠性曲线和概率损失。"
tags:
  - Machine Learning
  - metrics
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Probability calibration"
    url: https://scikit-learn.org/stable/modules/calibration.html
    type: primary
---

概率校准让分数具有可信的发生率含义。若模型给一百个样本都报 0.8，而只有五十个是真的正类，这一段概率就明显偏高。校准与排序是两种不同要求；把全部分数做严格递增变换会保持排序，却可能改变概率与实际频率的对应关系。

我会把独立验证数据按预测概率分组，比较每组平均预测值和实际正类比例，同时看组内样本量。偏差稳定时，可以用 sigmoid 映射或保序回归调整输出；保序回归允许更灵活的单调函数，数据少时也更容易过拟合。

拟合校准器的数据不能直接采用模型拟合过的样本预测，否则原模型的过拟合会传给校准器。可以保留单独的校准集，或用交叉验证产生折外预测。评估时同时报告概率损失、可靠性图和排序指标，因为 Brier 或 log loss 也受区分能力影响，单个损失变好不等于校准一定变好。

## 面试追问

**做了单调校准，AUC 一定不变吗？**
严格递增映射会保留排序。保序回归产生平坦区间，会引入同分，AUC 可能略有变化；交叉验证集成也可能改变最终排序。

**校准后所有子人群都可靠吗？**
不保证。总体校准可能掩盖小群体的偏差，重要群体应单独检查，并在样本稀少时报告不确定性。

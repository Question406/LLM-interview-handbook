---
id: ml101-calibration
section: metrics
order: 5
level: S
title: probability calibration 是什么？AUC 高还需要 calibration 吗？
quick: >-
  假设模型给 100 个样本都预测 80% 的正类概率，但实际只有 50 个是正类，这一段预测就偏高了。Calibration
  要让预测概率与相近样本的实际发生率对应。
tags:
  - Machine Learning
  - metrics
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 'scikit-learn: Probability calibration'
    url: 'https://scikit-learn.org/stable/modules/calibration.html'
    type: primary
---

## 回答思路

> **问题与场景：** 假设模型给 100 个样本都预测 80% 的正类概率，但实际只有 50 个是正类，这一段预测就偏高了。
>
> **做法与原因：** AUC 高也可能需要 calibration。
>
> **检查与取舍：** 我会在独立数据上按预测概率分组，比较平均预测值和实际正类比例，再决定是否拟合一个 calibration mapping。

## 可以这样回答

假设模型给 100 个样本都预测 80% 的正类概率，但实际只有 50 个是正类，这一段预测就偏高了。Calibration 要让预测概率与相近样本的实际发生率对应。

AUC 高也可能需要 calibration。AUC 主要关心排序是否正确；把分数整体放大，排序可以不变，概率却可能变得过度自信。

我会在独立数据上按预测概率分组，比较平均预测值和实际正类比例，再决定是否拟合一个 calibration mapping。拟合和最终评估的数据需要隔离，同时检查样本量与任务差异，不能仅凭一张好看的曲线判断。

## 技术备查

probability calibration 让分数具有可信的发生率含义。若模型给一百个样本都报 0.8，而只有五十个是真的正类，这一段概率就明显偏高。calibration 与排序是两种不同要求；把全部分数做严格递增变换会保持排序，却可能改变概率与实际频率的对应关系。

我会把独立验证数据按预测概率分组，比较每组平均预测值和实际正类比例，同时看组内样本量。偏差稳定时，可以用 sigmoid 映射或保序回归调整输出；保序回归允许更灵活的单调函数，数据少时也更容易 overfitting。

拟合 calibration 器的数据不能直接采用模型拟合过的样本预测，否则原模型的 overfitting 会传给 calibration 器。可以保留单独的 calibration 集，或用交叉验证产生折外预测。评估时同时报告概率损失、可靠性图和排序指标，因为 Brier 或 log loss 也受区分能力影响，单个损失变好不等于 calibration 一定变好。

## 面试追问

**做了单调 calibration，AUC 一定不变吗？**
严格递增映射会保留排序。保序回归产生平坦区间，会引入同分，AUC 可能略有变化；交叉验证集成也可能改变最终排序。

**calibration 后所有子人群都可靠吗？**
不保证。总体 calibration 可能掩盖小群体的偏差，重要群体应单独检查，并在样本稀少时报告不确定性。

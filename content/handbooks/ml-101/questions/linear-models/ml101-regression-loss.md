---
id: ml101-regression-loss
section: linear-models
order: 2
level: S
title: "MSE、MAE、RMSE 和 R 方有什么区别？"
quick: "MSE 对残差平方再平均，会更重地惩罚大错误；MAE 对绝对误差平均，较少受极端残差影响；RMSE 是 MSE 的平方根，单位与目标一致。R 方把误差与常数均值基线比较，测试集上可以为负。"
tags:
  - Machine Learning
  - linear-models
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Google ML Crash Course: Linear regression loss"
    url: https://developers.google.com/machine-learning/crash-course/linear-regression/loss
    type: primary
  - title: "scikit-learn: Metrics and scoring"
    url: https://scikit-learn.org/stable/modules/model_evaluation.html
    type: primary
---

选回归指标时，我会先问大错误是否应该得到特别重的惩罚。若预测偏十元比偏一元严重得多，MSE 比 MAE 更强调这种差别；想用目标原单位交流，就报告 RMSE 或 MAE。

例如两次残差分别是 1 和 3，MAE 为 2，MSE 为 5，RMSE 为 $\sqrt5\approx2.24$。如果把 3 换成 30，平方损失会被这个大残差明显主导。异常记录先核实含义，不能因为某指标敏感就直接删掉。

R 方使用下面的比较：

$$R^2=1-\frac{\sum_i(y_i-\hat y_i)^2}{\sum_i(y_i-\bar y)^2}.$$

$\bar y$ 是该评估样本的目标均值。预测比总报均值还差时，R 方就会小于零；它也不能直接当成因果解释比例。真实目标恒定时分母为零，需要声明工具如何处理。

## 面试追问

**训练 MAE 和训练 MSE 会学到同一个预测吗？**
不一定。在不受模型形式限制时，平方损失的条件最优预测是条件均值，绝对损失对应条件中位数。偏斜分布下两者可能不同。

**跨不同目标单位比较 RMSE 合理吗？**
直接比较通常不合理。元和万元的数字尺度不同，要在相同任务和单位上比较，或明确 normalization 方式与业务含义。

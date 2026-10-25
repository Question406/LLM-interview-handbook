---
id: ml101-precision-recall
section: metrics
order: 1
level: S
title: "准确率、精确率、召回率和 F1 怎么选？"
quick: "准确率看全部样本中预测正确的比例；精确率看判为正类的样本里有多少是真的；召回率看真实正类找回了多少。F1 是精确率与召回率的调和平均。选择时先看误报、漏报成本和类别比例，再明确阈值与评价人群。"
tags:
  - Machine Learning
  - metrics
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Google ML Crash Course: Accuracy, recall, precision"
    url: https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall
    type: primary
---

我会根据错误的代价选指标。误报很贵时重视精确率，漏报很贵时重视召回率，两者都需要兼顾时可以参考 F1，但还要分别报告两项。

假设有 100 条待审消息，其中 10 条确实违规。模型拦下 20 条，8 条真的违规，那么精确率是 $8/20=40\%$，召回率是 $8/10=80\%$。另外 78 条正常消息被正确放行，所以准确率是 $(8+78)/100=86\%$。全放行也有 90% 准确率，却一条违规都找不到。

一般用 $TP$ 表示命中的正类、$FP$ 表示误报、$FN$ 表示漏报。精确率 $P=TP/(TP+FP)$，召回率 $R=TP/(TP+FN)$，$F_1=2PR/(P+R)$。F1 不使用真负例数量，也没有直接编码具体业务成本，适用性要结合任务判断。

## 面试追问

**提高阈值，精确率一定提高吗？**
有限样本中不保证每一步都提高。提高阈值通常会减少预测正类、降低召回，精确率取决于被移除样本的真假比例；应直接查看验证曲线。

**没有预测正类时精确率怎么算？**
此时分母为零，指标未定义。报告工具的约定和预测数量，避免把设置为零或忽略的默认处理误解成实际效果。

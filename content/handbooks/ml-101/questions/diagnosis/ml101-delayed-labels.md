---
id: "ml101-delayed-labels"
section: "diagnosis"
order: 9
level: "A"
title: "标签延迟到达时怎么监测模型效果？"
quick: "标签延迟时，把即时管道预警与成熟标签上的真实效果分开监测。按预测发生时间建 cohort，等同样观察窗口后比较，并记录尚未成熟的比例；刚发生但尚未转化的样本不能直接当最终负例。"
tags: ["ML101", "diagnosis"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "Modeling Delayed Feedback in Display Advertising"
    url: https://wnzhang.net/share/rtb-papers/delayed-feedback.pdf
    type: primary
  - title: "Google ML Crash Course: Monitoring pipelines"
    url: https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring
    type: primary
---

标签尚未成熟时，不能把“暂时没看到结果”直接当成负例。转化预测里，用户可能几天后才购买；如果把刚曝光的未购买都记为负，最近一批样本的转化率会被系统性低估。 [Modeling Delayed Feedback in Display Advertising](https://wnzhang.net/share/rtb-papers/delayed-feedback.pdf)

监控可以分成两层：即时检查缺失率、特征分布、预测分数和服务异常；标签成熟后再计算准确率、校准或收益等真实指标。前者帮助提早发现问题，不能替代效果评价。 [Google ML Crash Course: Monitoring pipelines](https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring)

例如目标定义为七天内购买，就按曝光日期建 cohort（同批时间样本），等完整七天且标签管道到齐后比较。最新 cohort 标记为未成熟，保留预测时间、标签事件时间和入库时间，标签补到后更新统计；若要提前估计，用延迟模型校正并另行标明假设。

## 追问

**只看已经返回标签的样本行吗？**
可能有选择偏差。快速出现结果的人群未必代表全体，需要检查标签到达机制。

**等待窗口越长越好吗？**
更长可能覆盖更多结果，也会增加反馈滞后。先定义业务标签窗口，再按实际延迟分布设计统计时点。

**效果跌了，怎么排除只是标签管道变慢？**
同时看标签到达率和延迟分布，按相同成熟度重算 cohort；管道延迟应与模型退化分开报警。

---
id: dt-data-cascade
kind: concept
situation: 上游错误可能直到训练后才暴露。
task: 找出错误何时进入并被放大。
approach: 记录各阶段版本与拒收原因，沿链路回溯。
result: 复跑能定位同批问题并阻止再次进入训练。
---

## 可以这样回答

上游错误可能直到训练后才暴露。

因为训练 loss 看不出来：上游数据错了，模型只是更好地拟合了错误数据，loss 照样往下走。抽取错误、阈值不合适、teacher 版本变化、evaluation contamination 会沿处理流程一步步放大，最后才在下游任务里暴露，这就是 Data Cascade。每一步都留下处理原因和版本，出事时才能回溯。

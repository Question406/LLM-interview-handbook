---
id: dt-simpson-release-metrics
kind: design
situation: 流量构成变化能掩盖各组退化。
task: 拆开组内变化和混合权重变化。
approach: 固定权重重算，检查同任务配对结果。
result: 同时报告总体和 evaluation slices，不能由总分决定发布。
---

## 可以这样回答

流量构成变化能掩盖各组退化。

先固定任务分布，再比较桶内成功率。流量结构变化可能抬高总分，即使每个桶都变差；报告同一权重下的新旧结果，并将模型变化与产品路由变化分开评估。

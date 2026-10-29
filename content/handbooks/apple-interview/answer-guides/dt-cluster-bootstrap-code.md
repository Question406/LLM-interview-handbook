---
id: dt-cluster-bootstrap-code
kind: coding
situation: 模板多的任务家族会支配逐条统计。
task: 估计按家族等权的配对差异。
approach: 整个 cluster resampling 并保留两版本配对。
result: 固定 seed，手算家族均值，报告不确定性。
---

## 可以这样回答

模板多的任务家族会支配逐条统计。

先计算同一任务上新旧模型的差，再在家族内取均值、对家族等权。bootstrap 时 resampling 家族而非单行，以保持组内相关结构；这种指标评价的是家族平均收益，不是流量平均收益。

测试还要满足这个条件：固定 seed，手算家族均值，报告不确定性。

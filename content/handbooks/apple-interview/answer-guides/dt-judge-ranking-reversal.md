---
id: dt-judge-ranking-reversal
kind: concept
situation: 自动胜率与 human evaluation 结论反向。
task: 先确认测量标准是否一致。
approach: 冻结候选、顺序和协议，审计分歧样本。
result: 修测量后再比较策略，避免追逐错误 judge。
---

## 可以这样回答

自动胜率与 human evaluation 结论反向。

先对同一输出做盲评、交换位置和长度分层，确认自动评价是否偏向风格或来源。冻结 calibration 集与训练用途，再决定修 judge、改偏好采集还是训练策略，避免用同一 judge 造标签又证明收益。

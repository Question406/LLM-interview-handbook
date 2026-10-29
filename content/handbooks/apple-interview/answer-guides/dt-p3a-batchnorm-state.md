---
id: dt-p3a-batchnorm-state
kind: coding
situation: 训练用当前批，推断用运行状态。
task: 实现仿射参数和统计更新。
approach: 分开处理训练方差与 running variance。
result: 对照训练/推断结果，检查状态不被误当参数。
---

## 可以这样回答

训练用当前批，推断用运行状态。

BatchNorm 按特征聚合 batch 统计量；训练输出使用当前批的有偏方差，同时更新运行统计，推断只读运行均值方差。gamma/beta 是可学习仿射参数，running statistics 是状态，不能混为一谈。

测试时，我会对照训练/推断结果，检查状态不被误当参数。

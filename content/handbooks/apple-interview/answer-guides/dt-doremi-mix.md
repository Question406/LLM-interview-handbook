---
id: dt-doremi-mix
kind: concept
situation: 代理模型的最坏域目标不等于产品质量。
task: 评估学到的 data mix 能否迁移。
approach: 先审计域划分，再在 large model 和 task slices 验证。
result: 实际收益成立才采用，不把代理最优当普适最优。
---

## 可以这样回答

代理模型的最坏域目标不等于产品质量。

不能直接用，拿来当 core pre-training data mix 的初值比较合适。DoReMi 优化的是相对 reference model 的最坏域损失，目标里没有摘要 human evaluation 或工具成功率，所以还要在 large model 和下游 evaluation slices 上验证。另外要先清理并合理划分数据域，否则最差域是垃圾时它会被一直加权。

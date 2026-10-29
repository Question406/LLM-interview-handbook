---
id: dt-stale-rollout-incident
kind: design
situation: throughput 增加可能让训练用到过期策略 trajectories。
task: 区分 throughput 收益与有效学习质量。
approach: 记录策略版本、排队延迟及奖励环境一致性。
result: 新策略独立成功率与成本共同支持系统变化。
---

## 可以这样回答

throughput 增加可能让训练用到过期策略 trajectories。

检查 rollout 的行为策略版本、奖励版本和环境状态，再按陈旧程度 evaluation slices 比较。异步提升 throughput 会改变样本分布，重要性修正也不能修复未知行为概率或奖励协议漂移。

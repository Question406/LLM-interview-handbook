---
id: dt-curriculum-moving-target
kind: design
situation: 同一批难题会随策略进步变简单。
task: 持续提供有学习信号的任务。
approach: 按 current policy 重估难度并保留覆盖配额。
result: 新 hard examples 可学、旧能力稳定且不反复适配 holdout。
---

## 可以这样回答

同一批难题会随策略进步变简单。

按当前 student 的表现估计任务难度，追踪任务家族覆盖与迁移收益，而不是一直按 teacher 分数排序。课程更新要与最终评测隔离，保留固定 regression tasks 和旧能力回归检查。

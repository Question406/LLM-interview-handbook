---
id: afm-case-endtoend
kind: guide
situation: 截图到日历需要视觉证据和状态安全。
task: 串起生成、训练、评测与反馈。
approach: 任务真值与 executor 独立，每轮只改确认的缺口。
result: 新模板成功、无重复写入并符合 privacy requirements。
---

## 可以这样回答

截图到日历需要视觉证据和状态安全。

用同一个任务贯穿视觉证据、字段抽取、工具执行、恢复 trajectories、偏好选择和隐私反馈。每轮只针对确认的缺口改数据，并用独立任务和副作用指标验收。

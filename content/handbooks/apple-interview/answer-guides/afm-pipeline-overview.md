---
id: afm-pipeline-overview
kind: design
situation: 不同任务需要不同的可验证反馈。
task: 选一条能讲清数据到改进的 pipeline。
approach: skill、code 和视觉操作分别确定真值与训练视图。
result: 独立任务收益成立，示例不冒充已采集数据。
---

## 可以这样回答

不同任务需要不同的可验证反馈。

把三条 pipeline 分别落到技能选择与适配、代码 verifier、截图驱动工具操作。每条都有任务、数据契约、data quality checks、训练视图、独立评价和反馈迭代；已公开方法和建议扩展分别说明。

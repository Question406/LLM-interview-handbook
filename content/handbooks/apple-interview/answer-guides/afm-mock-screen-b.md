---
id: afm-mock-screen-b
kind: guide
situation: preference labels 和偏差审计需要同时讲清。
task: 跑通 RM 并解释分数何时可信。
approach: 共享 scorer 训练，固定候选查长度和位置。
result: calibration、选择质量与训练隔离均检查。
---

## 可以这样回答

preference labels 和偏差审计需要同时讲清。

先确认偏好、tie 和 confidence weight 的含义，再训练 RM，最后检查长度、位置与 source bias。模型跑通后仍要用独立执行结果判断选择质量。

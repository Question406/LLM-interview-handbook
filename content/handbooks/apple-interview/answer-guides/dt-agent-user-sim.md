---
id: dt-agent-user-sim
kind: design
situation: 模拟用户可能 leakage 目标或过度配合。
task: 获得可信的多轮交互训练。
approach: 约束用户可见信息与状态，独立核对终局。
result: 真实或人工抽查支持，换模拟器仍有效。
---

## 可以这样回答

模拟用户可能 leakage 目标或过度配合。

模拟器只负责生成用户的话，看不到隐藏数据库和完整的内部政策；成功由真实环境状态和政策 grader 判，模拟器说满意不能当 oracle。要查过度配合、泄密、文风单一和停不下来这几类问题，评测时换 seed 或 teacher 并人工抽查，免得 agent 只学会适应模拟用户。

---
id: apple-foundation-models
kind: design
situation: on-device 与 server-side 承担不同约束与任务。
task: 准确解释公开模型定位。
approach: 用公开报告连接能力、成本与 privacy requirements。
result: 不推测内部细节，任务路由有证据。
---

## 可以这样回答

on-device 与 server-side 承担不同约束与任务。

Apple 的公开方案是 on-device 与 PCC 上的 server 模型互补：约 3B 的 on-device 模型处理日常、低延迟和私有上下文任务，更难的推理交给 server-side。on-device 擅长摘要、抽取和短对话，设计时要按能力与隐私要求决定路由，并保留拒答或非生成 UI。

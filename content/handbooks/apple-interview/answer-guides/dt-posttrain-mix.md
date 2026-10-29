---
id: dt-posttrain-mix
kind: design
situation: 一种 post-training 数据可能挤掉其他行为。
task: 平衡新技能和通用能力。
approach: 固定预算做 data mix ablation study，保留 regression tasks。
result: 逐任务回归和成本决定 mix，而非统一比例。
---

## 可以这样回答

一种 post-training 数据可能挤掉其他行为。

四类数据分别设 token 配额和 loss 范围再混，可验证任务用 rule-based reward，主观偏好用 human evaluation 或 RM，奖励尺度不同的任务不放进同一个 GRPO 分组，工具返回不计入损失。每加一类数据都回看其余能力，防止代码伤拒答、工具 JSON 伤自然语言。

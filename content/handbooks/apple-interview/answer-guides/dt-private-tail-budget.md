---
id: dt-private-tail-budget
kind: design
situation: 聚合信号可能看不到稀有但重要的失败。
task: 在 privacy requirements 内补 long-tail 监督。
approach: 从合法类别信号出发，用许可研究和合成复现。
result: 独立 long-tail 测试改善，不恢复用户原文。
---

## 可以这样回答

聚合信号可能看不到稀有但重要的失败。

聚合趋势适合发现常见需求，未观察到稀有模式不代表它不存在。long-tail 能力应结合公开或获授权的 seed、专家设计和受控合成，用独立验证确认；不能为追求覆盖绕开隐私阈值。

---
id: apple-diff-privacy
kind: design
situation: 数据不出设备不自动意味着有 DP 保证。
task: 说清保护对象与 privacy budget。
approach: 定义邻居关系、裁剪、加噪和组合。
result: 报告效用与预算，不将匿名化当形式保证。
---

## 可以这样回答

数据不出设备不自动意味着有 DP 保证。

数据不出设备说明这条路径没有发布数据，本身没有一个可报的 $\varepsilon$。DP 约束的是发布结果对单条记录的敏感度；个性化上下文优先留在 on-device，只有发布人群统计时再讨论噪声、每日条数和合成预算。

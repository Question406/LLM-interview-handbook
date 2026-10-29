---
id: dt-senior-proxy-scale-reversal
kind: project
situation: small model 选出的 mix 可能在 large model 失效。
task: 判断规模迁移是否成立。
approach: 控制训练预算与数据，少量 large model 对照验证。
result: 按真实 large model 收益重新分配预算。
---

## 可以这样回答

small model 选出的 mix 可能在 large model 失效。

small model 实验是筛选证据，不保证排序跨规模保持。检查训练阶段、token 预算、容量与目标任务差异，在少量代表配方上做跨规模验证，再决定继续调数据还是修代理实验设计。

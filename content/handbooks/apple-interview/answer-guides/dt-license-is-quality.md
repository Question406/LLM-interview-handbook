---
id: dt-license-is-quality
kind: concept
situation: 有能力价值的数据也可能不可用于训练。
task: 把许可和撤回当作数据可用性条件。
approach: 摄入前检查用途，保存精确来源依赖。
result: 不合格来源无法进入 mix，撤回可追踪。
---

## 可以这样回答

有能力价值的数据也可能不可用于训练。

因为能不能合法用于训练，本身就是质量条件。许可不合格、opt-out 执行不了、或者带着不该用的 personally identifiable information (PII)，评测分再高也可能被迫撤回重训。所以要把这些约束放进数据选择流程，追踪来源、拒绝记录、teacher 和合成 seed。

---
id: dt-eval-harness
kind: concept
situation: 版本不固定时小幅涨分难以解释。
task: 建设可复现可回归的评价流程。
approach: 保存逐题结果、模型提示 decoding 与 grader 版本。
result: 配对证据和稳定复跑支持结论。
---

## 可以这样回答

版本不固定时小幅涨分难以解释。

核心是每个分数都能复现、能公平比较：每次评测记下模型、题集、提示模板、decoding 参数和 seed，scorer 版本也固定。小幅涨分要做逐题 paired test。日常跑快速检查、夜间跑全套，保存逐题结果来定位回归。

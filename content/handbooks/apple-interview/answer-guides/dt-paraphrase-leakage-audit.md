---
id: dt-paraphrase-leakage-audit
kind: design
situation: 翻译和改写会绕过字面 contamination scan。
task: 确认记忆 leakage 及其来源。
approach: 语义 nearest neighbors、teacher 提示和跨语言家族一起审计。
result: 未见家族复测，绿色 n-gram 报告不当无 contamination 证明。
---

## 可以这样回答

翻译和改写会绕过字面 contamination scan。

字面重叠只能排查部分 leakage。沿 seed、翻译和改写的来源链追踪任务家族，再结合语义候选检索与人工核对；能力相似不等于 contamination，不能把所有同题型数据一律删除。

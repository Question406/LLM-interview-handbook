---
id: dt-tokenizer-migration-gap
kind: concept
situation: tokenizer 改变后 loss 单位也变了。
task: 判断是真能力退化还是指标不可比。
approach: 比较原始文本覆盖、长度预算与独立任务。
result: 不跨 tokenizer 直接比 loss，报告语言和长度 evaluation slices。
---

## 可以这样回答

tokenizer 改变后 loss 单位也变了。

不同 tokenizer 的每 token loss 不可直接比较。先用相同原始文本与统一 normalization 对照，再检查切分膨胀、特殊 token、截断与监督对齐，避免把 data pipeline 错误误判为模型退化。

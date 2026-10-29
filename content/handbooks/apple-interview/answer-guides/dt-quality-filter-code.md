---
id: dt-quality-filter-code
kind: coding
situation: 统一过滤阈值可能误删 low-resource 语言。
task: 实现可解释的多级质量筛选。
approach: 先便宜规则后模型打分，按语言做 calibration。
result: 抽查 false rejection 并比较各组通过率和下游收益。
---

## 可以这样回答

统一过滤阈值可能误删 low-resource 语言。

过滤分三步：先做便宜的语言、长度、PII 和重复字符检查，再用按语言做 calibration 的质量模型打分，最后按阈值和配额选。全局取 top-$k$ 容易把 low-resource 语言整个丢掉。AFM 2025 公开的经验是过强的启发式会误删有价值的数据，所以要查 false rejection，并按语言分别对 threshold 做 calibration。

测试还要满足这个条件：抽查 false rejection 并比较各组通过率和下游收益。

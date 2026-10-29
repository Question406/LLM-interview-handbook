---
id: dt-global-dedup
kind: concept
situation: 跨快照重复内容也可能是高价值来源。
task: 确定 deduplication 范围与保留策略。
approach: 比较快照内和全局方案，检查质量构成变化。
result: 同预算下游收益决定范围，不追最低重复率。
---

## 可以这样回答

跨快照重复内容也可能是高价值来源。

因为跨快照反复出现的往往是优质网页，全局 near-duplicate deduplication 把它们只留一份，一次性出现的低质页面比例就上去了。网页先在快照内去 near-duplicates，跨快照重点处理页脚、导航和评测指纹，范围用 small model 的下游对照来定。

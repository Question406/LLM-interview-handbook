---
id: dt-worse-after-data
kind: design
situation: 新数据加入后目标任务退步。
task: 区分来源质量、data mix 和训练条件问题。
approach: 先复现，再按来源与失败类型做 ablation study。
result: 撤回或修复该因素后独立 evaluation slices 恢复。
---

## 可以这样回答

新数据加入后目标任务退步。

先复现只换数据的对照，排除步数、decoding 和奖励的变化；确认是数据造成的，再按 evaluation slices、新旧题、抽查、data mix、learnability 的顺序查 negative transfer、标签错误、data mix 失控、过难样本和 evaluation leakage。旧题分数下降、新题分数不变，也可能是原先由 contamination 带来的分数优势消失了。按查到的证据调整对应的数据，全部回滚会把有用的部分一起丢掉。

---
id: dt-hash-split-code
kind: coding
situation: 重跑和新增数据不能改变已有 split。
task: 按稳定单位隔离训练与评价。
approach: 对实体或重复 cluster 的规范键做哈希分桶。
result: 同组不跨 split，新增记录不移动旧样本。
---

## 可以这样回答

重跑和新增数据不能改变已有 split。

对稳定的 group_id 做哈希再取模，让同一仓库、书、线程或 near-duplicates cluster 整组落在训练或评测的同一侧。随机 shuffle 会把同一篇转载拆到两边，让记忆看起来像泛化。seed 和规范化版本要记录，重跑才稳定；时间 leakage 和生成 prompt 里混入评测题，哈希解决不了，要单独查。

测试还要满足这个条件：同组不跨 split，新增记录不移动旧样本。

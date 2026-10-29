---
id: dt-data-replay-incident
kind: concept
situation: 重试后重复样本可能进入训练。
task: 先恢复数据正确性再修重试机制。
approach: 冻结受影响版本，按稳定样本 ID 对账和 idempotent write 入。
result: 重跑不再增量翻倍，修复后下游版本可追溯。
---

## 可以这样回答

重试后重复样本可能进入训练。

把原始样本身份、变换版本与运行尝试分开，写入不可变分片并用完整 manifest 原子发布。恢复时检查训练已消费的数据版本和位置；deduplication 必须明确区分重复交付与有意的 data augmentation。

---
id: dt-ngram-contam-code
kind: coding
situation: 训练 corpus 可能包含冻结评测题面。
task: 标出达到命中阈值的训练文档。
approach: 评测建倒排索引，训练侧逐 gram 查询。
result: 手算重叠计数，隔离训练文档并保留评测。
---

## 可以这样回答

训练 corpus 可能包含冻结评测题面。

把评测题面切成 13-gram 建倒排索引，训练文档逐个 gram 查表，命中数过阈值的训练文档进 quarantine，评测题留着不删。改写数字或翻译会让 n-gram false negative，所以还要配合 URL 检查和 embedding nearest neighbors，见 `dt-contamination`。

测试时，我会手算重叠计数，隔离训练文档并保留评测。

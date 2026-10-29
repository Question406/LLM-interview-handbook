---
id: dt-bench-vs-user
kind: concept
situation: 公开榜涨分却不改善实际工作。
task: 找到 benchmark 与产品失败的断点。
approach: 依次查 contamination、judge、题目质量和分布。
result: 真实任务复测改善才接受数据干预。
---

## 可以这样回答

公开榜涨分却不改善实际工作。

先诊断断在哪，再动数据。我会按顺序查四层：training set 有没有 leakage 评测题，scorer 是不是偏爱某种文风，基准题和测试本身有没有错，榜单任务和用户的实际工作差多远。没找到原因就加数据，很可能只是把榜单继续往上推。

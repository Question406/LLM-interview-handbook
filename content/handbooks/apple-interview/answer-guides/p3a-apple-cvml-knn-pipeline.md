---
id: p3a-apple-cvml-knn-pipeline
kind: coding
situation: 预处理和选邻居都可能 leakage 验证信息。
task: 构建只拟合 training set 的 kNN 流程。
approach: 训练统计应用到查询，距离和投票平票明确。
result: 测试零方差、平票和验证输入不影响拟合。
---

## 可以这样回答

预处理和选邻居都可能 leakage 验证信息。

只用 training set 拟合均值与标准差，再对查询应用同一变换，按距离稳定选邻居并投票。距离平票、投票平票和零方差都要提前定义；把 validation set 一起拟合预处理会 leakage 分布，调 k 也只能用 development set。

测试还要满足这个条件：测试零方差、平票和验证输入不影响拟合。

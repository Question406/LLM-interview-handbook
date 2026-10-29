---
id: dt-p3a-tabular-full-pipeline
kind: coding
situation: 面试要求从原始表格跑到可解释结果。
task: 完成预处理、训练、指标和投影。
approach: 先划分再拟合，简单 baseline 用于暴露数据问题。
result: 改变 test set 不影响模型，检查缺失值和类别指标。
---

## 可以这样回答

面试要求从原始表格跑到可解释结果。

先冻结 train/test split，只在 training set 拟合缺失值填补、standardization、模型和降维投影；test set 只做 transform 与最终指标计算。先跑通简单 baseline，再解释降维图和误差，不用复杂网络掩盖 data leakage。

测试还要满足这个条件：改变 test set 不影响模型，检查缺失值和类别指标。

---
id: dt-p3a-kfold-indices
kind: coding
situation: 折分不均或先预处理会 contamination 交叉验证。
task: 让每个样本恰好验证一次。
approach: 一次打乱分配余数，每折重新拟合流程。
result: 检查折间覆盖、互斥与固定 seed 复现。
---

## 可以这样回答

折分不均或先预处理会 contamination 交叉验证。

先生成一次可复现排列，把余数分给前几折；每个样本恰好一次进入 validation set，训练索引为该折的补集。执行模型比较时，每折重新拟合预处理与模型，不能在全数据上先 standardization 再交叉验证。

测试时，我会检查折间覆盖、互斥与固定 seed 复现。

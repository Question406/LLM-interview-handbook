---
id: dt-token-budget-batch-code
kind: coding
situation: padding 开销取决于批中最大长度。
task: 按真实计算预算组 batch。
approach: 加入样本前计算新最大长度乘批大小。
result: 检查最后一批、超长单例和顺序守恒。
---

## 可以这样回答

padding 开销取决于批中最大长度。

预算按 batch 内最大长度乘样本数计算，不能只累加真实长度。顺序扫描，加入下一条会超预算时先交付当前 batch；单条超长样本单独记录为拒收，其他样本不丢失、不重排。

测试时，我会检查最后一批、超长单例和顺序守恒。
